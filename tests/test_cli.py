from pathlib import Path

from cuga_harness_kit.cli import init


def test_init_skips_differing_files_without_force(tmp_path: Path):
    dest = tmp_path / ".claude" / "skills" / "getting-started" / "SKILL.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("hand-edited content")

    init(["claude"], force=False, dry_run=False, cwd=tmp_path)

    assert dest.read_text() == "hand-edited content"


def test_update_overwrites_differing_files(tmp_path: Path):
    dest = tmp_path / ".claude" / "skills" / "getting-started" / "SKILL.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("stale content from an older cuga-harness-kit version")

    init(["claude"], force=True, dry_run=False, cwd=tmp_path)

    assert "cuga-getting-started" in dest.read_text()
