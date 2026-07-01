"""Render a canonical Claude SKILL.md into Cursor .mdc, a Codex AGENTS.md section, or a Bob rules file.

Claude, Cursor, Codex, and Bob each read assistant guidance in a different
shape (per-skill directory + frontmatter / single rule file + frontmatter /
one shared file with no frontmatter / a rules directory with no frontmatter
and no selective loading). Rather than hand-maintaining four copies of the
same content, every skill is authored once as SKILL.md and the other shapes
are derived from it here, at scaffold time.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,5})(\s)", re.MULTILINE)


def parse_skill_md(skill_md_path: Path) -> tuple[dict, str]:
    """Split a SKILL.md file into (frontmatter dict, body markdown)."""
    text = skill_md_path.read_text()
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{skill_md_path} has no YAML frontmatter")
    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).strip("\n")
    return frontmatter, body


def render_mdc(skill_md_path: Path) -> str:
    """SKILL.md -> Cursor .mdc content: same description, alwaysApply: false, body verbatim."""
    frontmatter, body = parse_skill_md(skill_md_path)
    header = yaml.safe_dump(
        {"description": frontmatter["description"], "alwaysApply": False},
        sort_keys=False,
        allow_unicode=True,
    ).strip()
    return f"---\n{header}\n---\n\n{body}\n"


def render_agents_section(skill_md_path: Path) -> str:
    """SKILL.md -> one '## <name>' section for AGENTS.md, headings demoted one level."""
    frontmatter, body = parse_skill_md(skill_md_path)
    demoted = _HEADING_RE.sub(r"#\1\2", body)
    return f"## {frontmatter['name']}\n\n_{frontmatter['description']}_\n\n{demoted}\n"


def render_bob(skill_md_path: Path) -> str:
    """SKILL.md -> a Bob rules file: plain markdown, no frontmatter (Bob doesn't support it
    or selective loading — every file under .bob/rules/ is injected into every conversation
    in full), body verbatim.
    """
    _, body = parse_skill_md(skill_md_path)
    return f"{body}\n"
