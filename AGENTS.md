# AGENTS.md — operating schema for the Night City Arcade project

This repo builds a live-streamed, chat-controlled Cyberpunk TTRPG "arcade cabinet" rendered in Cyberpunk 2077.
Its **working memory is the wiki in `wiki/`**. Every agent session reads it, works, and writes back to it.

The wiki is *memory, not law*. It records what we know, how sure we are, and what we decided and why.
Any decision may be overturned: write a superseding ADR that cites evidence. Never silently contradict a page — update it.

---

## 1. Memory hierarchy (read in this order)

| Tier | File | Purpose | Budget |
|---|---|---|---|
| L0 | `wiki/now.md` | Current focus, active gate, next actions, blockers, last handoff | ≤ 80 lines. Rewrite, don't append. |
| L1 | `wiki/index.md` | Catalog of every page with a one-line summary | One line per page |
| L2 | `wiki/**/*.md` | Compiled knowledge: decisions, spikes, design, components, registers | Pages ≤ ~250 lines; split when larger |
| L3 | `raw/**` | Immutable sources and evidence (user docs, prior-project snapshots, logs, web notes, Cursor chats) | Never edited. Add new files only. |
| Log | `wiki/log.md` | Append-only timeline of operations | One entry per operation |

Session start: read `wiki/now.md`, then the last ~5 entries of `wiki/log.md`, then the latest `raw/chats/*/session.md` if resuming after a gap, then pull pages from `wiki/index.md` as needed.
Session end: run **handoff** (§4). On **close session**, also archive chats (§3).

## 2. Page types and frontmatter

Every wiki page except `log.md` starts with YAML frontmatter (flat keys; lists inline as `[a, b]`).

Common keys: `type`, `title`, `status`, `updated` (YYYY-MM-DD). Optional: `depends_on: [F-001, ADR-002]`, `tags`.

| type | Location | Extra keys | status values |
|---|---|---|---|
| `decision` | `wiki/decisions/ADR-NNN-slug.md` | `id`, `supersedes`, `revisit_if` | proposed · accepted · superseded · rejected |
| `spike` | `wiki/spikes/S-NN-slug.md` | `id`, `gate` | planned · running · passed · partial · failed |
| `design` | `wiki/design/` | — | draft · stable · retired |
| `component` | `wiki/components/` | — | draft · stable · built · retired |
| `plan` | `wiki/plan/` | — | active · done · retired |
| `source` | `wiki/sources/` | `raw: [paths]` | current · superseded |
| `register` | `wiki/facts.md`, `wiki/risks.md`, `wiki/questions.md` | `stack` (facts only) | active |
| `hub` | `now.md`, `index.md`, `overview.md`, `glossary.md` | — | active |

### Registers (ID'd entries inside one page)

- **Facts** (`wiki/facts.md`): claims about the engine, mods, vendors, host. Heading `### F-NNN — claim`, then lines
  `status:`, `scope:` (stack it was observed on), `evidence:` (raw path, log date, or URL), optional `note:`.
  Status ladder: `hypothesis` → `claimed` (prior notes, no proof) → `documented` (vendor/community docs) →
  `source-read` (we read the mod's code) → `verified` (we observed it ourselves, evidence recorded). Also `refuted`.
  A fact whose `scope` differs from the register's `stack:` line is **stale** until re-verified.
- **Risks** (`wiki/risks.md`): `### R-NN — title` + `likelihood:`, `impact:`, `mitigation:`, `owner:` (spike/phase).
- **Questions** (`wiki/questions.md`): `### Q-NN — question` + `blocks:` (IDs or phase), `default:` (what we assume until answered), `answer:`.

### Linking

Use relative markdown links (`[ADR-002](decisions/ADR-002-transport.md)`). They work in Cursor, GitHub, and Obsidian.
Reference register entries by bare ID (`F-007`, `R-01`, `Q-03`) — lint resolves them.

## 3. Operations

| Op | Trigger | Steps |
|---|---|---|
| **ingest** | New file in `raw/` | Write/refresh a `sources/` summary → update every affected page and register entry → note contradictions explicitly → update `index.md` → log. |
| **query** | A question about the project | Read `now.md` + `index.md` → read pages → answer with links. If the answer is reusable, file it as a page and log it. |
| **spike-report** | An experiment ran (in-game or otherwise) | Fill the spike's *Result* section with raw evidence (save logs/screenshots under `raw/evidence/YYYY-MM-DD-*`) → move facts up/down the status ladder → mark dependents (pages whose `depends_on` includes a refuted fact) → update gate status in `plan/roadmap.md` → log. |
| **decide** | A choice with consequences | New ADR (or supersede one: set old `status: superseded`, link both ways) → update affected design/component pages → log. |
| **lint** | Weekly, after big ingests, before handoff | `python tools/wiki.py lint` → fix errors → judge warnings → log. Also look for contradictions the tool can't see. |
| **handoff** | End of every session | Rewrite `now.md` (focus, gate, next 3 actions, blockers, what just changed) → log entry → `python tools/wiki.py lint`. |
| **close session** | User ends a dev stretch | **handoff** → copy all Cursor transcripts for this project into `raw/chats/YYYY-MM-DD-slug/` (parent `.jsonl`, subagents, compaction) → write `session.md` digest (user constraints, decisions, arc) → commit and push unless user said no commit. **Checkpoint** = same save without treating the session as ended. |
| **playtest-ingest** | After any test stream | Session report → `raw/sessions/` → update design pages (pacing, balance, chat behaviour) and risks. |

Log entry format (parseable): `## [YYYY-MM-DD] op | title` followed by short bullets of pages touched.

## 4. Tooling

- `python tools/wiki.py lint` — frontmatter, broken links, unknown IDs, orphans, index coverage, stale facts, pages depending on refuted/stale facts.
- `python tools/wiki.py status` — dashboard: gates, spikes, blocking questions, high risks, fact ladder counts.
- Stdlib only. Extend it when a maintenance chore repeats twice.

## 5. Engineering guardrails (for code work)

- **Never invent game APIs.** Check `wiki/facts.md`, then NativeDB (https://nativedb.red4ext.com) or mod source. Unverified calls must be wrapped in `pcall` and logged.
- The rules engine is pure and deterministic; all randomness comes from the provable dice service ([ADR-006](wiki/decisions/ADR-006-provable-dice.md)).
- No generative LLM in the authoritative path (rules, votes, outcomes). See [ADR-009](wiki/decisions/ADR-009-llm-boundary.md).
- Everything the show does must be reproducible from the event log ([ADR-007](wiki/decisions/ADR-007-event-sourced-ledger.md)).
- Do not write rulebook text from Cyberpunk RED into code, overlays, or docs (IP — see `R-08`).
- When code changes a contract, update `wiki/components/contracts.md` in the same change.
