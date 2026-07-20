"""Render a canonical Claude SKILL.md into Cursor .mdc or a Codex AGENTS.md section.

Claude and Bob both read skills as a per-skill directory + SKILL.md with
frontmatter, so those two targets use the SKILL.md file verbatim. Cursor
(single rule file + frontmatter) and Codex (one shared file, no frontmatter)
need different shapes, which are derived from the canonical SKILL.md here,
at scaffold time, so there's a single source of truth per skill.
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
