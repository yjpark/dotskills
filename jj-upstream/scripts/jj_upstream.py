#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click",
# ]
# ///
"""Generate and classify jj patches for upstream contribution."""

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class Config:
    company_name: str
    upstream_ref: str
    local_ref: str
    upstream_patches_dir: str
    company_patches_dir: str


@dataclass
class Revision:
    change_id: str
    commit_id: str
    timestamp: str
    description: str
    is_company: bool = False


@dataclass
class HunkLine:
    text: str  # full line including +/- prefix or context


@dataclass
class Hunk:
    header: str  # the @@ line
    lines: list[HunkLine] = field(default_factory=list)


@dataclass
class FileDiff:
    header: str  # the "diff --git ..." line and subsequent metadata lines
    hunks: list[Hunk] = field(default_factory=list)
    path_a: str = ""
    path_b: str = ""


def run(cmd: list[str], check: bool = True, **kwargs) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        if check:
            print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)
        return ""
    return result.stdout.strip()


def get_repo_root() -> Path:
    return Path(run(["jj", "root"]))


def load_config(repo_root: Path) -> Config:
    config_path = repo_root / ".claude" / "jj-upstream.json"
    if not config_path.exists():
        print(
            f"Config not found at {config_path}. Please create it with company_name, "
            "upstream_ref, local_ref, upstream_patches_dir, company_patches_dir.",
            file=sys.stderr,
        )
        sys.exit(1)
    data = json.loads(config_path.read_text())
    return Config(**data)


def get_short_id(ref: str) -> str:
    return run(
        ["jj", "log", "-r", ref, "--no-graph", "-T", "change_id.shortest()"]
    )


def get_revisions(config: Config) -> list[Revision]:
    revset = f"{config.upstream_ref}::{config.local_ref}"
    template = 'change_id.shortest() ++ "\\t" ++ commit_id.shortest() ++ "\\t" ++ committer.timestamp() ++ "\\t" ++ description.first_line() ++ "\\n"'
    output = run(
        ["jj", "log", "-r", revset, "--no-graph", "--reversed", "-T", template]
    )
    revisions = []
    company_lower = config.company_name.lower()
    for line in output.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 3)
        if len(parts) < 4:
            continue
        change_id, commit_id, timestamp, description = parts
        is_company = description.lower().startswith(f"{company_lower} ")  or description.lower().startswith(f"{company_lower}:")
        revisions.append(
            Revision(
                change_id=change_id.strip(),
                commit_id=commit_id.strip(),
                timestamp=timestamp.strip(),
                description=description.strip(),
                is_company=is_company,
            )
        )
    return revisions


def make_folder_name(config: Config) -> str:
    upstream_short = get_short_id(config.upstream_ref)
    local_short = get_short_id(config.local_ref)
    today = date.today().isoformat()
    return f"{today}_{upstream_short}_{local_short}"


def ensure_dirs(
    repo_root: Path, config: Config, folder_name: str
) -> tuple[Path, Path]:
    upstream_dir = repo_root / config.upstream_patches_dir / folder_name
    company_dir = repo_root / config.company_patches_dir / folder_name
    upstream_dir.mkdir(parents=True, exist_ok=True)
    company_dir.mkdir(parents=True, exist_ok=True)
    return upstream_dir, company_dir


def write_revisions_md(
    path: Path, revisions: list[tuple[int, Revision]], label: str
) -> None:
    lines = [f"# {label} Revisions\n\n"]
    lines.append("| # | Timestamp | JJ Rev | Git Rev | Description |\n")
    lines.append("|---|-----------|--------|---------|-------------|\n")
    for idx, rev in revisions:
        lines.append(
            f"| {idx} | {rev.timestamp} | {rev.change_id} | {rev.commit_id} | {rev.description} |\n"
        )
    path.write_text("".join(lines))


# --- Diff parsing and splitting ---


def parse_diff(diff_text: str) -> list[FileDiff]:
    """Parse a git-format diff into FileDiff objects."""
    files: list[FileDiff] = []
    # Split on "diff --git" boundaries
    parts = re.split(r"(?=^diff --git )", diff_text, flags=re.MULTILINE)
    for part in parts:
        part = part.strip()
        if not part.startswith("diff --git "):
            continue
        fd = FileDiff(header="")
        # Extract paths from the diff --git line
        first_line = part.split("\n", 1)[0]
        m = re.match(r"diff --git a/(.*?) b/(.*)", first_line)
        if m:
            fd.path_a = m.group(1)
            fd.path_b = m.group(2)

        # Split into header (before first @@) and hunks
        hunk_splits = re.split(r"(?=^@@)", part, flags=re.MULTILINE)
        fd.header = hunk_splits[0]
        for hunk_text in hunk_splits[1:]:
            hunk_lines = hunk_text.split("\n")
            hunk = Hunk(header=hunk_lines[0])
            for hl in hunk_lines[1:]:
                if hl or hunk.lines:  # skip trailing empty
                    hunk.lines.append(HunkLine(text=hl))
            # Remove trailing empty lines
            while hunk.lines and not hunk.lines[-1].text:
                hunk.lines.pop()
            fd.hunks.append(hunk)
        files.append(fd)
    return files


def is_company_file(file_diff: FileDiff, company_name: str) -> bool:
    """Check if the entire file belongs to company (folder or filename rules)."""
    cn_lower = company_name.lower()
    for path in [file_diff.path_a, file_diff.path_b]:
        path_lower = path.lower()
        # File under a company-named folder
        if f"{cn_lower}/" in path_lower or path_lower.startswith(f"{cn_lower}/"):
            return True
        # Filename starts with company_
        filename = path.split("/")[-1].lower()
        if filename.startswith(f"{cn_lower}_"):
            return True
    return False


def line_mentions_company(line: str, company_name: str) -> bool:
    """Check if a line mentions the company name (case-insensitive)."""
    return company_name.lower() in line.lower()


def recompute_hunk_header(
    original_header: str, lines: list[HunkLine]
) -> str:
    """Recompute the @@ header based on actual line counts."""
    m = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)", original_header)
    if not m:
        return original_header
    old_start = int(m.group(1))
    new_start = int(m.group(3))
    rest = m.group(5)
    old_count = 0
    new_count = 0
    for hl in lines:
        if hl.text.startswith("-"):
            old_count += 1
        elif hl.text.startswith("+"):
            new_count += 1
        else:
            old_count += 1
            new_count += 1
    return f"@@ -{old_start},{old_count} +{new_start},{new_count} @@{rest}"


def split_hunk(
    hunk: Hunk, company_name: str
) -> tuple[Hunk | None, Hunk | None]:
    """Split a hunk into upstream and company parts based on added lines mentioning company."""
    upstream_lines: list[HunkLine] = []
    company_lines: list[HunkLine] = []
    has_company = False
    has_upstream_adds = False

    for hl in hunk.lines:
        if hl.text.startswith("+") and not hl.text.startswith("+++"):
            if line_mentions_company(hl.text, company_name):
                has_company = True
                company_lines.append(hl)
                # Don't include in upstream
            else:
                has_upstream_adds = True
                upstream_lines.append(hl)
                # context for company too if needed
        elif hl.text.startswith("-") and not hl.text.startswith("---"):
            # Removed lines go to both
            upstream_lines.append(hl)
            company_lines.append(hl)
        else:
            # Context lines go to both
            upstream_lines.append(hl)
            company_lines.append(hl)

    upstream_hunk = None
    company_hunk = None

    # Only create upstream hunk if there are meaningful changes
    if has_upstream_adds or any(
        hl.text.startswith("-") and not hl.text.startswith("---")
        for hl in upstream_lines
    ):
        upstream_hunk = Hunk(
            header=recompute_hunk_header(hunk.header, upstream_lines),
            lines=upstream_lines,
        )

    if has_company:
        company_hunk = Hunk(
            header=recompute_hunk_header(hunk.header, company_lines),
            lines=company_lines,
        )

    return upstream_hunk, company_hunk


def reconstruct_diff(file_diff: FileDiff, hunks: list[Hunk]) -> str:
    """Reconstruct a git diff string from header and hunks."""
    if not hunks:
        return ""
    parts = [file_diff.header.rstrip()]
    for hunk in hunks:
        parts.append(hunk.header)
        for hl in hunk.lines:
            parts.append(hl.text)
    return "\n".join(parts) + "\n"


def split_file_diff(
    file_diff: FileDiff, company_name: str
) -> tuple[str, str]:
    """Split a file diff into upstream and company patches.

    Returns (upstream_patch, company_patch) as strings.
    """
    # Entire file is company
    if is_company_file(file_diff, company_name):
        full = reconstruct_diff(file_diff, file_diff.hunks)
        return "", full

    upstream_hunks: list[Hunk] = []
    company_hunks: list[Hunk] = []

    for hunk in file_diff.hunks:
        uh, ch = split_hunk(hunk, company_name)
        if uh:
            upstream_hunks.append(uh)
        if ch:
            company_hunks.append(ch)

    upstream_patch = reconstruct_diff(file_diff, upstream_hunks)
    company_patch = reconstruct_diff(file_diff, company_hunks)
    return upstream_patch, company_patch


def slugify(text: str, max_len: int = 40) -> str:
    """Convert text to a filename-safe slug."""
    import re
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if len(slug) > max_len:
        slug = slug[:max_len]
        # Trim at last hyphen to avoid cutting mid-word
        last = slug.rfind("-")
        if last > 0:
            slug = slug[:last]
    return slug


# --- CLI ---

import click


@click.group()
def cli():
    """jj-upstream: classify and export patches for upstream contribution."""
    pass


@cli.command()
def list():
    """List revisions classified as upstream or company."""
    repo_root = get_repo_root()
    config = load_config(repo_root)
    revisions = get_revisions(config)
    folder_name = make_folder_name(config)
    upstream_dir, company_dir = ensure_dirs(repo_root, config, folder_name)

    upstream_revs = [(i + 1, r) for i, r in enumerate(revisions) if not r.is_company]
    company_revs = [(i + 1, r) for i, r in enumerate(revisions) if r.is_company]

    write_revisions_md(upstream_dir / "revisions.md", upstream_revs, "Upstream")
    write_revisions_md(company_dir / "revisions.md", company_revs, "Company")

    print(f"Folder: {folder_name}")
    print(f"Total revisions: {len(revisions)}")
    print(f"Upstream: {len(upstream_revs)}, Company: {len(company_revs)}")
    print(f"Written: {upstream_dir / 'revisions.md'}")
    print(f"Written: {company_dir / 'revisions.md'}")


@cli.command()
def export():
    """Export patches, splitting company content from upstream."""
    repo_root = get_repo_root()
    config = load_config(repo_root)
    revisions = get_revisions(config)
    folder_name = make_folder_name(config)
    upstream_dir, company_dir = ensure_dirs(repo_root, config, folder_name)

    # Also write revisions.md
    upstream_revs = [(i + 1, r) for i, r in enumerate(revisions) if not r.is_company]
    company_revs = [(i + 1, r) for i, r in enumerate(revisions) if r.is_company]
    write_revisions_md(upstream_dir / "revisions.md", upstream_revs, "Upstream")
    write_revisions_md(company_dir / "revisions.md", company_revs, "Company")

    upstream_count = 0
    company_count = 0

    for idx, rev in enumerate(revisions, 1):
        diff_output = run(
            ["jj", "diff", "-r", rev.commit_id, "--git"], check=False
        )
        if not diff_output:
            continue

        slug = slugify(rev.description, max_len=40)
        patch_name = f"{idx:03d}_{rev.change_id}_{slug}.patch"

        if rev.is_company:
            # Entire revision goes to company
            (company_dir / patch_name).write_text(diff_output + "\n")
            company_count += 1
            print(f"  [{idx}] company: {patch_name} ({rev.description})")
        else:
            # Parse and split
            file_diffs = parse_diff(diff_output)
            upstream_parts: list[str] = []
            company_parts: list[str] = []

            for fd in file_diffs:
                up, cp = split_file_diff(fd, config.company_name)
                if up:
                    upstream_parts.append(up)
                if cp:
                    company_parts.append(cp)

            if upstream_parts:
                (upstream_dir / patch_name).write_text("".join(upstream_parts))
                upstream_count += 1
                print(f"  [{idx}] upstream: {patch_name} ({rev.description})")

            if company_parts:
                (company_dir / patch_name).write_text("".join(company_parts))
                company_count += 1
                print(f"  [{idx}] company (split): {patch_name}")

    print(f"\nExported {upstream_count} upstream patches, {company_count} company patches")
    print(f"Upstream: {upstream_dir}")
    print(f"Company:  {company_dir}")


if __name__ == "__main__":
    cli()
