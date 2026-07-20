"""`cuga-harness-kit init` — scaffold cuga skill files for Claude Code, Cursor, Codex, and Bob."""

from __future__ import annotations

import argparse
from pathlib import Path

from cuga_harness_kit.render import render_agents_section, render_mdc

SKILLS_DIR = Path(__file__).parent / "skills"
DOCS_DIR = Path(__file__).parent / "docs"
ALL_TARGETS = ("claude", "cursor", "codex", "bob")
AGENTS_START = "<!-- cuga-harness-kit:start -->"
AGENTS_END = "<!-- cuga-harness-kit:end -->"


def _skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.iterdir() if (p / "SKILL.md").is_file())


def _detect_cuga_message(cwd: Path) -> str:
    pyproject = cwd / "pyproject.toml"
    looks_like_cuga_checkout = (cwd / "src" / "cuga").is_dir() or (
        pyproject.is_file() and 'name = "cuga"' in pyproject.read_text(errors="ignore")
    )
    if looks_like_cuga_checkout:
        return "Detected an existing cuga source checkout — skills will reference your local `cuga` package."
    return "No existing cuga installation detected — skills will guide you through `uv init` and `uv add cuga` from scratch."


def _write_file(path: Path, content: str, *, force: bool, dry_run: bool, written: list[str], skipped: list[str]) -> None:
    if path.exists():
        if path.read_text() == content:
            skipped.append(f"{path} (already up to date)")
            return
        if not force:
            skipped.append(f"{path} (exists, differs — pass --force to overwrite)")
            return
    if dry_run:
        written.append(f"{path} (dry-run)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    written.append(str(path))


def _write_agents_md(cwd: Path, skill_paths: list[Path], *, dry_run: bool, written: list[str], skipped: list[str]) -> None:
    block_body = "\n".join(render_agents_section(p) for p in skill_paths)
    block = f"{AGENTS_START}\n\n{block_body}{AGENTS_END}\n"

    path = cwd / "AGENTS.md"
    if path.exists():
        existing = path.read_text()
        if AGENTS_START in existing and AGENTS_END in existing:
            pre, _, rest = existing.partition(AGENTS_START)
            _, _, post = rest.partition(AGENTS_END)
            new_content = f"{pre}{block}{post}"
        else:
            new_content = existing.rstrip("\n") + "\n\n" + block
    else:
        new_content = block

    if path.exists() and path.read_text() == new_content:
        skipped.append(f"{path} (already up to date)")
        return
    if dry_run:
        written.append(f"{path} (dry-run)")
        return
    path.write_text(new_content)
    written.append(str(path))


def init(targets: list[str], *, force: bool, dry_run: bool, cwd: Path | None = None) -> None:
    cwd = cwd or Path.cwd()
    skill_paths = _skill_dirs()
    written: list[str] = []
    skipped: list[str] = []

    print(_detect_cuga_message(cwd))

    if "claude" in targets:
        for skill_path in skill_paths:
            src = skill_path / "SKILL.md"
            dest = cwd / ".claude" / "skills" / skill_path.name / "SKILL.md"
            _write_file(dest, src.read_text(), force=force, dry_run=dry_run, written=written, skipped=skipped)

    if "cursor" in targets:
        for skill_path in skill_paths:
            src = skill_path / "SKILL.md"
            dest = cwd / ".cursor" / "rules" / f"cuga-{skill_path.name}.mdc"
            _write_file(dest, render_mdc(src), force=force, dry_run=dry_run, written=written, skipped=skipped)

    if "codex" in targets:
        _write_agents_md(cwd, [p / "SKILL.md" for p in skill_paths], dry_run=dry_run, written=written, skipped=skipped)

    if "bob" in targets:
        for skill_path in skill_paths:
            src = skill_path / "SKILL.md"
            dest = cwd / ".bob" / "skills" / skill_path.name / "SKILL.md"
            _write_file(dest, src.read_text(), force=force, dry_run=dry_run, written=written, skipped=skipped)

    env_doc = DOCS_DIR / "env-api-keys.md"
    _write_file(
        cwd / "docs" / "cuga-env-api-keys.md",
        env_doc.read_text(),
        force=force,
        dry_run=dry_run,
        written=written,
        skipped=skipped,
    )

    print(f"\n{len(written)} file(s) written, {len(skipped)} skipped.")
    for line in written:
        print(f"  wrote:    {line}")
    for line in skipped:
        print(f"  skipped:  {line}")
    print(
        '\nNext step: open this folder in Claude Code, Cursor, Codex, or Bob, and try asking '
        '"help me build a cuga tool" or "how do I launch cuga".'
    )


def _add_targets_arg(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument(
        "--targets",
        default=",".join(ALL_TARGETS),
        help=f"comma-separated subset of {ALL_TARGETS} (default: all)",
    )
    subparser.add_argument("--dry-run", action="store_true", help="print what would be written, write nothing")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="cuga-harness-kit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="scaffold cuga skill files into the current directory")
    _add_targets_arg(init_parser)
    init_parser.add_argument("--force", action="store_true", help="overwrite files that already exist and differ")

    update_parser = subparsers.add_parser(
        "update", help="re-scaffold cuga skill files after upgrading cuga-harness-kit (alias for `init --force`)"
    )
    _add_targets_arg(update_parser)

    args = parser.parse_args(argv)

    if args.command in ("init", "update"):
        targets = [t.strip() for t in args.targets.split(",") if t.strip()]
        unknown = set(targets) - set(ALL_TARGETS)
        if unknown:
            parser.error(f"unknown target(s): {', '.join(sorted(unknown))} (choose from {ALL_TARGETS})")
        force = True if args.command == "update" else args.force
        init(targets, force=force, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
