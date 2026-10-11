"""Wiki maintenance tool: `python tools/wiki.py lint` and `python tools/wiki.py status`.

Stdlib only. Conventions are defined in AGENTS.md.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
SPECIAL = {"log.md"}
HUBS_EXEMPT_FROM_ORPHAN = {"now.md", "index.md", "log.md"}

STATUSES = {
    "decision": {"proposed", "accepted", "superseded", "rejected"},
    "spike": {"planned", "running", "passed", "partial", "failed"},
    "design": {"draft", "stable", "retired"},
    "component": {"draft", "stable", "built", "retired"},
    "plan": {"active", "done", "retired"},
    "source": {"current", "superseded"},
    "register": {"active"},
    "hub": {"active"},
}
REQUIRED = {"type", "title", "status", "updated"}
REQUIRED_BY_TYPE = {"decision": {"id"}, "spike": {"id", "gate"}, "source": {"raw"}}
FACT_STATUSES = ["hypothesis", "claimed", "documented", "source-read", "verified", "refuted"]
TRUSTED_FACT_STATUSES = {"documented", "source-read", "verified"}

ID_RE = re.compile(r"\b(F-\d{3}|R-\d{2}|Q-\d{2}|ADR-\d{3}|S-\d{2})\b")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)
LOG_ENTRY_RE = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] [a-z][a-z-]* \| .+")
ENTRY_RE = re.compile(r"^### ((?:F-\d{3})|(?:R-\d{2})|(?:Q-\d{2})) — (.+)$")


@dataclass
class Page:
    path: Path
    meta: dict
    body: str

    @property
    def rel(self) -> str:
        return self.path.relative_to(ROOT).as_posix()


@dataclass
class Entry:
    id: str
    title: str
    fields: dict = field(default_factory=dict)
    page: str = ""


def parse_value(raw: str):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        return [v.strip() for v in raw[1:-1].split(",") if v.strip()]
    return raw


def parse_page(path: Path) -> Page:
    text = path.read_text(encoding="utf-8")
    meta: dict = {}
    body = text
    if text.startswith("---\n") or text.startswith("---\r\n"):
        lines = text.splitlines()
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                for line in lines[1:i]:
                    if ":" in line:
                        key, val = line.split(":", 1)
                        meta[key.strip()] = parse_value(val)
                body = "\n".join(lines[i + 1 :])
                break
    return Page(path, meta, body)


def parse_entries(page: Page) -> list[Entry]:
    entries: list[Entry] = []
    current: Entry | None = None
    for line in page.body.splitlines():
        m = ENTRY_RE.match(line)
        if m:
            current = Entry(m.group(1), m.group(2), page=page.rel)
            entries.append(current)
            continue
        if line.startswith("#"):
            current = None
            continue
        if current and re.match(r"^[a-z_]+:", line):
            key, val = line.split(":", 1)
            current.fields[key.strip()] = parse_value(val)
    return entries


class Wiki:
    def __init__(self) -> None:
        self.pages = [parse_page(p) for p in sorted(WIKI.rglob("*.md"))]
        self.by_rel = {p.rel: p for p in self.pages}
        self.entries: dict[str, Entry] = {}
        for p in self.pages:
            if p.meta.get("type") == "register":
                for e in parse_entries(p):
                    self.entries[e.id] = e
        self.page_ids = {p.meta["id"]: p for p in self.pages if isinstance(p.meta.get("id"), str)}
        facts_page = self.by_rel.get("wiki/facts.md")
        self.stack = facts_page.meta.get("stack", "") if facts_page else ""

    def known_ids(self) -> set[str]:
        return set(self.entries) | set(self.page_ids)

    def fact_state(self, fid: str) -> str:
        e = self.entries.get(fid)
        if not e:
            return "missing"
        status = e.fields.get("status", "")
        scope = e.fields.get("scope", "")
        if status in TRUSTED_FACT_STATUSES and str(scope).startswith("cp2077-") and scope != self.stack:
            return "stale"
        return status

    def id_home(self, ident: str) -> str | None:
        if ident in self.page_ids:
            return self.page_ids[ident].rel
        if ident in self.entries:
            return self.entries[ident].page
        return None

    def links(self, page: Page) -> list[tuple[str, Path | None]]:
        out = []
        prose = CODE_RE.sub("", page.body)
        for target in LINK_RE.findall(prose):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            out.append((target, (page.path.parent / clean).resolve()))
        return out


def lint(w: Wiki) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    inbound: dict[str, int] = {p.rel: 0 for p in w.pages}
    index_targets: set[str] = set()
    known = w.known_ids()

    for p in w.pages:
        name = p.path.name
        if name not in SPECIAL:
            missing = REQUIRED - p.meta.keys()
            ptype = p.meta.get("type")
            if missing:
                errors.append(f"{p.rel}: missing frontmatter {sorted(missing)}")
            if ptype and ptype not in STATUSES:
                errors.append(f"{p.rel}: unknown type '{ptype}'")
            elif ptype:
                if p.meta.get("status") not in STATUSES[ptype]:
                    errors.append(f"{p.rel}: status '{p.meta.get('status')}' invalid for type {ptype}")
                for key in REQUIRED_BY_TYPE.get(ptype, set()) - p.meta.keys():
                    errors.append(f"{p.rel}: {ptype} page missing '{key}'")
            raw = p.meta.get("raw", [])
            for r in raw if isinstance(raw, list) else [raw]:
                if r and not (ROOT / r).exists():
                    errors.append(f"{p.rel}: raw source not found: {r}")

        for target, resolved in w.links(p):
            if resolved is None or not resolved.exists():
                errors.append(f"{p.rel}: broken link -> {target}")
                continue
            try:
                rel = resolved.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if rel in inbound and rel != p.rel:
                inbound[rel] += 1
                if name == "index.md":
                    index_targets.add(rel)

        deps = p.meta.get("depends_on", [])
        deps = deps if isinstance(deps, list) else [deps]
        for ref in set(ID_RE.findall(p.body)) | set(deps):
            if not ID_RE.fullmatch(ref):
                continue
            if ref not in known:
                errors.append(f"{p.rel}: unknown ID {ref}")
                continue
            home = w.id_home(ref)
            if home and home != p.rel and name != "index.md":
                inbound[home] += 1
        for d in deps:
            if d.startswith("F-"):
                state = w.fact_state(d)
                if state in {"refuted", "stale"}:
                    warnings.append(f"{p.rel}: depends on {state} fact {d}: re-verify or revise")

    for e in w.entries.values():
        f = e.fields
        if e.id.startswith("F-"):
            if f.get("status") not in FACT_STATUSES:
                errors.append(f"{e.page}: {e.id} has invalid status '{f.get('status')}'")
            for key in ("scope", "evidence"):
                if key not in f:
                    errors.append(f"{e.page}: {e.id} missing '{key}'")
            if w.fact_state(e.id) == "stale":
                warnings.append(f"{e.page}: {e.id} is stale (scope != stack), re-verify")
        elif e.id.startswith("R-"):
            for key in ("likelihood", "impact", "mitigation", "owner"):
                if key not in f:
                    errors.append(f"{e.page}: {e.id} missing '{key}'")
        elif e.id.startswith("Q-"):
            for key in ("blocks", "default"):
                if key not in f:
                    errors.append(f"{e.page}: {e.id} missing '{key}'")

    for rel, count in inbound.items():
        name = Path(rel).name
        if name in HUBS_EXEMPT_FROM_ORPHAN:
            continue
        if rel not in index_targets:
            errors.append(f"{rel}: not listed in wiki/index.md")
        if count - (1 if rel in index_targets else 0) == 0:
            warnings.append(f"{rel}: orphan (only the index links here)")

    now = w.by_rel.get("wiki/now.md")
    if now and len(now.body.splitlines()) > 80:
        warnings.append("wiki/now.md exceeds 80 lines, compress it")
    log = w.by_rel.get("wiki/log.md")
    if log:
        for line in log.body.splitlines():
            if line.startswith("## ") and not LOG_ENTRY_RE.match(line):
                errors.append(f"wiki/log.md: malformed entry heading: {line}")

    agents = ROOT / "AGENTS.md"
    if agents.exists():
        a = Page(agents, {}, agents.read_text(encoding="utf-8"))
        for target, resolved in w.links(a):
            if resolved is None or not resolved.exists():
                errors.append(f"AGENTS.md: broken link -> {target}")

    for line in errors:
        print(f"ERROR  {line}")
    for line in warnings:
        print(f"WARN   {line}")
    print(f"\n{len(w.pages)} pages, {len(w.entries)} register entries, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


def status(w: Wiki) -> int:
    roadmap = w.by_rel.get("wiki/plan/roadmap.md")
    print("GATES")
    if roadmap:
        for line in roadmap.body.splitlines():
            m = re.match(r"^\| \*\*(G\d [^*]+)\*\* \|.*\| ([a-z]+) \|$", line)
            if m:
                print(f"  {m.group(1):<20} {m.group(2)}")

    print("\nSPIKES")
    for p in sorted((p for p in w.pages if p.meta.get("type") == "spike"), key=lambda p: p.meta["id"]):
        print(f"  {p.meta['id']:<5} {p.meta.get('status', '?'):<8} {p.meta.get('gate', ''):<4} {p.meta.get('title', '')}")

    print("\nOPEN QUESTIONS")
    for e in w.entries.values():
        if e.id.startswith("Q-") and not e.fields.get("answer"):
            blocks = e.fields.get("blocks", [])
            print(f"  {e.id} {e.title}  [blocks: {', '.join(blocks) if isinstance(blocks, list) else blocks}]")

    print("\nTOP RISKS")
    for e in w.entries.values():
        if e.id.startswith("R-"):
            lk, im = e.fields.get("likelihood"), e.fields.get("impact")
            if im == "critical" or (lk == "high" and im == "high"):
                print(f"  {e.id} [{lk}/{im}] {e.title}")

    print("\nFACT LADDER")
    counts = {s: 0 for s in FACT_STATUSES + ["stale"]}
    for e in w.entries.values():
        if e.id.startswith("F-"):
            counts[w.fact_state(e.id)] = counts.get(w.fact_state(e.id), 0) + 1
    print("  " + "  ".join(f"{k}={v}" for k, v in counts.items()))

    print("\nPAGES RESTING ON UNVERIFIED FACTS")
    for p in w.pages:
        deps = p.meta.get("depends_on", [])
        weak = [d for d in (deps if isinstance(deps, list) else []) if d.startswith("F-") and w.fact_state(d) in {"hypothesis", "claimed", "stale", "refuted"}]
        if weak:
            print(f"  {p.rel}: {', '.join(f'{d}({w.fact_state(d)})' for d in weak)}")

    decisions = [p for p in w.pages if p.meta.get("type") == "decision"]
    by = {}
    for d in decisions:
        by[d.meta.get("status")] = by.get(d.meta.get("status"), 0) + 1
    print("\nDECISIONS  " + "  ".join(f"{k}={v}" for k, v in by.items()))
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "lint"
    w = Wiki()
    if cmd == "lint":
        return lint(w)
    if cmd == "status":
        return status(w)
    print("usage: python tools/wiki.py [lint|status]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
