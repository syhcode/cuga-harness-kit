# cuga-harness-kit

Skills that teach Claude Code, Cursor, and Codex how to install, launch, and build with [cuga](https://github.com/cuga-project/cuga-agent) — the open-source generalist agent framework.

No git clone, no marketplace install. Just:

```bash
pip install cuga-harness-kit
cuga-harness-kit init
```

Run `init` from an empty new project you're starting from scratch, or from inside an existing cuga checkout — either way it writes the same skill set into the current directory:

- `.claude/skills/<name>/SKILL.md` — auto-discovered by Claude Code just by opening the folder.
- `.cursor/rules/cuga-<name>.mdc` — auto-discovered by Cursor.
- `AGENTS.md` — read wholesale by Codex (and other `AGENTS.md`-aware tools). Re-running `init` only touches the `<!-- cuga-harness-kit:start/end -->` block, so it won't clobber anything else you've written in that file.

Then open the folder in your assistant of choice and ask something like *"help me build a cuga tool"* or *"how do I launch cuga"*.

## What's included (v1)

| Skill | Teaches |
|---|---|
| `getting-started` | Entry point — routes to the right skill below. |
| `install-and-launch` | `pip install cuga`, `cuga start <mode>`. |
| `build-agent` | `CugaAgent` / `CugaSupervisor` SDK basics. |
| `build-cuga-skill` | Authoring cuga's own **runtime** skills (`.cuga/skills/<name>/SKILL.md`) — not to be confused with the IDE-assistant skills in this repo. |
| `build-tool` | Registering a LangChain / OpenAPI / MCP tool. |
| `author-policy` | Intent guards, playbooks, tool approval/guides, output formatters — one unified skill. |
| `knowledge-rag` | Document ingestion/search. |
| `debug-trajectory` | `cuga viz`, `cuga doctor`, common failure patterns. |

All 8 are authored once, as Claude-native `SKILL.md` files under `src/cuga_harness_kit/skills/`, and rendered into the Cursor/Codex shapes at `init` time (`src/cuga_harness_kit/render.py`) — there's a single source of truth per skill, not three copies to keep in sync by hand.

## CLI

```bash
cuga-harness-kit init [--targets claude,cursor,codex] [--force] [--dry-run]
```

- `--targets` — comma-separated subset of `claude`, `cursor`, `codex` (default: all three).
- `--force` — overwrite `.claude/skills/*` and `.cursor/rules/*` files that already exist with different content (default: skip and report). `AGENTS.md`'s managed block always updates regardless, since it never touches content outside its markers.
- `--dry-run` — print what would be written without touching disk.

## Development

```bash
uv sync  # or: pip install -e '.[dev]' equivalent via [dependency-groups]
uv run pytest
```

## Phase 2 (not yet built)

Real Claude Code plugin packaging (`.claude-plugin/plugin.json` + marketplace listing for `/plugin install`), slash commands, session hooks, a smarter `update`/diff command, and additional harness targets (Windsurf, `.clinerules`, `GEMINI.md`) — add these only if a real gap shows up.
