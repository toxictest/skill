# Playbook: Computer, Browser & System Automation

**Triggers**: automate, bot, browser click, fill form, scrape UI, n8n,
workflow, server, Linux, Ansible, service, "automate kar do".

## Browser automation (in-sandbox)

1. Prefer **static fetch** (`fetch_page`) when DOM reading is enough —
   cheaper and preview-safe.
2. For real interaction (login state, clicks, multi-step flows): install
   `browser-use` (#9) or `Stagehand` (#25) — both need a local Chromium in
   the sandbox; verify with a 2-site smoke test before the full run.
3. **Preview constraint**: browser-facing code must use relative URLs —
   the user's browser cannot reach sandbox `localhost`. For user-facing
   flows, the dev server proxies via relative paths.
4. Rate-limit and respect `robots.txt`/ToS; identify what you automate.

## Workflow automation (n8n / Activepieces)

- These (#26, #27) are **self-hosted servers** — recommend architecture and
  export JSON workflow definitions the user can import; do not attempt to
  run a full n8n instance unless the user asks (then `start_process`,
  bind `0.0.0.0`, deliver the preview URL).
- Composio/awesome-claude-skills connect-apps (#52, Composio §4): app
  integrations need API keys — ask for key, never hardcode.

## Linux / system tasks

| Task | Approach |
|---|---|
| Server/admin in sandbox | native `bash` + `start_process`; systemd not guaranteed |
| **Real server ops (deploy/SSL/WAF/DB/monitoring)** | **Reference skill #66 `michael-ltm/linux-server-skill`** — BaoTa/1Panel-style AI panel over SSH: Nginx vhosts, Let's Encrypt, ModSecurity+OWASP CRS, MySQL/PG/Redis/Mongo, PM2/systemd deploys, cron, logs, users. Claude Code: `/plugin marketplace add michael-ltm/linux-server-skill` + `/plugin install linux-server-skill@linux-server-skill`. Always confirm SSH target ownership before touching a server. |
| Config management on user infra | Ansible (#63) — write playbook YAML, user runs it |
| Phone/gyro hardware control | **#71 `Mouse_controller`** (gyro phone-as-mouse, UDP/WebSocket) — user-device project, not sandbox; reference only |
| File share between devices | Localsend (#64) — user-device install, not sandbox |
| Android shell | Termux (#61) — user device only |
| Shell theme / fetch | ohmyzsh (#62), fastfetch (#65) — cosmetic dotfiles, write them on request |
| Windows tweaks | PowerToys (#24) — Windows only; irrelevant to this Linux sandbox |

**Bundled script**: `scripts/health_check.py --http URL --tcp host:port`
→ markdown UP/DOWN report with latencies (good first step for any server
task; exit code works in CI).

## Workflow

1. Identify what runs **where** (sandbox vs user's machine vs cloud).
2. For sandbox jobs: script it (`bash`/python), make it idempotent, then
   `start_process` if long-lived; stop when done.
3. For user machines: produce the script/role + exact run command; never
   claim it executed.
4. Verify: show command output; for servers, confirm port listening and
   HTTP 200 from inside sandbox.
