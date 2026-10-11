# Changelog

All notable changes to this project are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.1] - 2026-10-11

### Fixed

- Everyday dev commands were blocked by the model (`ls -la`, `npm run build`,
  `go test ./...`, `echo hello`: 11 of 50 judgments in a spot check). A new
  safe-command lane (`safe_commands` in `policy.yaml`) allows single plain
  commands without the model; chaining, pipes, redirects, substitution,
  program-running flags, and sensitive paths never qualify.
- A model failure at runtime (checkpoint download, OOM, inference error) is no
  longer reported as a model verdict: it falls back to regex+heuristics with
  `verdict_source: "heuristic"`, a "Model error" reason, and a logged warning.

### Added

- Shell eval set (`eval/run_eval.py --set shell`): 28 everyday + 22
  dangerous/bypass commands. Real model: 48/50 (was 32/50); CI gates it in
  mock mode. AgentDojo results unchanged (25/27, 92/97).
- Shell regexes: pipes into a shell or `nc`, `curl -d @file` uploads,
  redirects into `/etc/`, git `core.hooksPath`/`core.pager`-style config,
  `git push --force`.
- `verdict_source: "allowlist"` for safe-command verdicts.
- `laya-guard serve` loads the model before listening so the first hook call
  doesn't time out (and fail open) during the checkpoint download.
  Skip with `--no-warmup`.
- `guard-hook.sh` honors `LAYA_GUARD_URL`, like the other adapters.
- `SECURITY.md`, this changelog, and CI on Python 3.10–3.13.

### Changed

- `guard-hook.sh` judges only the command for the Bash tool, not the agent's
  description.
- PyPI summary and README install instructions (the PyPI name is
  `laya-guardrail`; `laya-guard` on PyPI is an unrelated project).

## [0.2.0] - 2026-10-11

### Added

- Adapters for 11 agents: Claude Code, OpenCode, Codex CLI, Cursor, Kilo Code,
  Windsurf, Cline, Gemini CLI, Qwen Code, Amp, Copilot CLI.
- `verdict_source` in responses (`regex` | `model` | `heuristic`).
- English policy reasons (`message_en`), chosen by input language.
- Comparison table, use-case docs, English demo GIF, brand assets.

### Changed

- Blocks now require risk agreement: AgentDojo benign overblocks dropped
  from 24 to 5 of 97 (attacks: 25/27 blocked).

## [0.1.0] - 2026-10-11

### Added

- Initial release: regex prefilter (10 policies) + local Laya judge,
  HTTP server (`/guard`, `/v1/systemone`), `check` / `serve` / `stats` CLI,
  Claude Code PreToolUse hook, local redacted telemetry, Korean 30-case eval,
  AgentDojo judge-level eval, E2E rollout harness.

[Unreleased]: https://github.com/scs0209/laya-guard/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/scs0209/laya-guard/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/scs0209/laya-guard/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/scs0209/laya-guard/releases/tag/v0.1.0
