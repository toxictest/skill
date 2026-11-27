# Playbook: Data, Analytics, AI / Memory & MCP

**Triggers**: data, analyze, chart, dashboard, CSV, SQL, RAG, embedding,
vector, agent, memory, MCP, LLM pipeline, "analysis karo".

## Data analysis (native-first)

1. **Load & inspect** — pandas in `bash` (`python3` + pip install pandas/
   openpyxl as needed): shape, dtypes, nulls, outliers. Show the head.
2. **Clean visibly** — log every transformation (dropped rows, imputed
   values) so results are reproducible.
3. **Analyze** — group-by, correlations, time trends; sanity-check totals.
4. **Visualize** — matplotlib/seaborn PNG into the deliverable, or
   interactive HTML (inline JS, no CDN for preview). Multi-file dashboard →
   small static site served via `start_process`.
5. **Deliver** — `report.md`/`.xlsx` + charts; in chat: top 3–5 findings
   with numbers, caveats, methodology one-liner.

**Bundled scripts**: run `scripts/csv_profile.py <file>` FIRST — it prints
shape, duplicates, nulls, and per-column stats in one shot; then
`scripts/chart.py file.csv --col VALUE --x LABEL --out chart.png` for an
instant dark-themed bar/line chart. Drop to raw pandas only for deeper
analysis beyond their reports.

## AI/RAG/agent architecture (advise first, install only on commitment)

| Goal | Recommended from list | Notes |
|---|---|---|
| Vector store | qdrant (#45) | `docker`/local mode; also FAISS/Chroma for tiny jobs |
| RAG pipeline | llama_index (#46) or langgraph (#47) | llama_index for retrieval, langgraph for stateful agents |
| Orchestration | langchain (#55), crewAI (#50) | crewAI = role-based multi-agent |
| Low-code flows | Flowise (#48) | visual builder, needs server |
| Enterprise framework | semantic-kernel (#49) | heavy; only if user is in MS stack |
| Memory | mem0 (#53) | LLM long-term memory service |
| Tool integrations | composio (#52), MCP servers (#51) | MCP = open standard; check `list_connector_tools` first for native connectors |

**MCP/integrations rule**: Arena connectors are the fast path — if the user
wants Gmail/Notion/Slack etc., call `list_connector_tools` to confirm state;
only if missing do you suggest MCP/composio setup.

## Workflow for "build me an AI X"

1. One `ask_user` round: data source, output form, offline-vs-API, budget.
2. Minimal architecture diagram (mermaid/ASCII) in `PLAN.md`.
3. Build smallest working slice (ingest → retrieve → answer) and demo it.
4. Evaluate with 5 real questions; show failure cases honestly.
5. Ship with `requirements.txt` + run instructions.

## Pitfalls

- Don't spin up qdrant/langgraph for a 50-row CSV — pandas suffices.
- Never present model outputs as verified facts; label them.
- AutoGPT (#54) is legacy — recommend langgraph/modern stacks instead.

## Guardrails pattern (Batch 4)

- **Karpathy Behavioral** (#81): four-rule behavioral file designed to
  merge into `CLAUDE.md`/`AGENTS.md` — recommend when the user's agents
  repeat mistakes; reinforces our §5 quality bar for projects.
