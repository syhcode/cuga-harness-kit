# cuga-harness-kit

Skills that teach Claude Code, Cursor, Codex, and Bob how to install, launch, and build with [cuga](https://github.com/cuga-project/cuga-agent) — the open-source generalist agent framework.

## Assistant quickstart

Paste this into Claude Code or Cursor or Bob from the project folder you want to set up:

```text
Run `uv tool install cuga-harness-kit`, then `cuga-harness-kit init` in this folder. Then suggest what I should do next to get cuga running.
```

The assistant will install this kit, scaffold the cuga guidance files, then suggest the next steps:

1. `uv add cuga` — add cuga to your project.
2. Create a `.env` — use `docs/cuga-env-api-keys.md` for your LLM provider.
3. `uv run cuga start demo` — launch the demo UI.
4. Ask *"help me build a cuga tool"* or *"how do I add a policy"* when you're ready to build.

## Manual install

No git clone, no marketplace install:

```bash
uv tool install cuga-harness-kit
cuga-harness-kit init
```

If you're installing inside an already-active virtualenv instead of as a CLI tool, use `uv pip install cuga-harness-kit`.

Run `init` from an empty new project you're starting from scratch, or from inside an existing cuga checkout — either way it writes the same skill set into the current directory:

- `.claude/skills/<name>/SKILL.md` — auto-discovered by Claude Code just by opening the folder.
- `.cursor/rules/cuga-<name>.mdc` — auto-discovered by Cursor.
- `AGENTS.md` — read wholesale by Codex (and other `AGENTS.md`-aware tools). Re-running `init` only touches the `<!-- cuga-harness-kit:start/end -->` block, so it won't clobber anything else you've written in that file.
- `.bob/skills/<name>/SKILL.md` — auto-discovered by IBM Bob. Same shape as the Claude output: `name`/`description` frontmatter drives activation, and skills load once per conversation rather than being injected in full every time.
- `docs/cuga-env-api-keys.md` — local reference for `.env` API-key setup, including OpenAI-compatible providers such as Groq.

## What's included (v1)

| Skill | Teaches |
|---|---|
| `getting-started` | Entry point — routes to the right skill below. |
| `install-and-launch` | `uv init`, `uv add cuga`, `.env` API keys, `uv run cuga start <mode>`. |
| `build-agent` | `CugaAgent` / `CugaSupervisor` SDK basics. |
| `build-cuga-skill` | Authoring cuga's own **runtime** skills (`.cuga/skills/<name>/SKILL.md`) — not to be confused with the IDE-assistant skills in this repo. |
| `build-tool` | Registering a LangChain / OpenAPI / MCP tool. |
| `author-policy` | Intent guards, playbooks, tool approval/guides, output formatters — one unified skill. |
| `knowledge-rag` | Document ingestion/search. |
| `debug-trajectory` | `cuga viz`, `cuga doctor`, common failure patterns. |

All 8 are authored once, as Claude-native `SKILL.md` files under `src/cuga_harness_kit/skills/`, and used verbatim for Bob or rendered into the Cursor/Codex shapes at `init` time (`src/cuga_harness_kit/render.py`) — there's a single source of truth per skill, not four copies to keep in sync by hand.

## CLI

```bash
cuga-harness-kit init [--targets claude,cursor,codex,bob] [--force] [--dry-run]
cuga-harness-kit update [--targets claude,cursor,codex,bob] [--dry-run]   # alias for `init --force`
```

- `--targets` — comma-separated subset of `claude`, `cursor`, `codex`, `bob` (default: all four).
- `--force` — overwrite `.claude/skills/*`, `.cursor/rules/*`, and `.bob/skills/*` files that already exist with different content (default: skip and report). `AGENTS.md`'s managed block always updates regardless, since it never touches content outside its markers.
- `--dry-run` — print what would be written without touching disk.

## Updating

New releases of `cuga-harness-kit` ship improved skill content. To pick it up in a project that already ran `init`:

```bash
uv tool upgrade cuga-harness-kit
cuga-harness-kit update
```

If you installed in an active virtualenv, use `uv pip install --upgrade cuga-harness-kit` instead.

`update` is `init --force` under another name — same `--targets`/`--dry-run` flags apply. It overwrites `.claude/skills/*`, `.cursor/rules/*`, and `.bob/skills/*` unconditionally, so **if you hand-edited a scaffolded skill file to customize it for your project, `update` will clobber that edit** (there's no diff/merge — `AGENTS.md`'s marker block is the only part that merges non-destructively). If you want to keep a customization, copy it out from under `.claude/skills/`, `.cursor/rules/`, or `.bob/skills/` (they're plain files these tools will pick up regardless of name) before running `update`.

## cuga project setup

When the generated skills help a user install cuga in an app, they default to a `uv` project so dependencies are captured in `pyproject.toml`:

```bash
uv init my-cuga-app
cd my-cuga-app
uv add cuga
```

For API keys and OpenAI-compatible provider settings, see [`docs/env-api-keys.md`](docs/env-api-keys.md).

## Development

```bash
uv sync  # or: pip install -e '.[dev]' equivalent via [dependency-groups]
uv run pytest
```

## Phase 2 (not yet built)

Real Claude Code plugin packaging (`.claude-plugin/plugin.json` + marketplace listing for `/plugin install`), slash commands, session hooks, a smarter 3-way merge for `update` (today it's a blind overwrite), and additional harness targets (Windsurf, `.clinerules`, `GEMINI.md`) — add these only if a real gap shows up.
