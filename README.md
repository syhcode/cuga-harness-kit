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

All 8 are authored once, as Claude-native `SKILL.md` files under `src/cuga_harness_kit/plain-skills/`, and used verbatim for Bob or rendered into the Cursor/Codex shapes at `init` time (`src/cuga_harness_kit/render.py`) — there's a single source of truth per skill, not four copies to keep in sync by hand.

## CLI

```bash
cuga-harness-kit init [--targets claude,cursor,codex,bob] [--force] [--dry-run] [--migration] [--skip-sdk] [--cuga-ref REF]
cuga-harness-kit update [--targets claude,cursor,codex,bob] [--dry-run] [--migration] [--skip-sdk] [--cuga-ref REF]   # alias for `init --force`
```

- `--targets` — comma-separated subset of `claude`, `cursor`, `codex`, `bob` (default: all four).
- `--force` — overwrite `.claude/skills/*`, `.cursor/rules/*`, and `.bob/skills/*` files that already exist with different content (default: skip and report). `AGENTS.md`'s managed block always updates regardless, since it never touches content outside its markers.
- `--dry-run` — print what would be written without touching disk.
- `--migration` / `--skip-sdk` / `--cuga-ref` — see "Migration pipeline" below.

## Migration pipeline (optional, claude/bob only)

Besides the 8 guidance skills, this kit also ships the **cuga-migrator** pipeline — a separate,
heavier tool that converts a *different* source agent system into a cuga SDK implementation,
using a 5-stage subagent pipeline (analyst → implementer → test_writer → evaluator → debugger).
It's opt-in and **exclusive**: `init --migration` scaffolds *only* the migration pipeline for the
given `--targets`, not the 8 guidance skills (they're two different workflows — run `init` a
second time without `--migration` if you want both in the same project). Its canonical,
hand-maintained source lives under
`src/cuga_harness_kit/migration-skills/{claude,bob}/` (plus the shared `cuga-templates/` alongside
them) — a separate boundary from the plain guidance skills, since this content is a full
standalone project (subagents, launch scripts, its own directory layout) rather than a single
`SKILL.md`.

```bash
cuga-harness-kit init --targets claude --migration   # or --targets bob
```

This additionally scaffolds `.claude/commands/migrate.md`, `.claude/agents/*.md` (the 5 subagents),
the `cuga-migrator` / `cuga-source-sync` / `cuga-template-sync` skills, `cuga-templates/`,
`migrate.sh` / `source_sync.sh` / `cuga_sync.sh`, and `migration_from/`/`migration_to/` — then
`git clone`s the [cuga SDK](https://github.com/cuga-project/cuga-agent) into
`migration_to/cuga-agent/` (shallow, `--depth 1`), which the pipeline's own agents/skills read
directly (e.g. `migration_to/cuga-agent/src/cuga/sdk.py`).

- Only `claude` and `bob` support it — the pipeline needs subagent/orchestration primitives Cursor
  and Codex don't have. `--migration` with only `cursor`/`codex` in `--targets` prints a notice
  and does nothing.
- `--skip-sdk` skips the SDK clone (copy it in yourself: `git clone
  https://github.com/cuga-project/cuga-agent migration_to/cuga-agent`). `--cuga-ref
  <branch-or-tag>` pins a specific version. If `migration_to/cuga-agent/` already exists, `init`
  leaves it alone (never re-clones, `--force` or not).
- **`.claude/settings.json` and `.claude/hooks/` are intentionally not scaffolded** — writing or
  merging a settings file is too easy to clobber a project's existing permissions/hooks config. If
  you want the upstream tool-use-logging hook, wire it in yourself.
- Once scaffolded, three more subcommands become available, each dispatching to the matching
  launch script in the current directory (or ask Claude Code / Bob directly — the `cuga-migrator`,
  `cuga-source-sync`, and `cuga-template-sync` skills are natural-language triggered the same way
  the other 8 skills are):

  ```bash
  cuga-harness-kit migrate <source-name> <target-name> [--stages stage[,stage...]]
  cuga-harness-kit source_sync <source-name>
  cuga-harness-kit cuga_sync
  ```

  `migrate` runs the full pipeline (or just the listed `--stages`); `source_sync` scouts a new
  source repo under `migration_from/<name>/` and writes its `CLAUDE.md`; `cuga_sync` syncs
  `cuga-templates/` against a `migration_to/cuga-agent/` you've updated to a newer SDK version. See
  the scaffolded kit's own `README.md` (written alongside everything else by `init --migration`)
  for the full credentials/directory-layout reference and natural-language trigger phrasing.

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
