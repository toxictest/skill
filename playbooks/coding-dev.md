# Playbook: Coding & Development

**Triggers**: code, build, app, website, API, bug, refactor, test, deploy,
repo, script, "banao".

## Workflow

1. **Clarify the spec** — language/stack, target runtime, must-have
   features, success criteria. One `ask_user` round only if blocking.
2. **Plan** — for anything > ~100 lines, write `PLAN.md` (structure, files,
   milestones) before coding. Reference stacks the user already uses.
3. **Build in increments** — create files under `/home/user/<project>/`;
   after each increment run something (script/test/build). Prefer minimal
   deps; state every package installed.
4. **Verify**
   - Run the test suite / lint / build command and show real output.
   - For web apps: `start_process` the dev server, bind `0.0.0.0`, wait for
     port, fix any preview warnings (host/origin rejection) in the same turn.
   - Browser-facing code uses **relative URLs** — never `localhost`/`127.0.0.1`
     from the page's perspective.
5. **Deliver** — `present_file` the entry file (or project folder summary),
   plus run instructions in chat.

## Arena specifics

- **Bundled scripts**: `git_commit_msg.py` → conventional-commit suggestion
  from the staged diff (#84 pattern); `run_checks.py [DIR]` → auto-detect
  project markers and run lint/test/build (use `--list` for dry-run);
  `html_template.py "Title" out.html [--dark] [--accent #hex]` →
  preview-safe single-file HTML scaffold (inline CSS/SVG, no CDN).
- Sandbox is Linux; only `/home/user` persists across messages.
- Long-lived servers → `start_process` (never `bash` loops); stop them with
  `stop_process` when done.
- In-app preview iframe has **no network**: inline CSS/SVG/JS or data-URIs
  in single-file HTML deliverables; CDNs work only in the downloaded copy.
- Installed packages/caches are wiped between sessions — ship
  `requirements.txt` / `package.json` with the deliverable.

## Quality bar

- Code compiles/runs before you claim it works (show the run).
- No placeholder functions left in deliverables; TODOs called out explicitly.
- Read existing files before editing; keep edits surgical (`edit_file`).
- Security: never embed real secrets; use env vars/example configs.

## Methodology references (Batch 2)

- **SDD — spec → plan → tasks** (#68 `spec-kit-command-cursor`): for
  non-trivial builds, tighten the PLAN phase as
  `/specify` (what & why) → `/plan` (how) → `/tasks` (checklist) — same
  spirit as superpowers' writing-plans; use `PLAN.md` with these three
  headings.
- **Team standards** (#69 `cursor-handbook`): when the user has a team
  codebase, encode conventions as a rules file (110-rule handbook pattern:
  type-check over huge test runs, block hardcoded secrets, consistent
  style) — portable to any agent's rules/AGENTS.md.
- **Cross-session task logs** (#70 `ai-skill-commands`): for long projects,
  keep a task/chat log file so work isn't duplicated across sessions
  (personal-kanban + chat-log idea — adopt pattern, not the repo).

## Review, git hygiene & writing (Batch 4)

- **Review before merge** (#85 Qodo landscape + #84 patterns):
  severity-ordered findings (Critical → Warning → Suggestion) with a
  security lens (SQLi, XSS, auth bypass, null checks, dead code);
  spec-check against repo standards; security-sensitive diffs get the
  Trail of Bits differential-review approach (ties to #31).
  Never claim "works" without running it (**truth-first** pattern).
- **Git hygiene** (#84): conventional commits generated from the staged
  diff; PR bodies with a test-plan section; changelog entries from commit
  ranges. Env broken? **env-doctor** sequence: runtime versions → deps →
  env vars → DB → ports.
- **Writing help** (#84 `humanize-writing`): when asked for prose/docs,
  strip AI-ish phrasing; concrete > fluffy.
- **Heavier methodologies**: gstack (#82, team-in-a-box) and GSD (#83,
  spec-driven) — cherry-pick steps into PLAN; don't adopt wholesale.

## External tools (recommend, don't auto-install)

- Pair-programming in user's own terminal → **aider** (`pip install aider-chat`).
- Large autonomous multi-file jobs → **OpenHands**, **SWE-agent**.
- Self-hosted completions → **Tabby**; IDE assist → **Continue**.
- Claude Code (#21) is this platform's peer — not an add-on.
