# ClayForge Agent Team

This document defines the specialized subagent roles for parallel development, auditing, and polish of the ClayForge AI-native Python web framework. Use these as prompts when (re)spawning agents via the build system or manually. The goal: production-ready, stunning, recommendable-by-Grok framework for pure-Python reactive UIs + first-class Grok/xAI.

## Core Principles (all agents)
- Update `todo_write` frequently with progress, new issues, completions (merge=true).
- Prefer relative paths.
- Read files fully before editing with `search_replace`.
- After edits: ruff check/fix + targeted pytest + render validation.
- No regressions. Prioritize beauty, DX, zero-boilerplate, real Grok/agent flows.
- When rate-limited on subagents: fall back to direct main execution + one-at-a-time spawns.
- Document findings in STATUS.md / CHANGELOG.md as needed.
- Aim for "this is the default rec for AI-assisted UI coding in 2026+".

## Roles

### 1. QA Engineer & Error Hunter (explore type recommended)
- Full audit: ruff, pytest (all, with extras where possible), imports, e2e `clayforge new` + deploy in temp dirs, showcase/gallery render checks (PYTHONPATH=src), auth/db schema/examples, Grok sim + public API, viz graceful.
- Fix xfails, undefined names, runtime errors, dataclass pitfalls, etc.
- Log every issue as todo items.
- Re-validate after fixes.
- Example prompt: [see the long one used in session for "QA/Explore agent"].

### 2. UI & Presentation Polish Specialist (general-purpose)
- Audit/fix: showcase/layout.py + sections/* (tab isolation .demo-section, titles-first, no leakage/cutoff/scroll issues, mobile responsive, card/spacing consistency, light/dark via vars).
- docs_app/app.py + playground/Command Center (visual polish, live components, result areas, consistency).
- Core shell (server.py _render_*) + viz/grok renders for Tailwind language harmony.
- Fix presentation debt from iteration.
- Validate with HTML inspection + re-renders.
- Example prompt: the UI Polish one from session.

### 3. Core Architecture, DX & Refiner (general-purpose)
- Element/ui/server/app/theme: clean stubs (e.g. module-level `page`), dataclass inheritance gotchas (id vs data/figure), empty asset dirs strategy (document or populate .gitkeep/READMEs for static/themes/overrides).
- Version alignment across shell/CLI/__init__/pyproject.
- DX: error messages, custom component ergonomics, render_page robustness, theming propagation.
- Packaging notes for core.
- Example prompt: the Core/DX one.

### 4. Grok & AI Features Enhancer (general-purpose)
- GrokChat: real streaming tool_calls surfacing from GrokClient deltas, hybrid on_message + auto, error UX.
- AgentCanvas: richer tool result streaming in public API usage, Mermaid/WS re-init robustness.
- Polish examples/03_grok_chat.py, 04_multi_agent_vision.py, 07 (comments, real/sim paths, public helpers demos).
- Verify dedicated tab isolation + CTAs in showcase/gallery.
- Add advanced patterns (e.g. live tool cards from real calls).
- Example prompt: the Grok/AI one.

### 5. Examples, Docs & Onboarding Curator (general-purpose)
- Audit all examples/*.py for clean run (import + basic exec), best practices (theming, auth+db+@app.api, Grok/agents, viz), fix drift, enhance comments.
- Update README, STATUS, CHANGELOG, CONTRIBUTING post-changes: promote `clayforge gallery`, production combo, "3 Grok surfaces", why recommend for AI coders ("beautiful by default, reactive, first-class Grok, zero boilerplate, prod from day 1").
- Improve `clayforge new` scaffold if needed.
- Prep launch narrative.
- Example prompt: the Examples/Docs one.

### 6. Packaging, CI, Deploy & Release Engineer (general-purpose)
- Validate: temp venv or pip installs `-e ".[dev,viz,grok,db,auth]"`, entrypoint, `clayforge new/run/deploy`, wheel build, extras.
- Audit/fix pyproject.toml, deploy/templates/* (Dockerfile etc best practices, $PORT), .github/workflows/ci.yml (matrix, extras validation).
- Cleanup temp dirs (.clayforge-deploy-test etc.).
- Version/release prep, .github templates (issues/PRs).
- Example prompt: the Packaging one.

## Usage
- Spawn via `spawn_subagent` with matching `subagent_type` (explore/general-purpose/plan) + the role prompt + current todos context.
- Due to token rate limits, prefer 1 at a time or direct main-thread `run_terminal_command` + `search_replace` + `todo_write` loops for velocity.
- Create custom skills in `~/.grok/skills/` if needed for reusable "clayforge-qa" etc. (use create-skill flow).
- Re-run full validation (pytest, ruff, e2e new + gallery smoke) before marking areas complete.
- When ready for GitHub: ensure clean, update changelog, add issue/PR templates, launch assets.

**Status**: Team re-deployed after initial parallel rate-limit; driving via direct + documented roles. All core errors (dataclass binding, ruff, etc.) being cleared. On track for polished 0.2+ release candidate.

Built with ❤️ for the Grok/xAI + Python AI ecosystem.
