import re

import yaml

from cuga_harness_kit.cli import SKILLS_DIR, _skill_dirs
from cuga_harness_kit.render import parse_skill_md, render_agents_section, render_mdc

GETTING_STARTED = SKILLS_DIR / "getting-started" / "SKILL.md"


def test_all_skills_have_required_frontmatter():
    skill_paths = _skill_dirs()
    assert len(skill_paths) == 8
    for skill_path in skill_paths:
        frontmatter, body = parse_skill_md(skill_path / "SKILL.md")
        assert frontmatter["name"], skill_path
        assert frontmatter["description"], skill_path
        assert body.strip(), skill_path


def test_render_mdc_shape():
    frontmatter, _ = parse_skill_md(GETTING_STARTED)
    mdc = render_mdc(GETTING_STARTED)

    match = re.match(r"\A---\n(.*?)\n---\n\n(.*)", mdc, re.DOTALL)
    assert match, mdc
    parsed_header = yaml.safe_load(match.group(1))
    assert parsed_header["alwaysApply"] is False
    assert parsed_header["description"] == frontmatter["description"]
    assert "# Getting started with cuga" in match.group(2)


def test_render_agents_section_shape():
    frontmatter, _ = parse_skill_md(GETTING_STARTED)
    section = render_agents_section(GETTING_STARTED)

    assert section.startswith(f"## {frontmatter['name']}\n")
    assert f"_{frontmatter['description']}_" in section
    assert "---" not in section.splitlines()[0]
    # body headings are demoted by one level so they don't collide with the
    # top-level "## <name>" wrapper this section lives under
    assert "### Two different meanings" in section


def test_render_is_pure_and_repeatable():
    assert render_mdc(GETTING_STARTED) == render_mdc(GETTING_STARTED)
    assert render_agents_section(GETTING_STARTED) == render_agents_section(GETTING_STARTED)
