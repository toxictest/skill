# How to Use super-skill on Arena.ai

No install, no API keys, no plugins. The skill lives in this workspace and
runs with Arena's built-in tools (web_search, bash, files, images, speech).

## ⚡ AUTO-MODE — seedha task do, skill khud choose hoga

Skill ab **always-on auto-router** hai. Aapko "super-skill" bolne ki
bilkul zaroorat nahi — **bas direct task likho**:

```
[seedha task likho — koi prefix nahi]
```

Examples (no prefix needed):
```
ye CSV ka analysis karo
ek landing page banao
is topic pe 3 sources ke saath research karo
mera resume PDF banao
is code ka security review karo
ek logo image banao
```

Kya hota hai:
1. Classifier chalta hai → `python3 scripts/choose_playbook.py "<task>"`
2. Ek line mein route announce hota hai: `→ Route: playbooks/…`
3. Sahi playbook load → plan → execute → verify → deliver

Prefix wale forms bhi chalte hain (agar aap explicitly skill use karna
chaho):

### Copy-paste examples

| You type | What happens |
|---|---|
| `super-skill use karke ye kaam kar: is CSV ka analysis do` | loads `data-ai-memory.md` → runs `csv_profile.py` → report |
| `super-skill se ek landing page banao` | loads `coding-dev.md` → `html_template.py` → preview |
| `is repo ka security review karo (authorized/local)` | loads `security.md` → semgrep-style review → findings table |
| `super-skill se 3 sources ke saath research karo: [topic]` | loads `research-web.md` → search → `check_urls.sh` → cited answer |
| `super-skill se ye PDF banawo: [content]` | loads `documents.md` → python-docx → `office_validate.py` → present |

## In a NEW Arena chat (later)

Workspace files persist in this workspace. If the skill folder is not
visible in the new chat:

1. **Easiest**: attach/paste `super-skill/SKILL.md` and say
   *"ye skill follow karo + [task]"* — I will load the rest of the folder
   from the workspace if present, or follow SKILL.md alone (it is
   self-sufficient: router + workflow + script catalog are all inside).
2. **Full setup**: say *"super-skill folder workspace mein dobara banao"*
   and point me to this session's files — everything regenerates.

## What makes it work here (100%, no edits)

- Router (SKILL.md §3) → picks 1 of 8 playbooks
- Workflow (§2) → plan → execute → verify → deliver
- Bundled scripts (§4) → run with `python3`/`bash`, already tested
- Safety rules (§6) → always active
- All Arena-native tools referenced in the skill exist in this platform

## Tips

- Hinglish/English/Hindi — jo bhi likho, summary usi mein milegi
- One task at a time gives best results; big jobs → I write `PLAN.md` first
- **Video pipeline** works: `"reel banao: [idea]"` → frames + narration → MP4
- Package health anytime: `python3 scripts/selftest.py` · integrity:
  `python3 scripts/make_manifest.py --verify`
- Skill files are editable: tweak a playbook or add scripts anytime;
  regenerate source docs with `python3 scripts/build_sources.py`, then
  refresh `MANIFEST.json`
