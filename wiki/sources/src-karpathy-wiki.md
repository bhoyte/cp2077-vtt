---
type: source
title: Karpathy's LLM Wiki pattern — what we adopted and how we extended it
status: current
updated: 2026-10-11
raw: [raw/web/karpathy-llm-wiki.md]
---

# Source: Karpathy, "LLM Wiki" (gist, 2026-04-04)

**The pattern.** Three layers: immutable raw sources, an LLM-maintained markdown wiki, and a schema file. Three operations:
ingest, query, lint. Two special files: `index.md` (catalog) and `log.md` (append-only, greppable). Knowledge is
compiled once and kept current, not re-derived per question.

## Adopted as-is
raw/ is immutable · the LLM writes the wiki · `AGENTS.md` is the schema · ingest/query/lint · index + greppable log · Obsidian-compatible links · git as history.

## Extensions for a *project* (his is a knowledge base; ours has to get something built)

| Extension | What it adds | Where |
|---|---|---|
| **Memory hierarchy** | `now.md` (L0, rewritten each session) above the index, so any agent resumes in one read | AGENTS.md §1 |
| **Epistemic ladder** | Every engine claim carries hypothesis → claimed → documented → source-read → verified/refuted | facts.md |
| **Version-scoped truth** | Facts record the mod stack they were observed on; a stack change auto-flags them stale | facts.md `stack:`, lint |
| **Truth maintenance** | Pages declare `depends_on`; refuting a fact flags every dependent page | lint |
| **Experiments as first-class pages** | Spikes: hypothesis → procedure → pass criteria → result; the only way facts climb the ladder | spikes/ |
| **Decisions with revisit triggers** | ADRs say what would overturn them; supersession links both ways | decisions/ |
| **Registers with IDs** | Facts / risks / questions as ID'd entries; questions carry `blocks:` and a working `default:` | registers |
| **New operations** | spike-report, decide, handoff, playtest-ingest | AGENTS.md §3 |
| **The product feeds the wiki** | The show's ledger writes session reports into raw/sessions/; design pages learn from every stream | components/ledger |
| **Machine-checkable** | `tools/wiki.py` lint + status dashboard over frontmatter and IDs | tools/ |

Principle kept from the user: the wiki is **working memory, not a design constraint**. It records belief and decisions; it never forbids.
