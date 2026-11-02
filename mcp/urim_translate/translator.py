"""Translation engine: TM lookup -> glossary match -> route (MT / LLM) -> validate -> selective retry."""
import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field

from . import config, segment
from .backends import make_backends
from .glossary import Glossary
from .store import Store

LONG_SEGMENT = 900        # chars; longer segments skip MT and go straight to the LLM


@dataclass
class Seg:
    text: str
    masked: str = ""
    ph: dict = field(default_factory=dict)
    matches: list = field(default_factory=list)
    draft: str = ""
    target: str = ""
    origin: str = ""
    flags: list = field(default_factory=list)


def length_ok(src: str, tgt: str) -> bool:
    if len(src) < 40:
        return True
    return 0.45 <= len(tgt) / max(1, len(src)) <= 2.6


class Translator:
    def __init__(self, store: Store = None, backends=None):
        self.store = store or Store()
        self.backends = backends if backends is not None else make_backends()
        self._gloss = {}

    # ---- plumbing
    def glossary(self, lang):
        g = self._gloss.get(lang)
        if g is None:
            g = self._gloss[lang] = Glossary(lang, self.store)
        return g

    def reload_glossary(self, lang):
        self._gloss.pop(lang, None)

    def _first(self, kind):
        for b in self.backends:
            if b.kind == kind and b.available()[0]:
                return b
        return None

    def status(self):
        out = []
        for b in self.backends:
            ok, detail = b.available()
            out.append({"backend": b.name, "kind": b.kind, "available": ok, "detail": detail})
        return out

    # ---- validation
    def problems(self, seg: Seg, target: str, g: Glossary):
        probs = []
        if not target.strip():
            return ["empty output"]
        if not segment.placeholders_ok(target, seg.ph):
            probs.append("a ⟦n⟧ placeholder was lost, duplicated or altered; keep each one exactly once")
        if segment.numbers(seg.masked) != segment.numbers(target):
            probs.append("numbers differ from the source")
        if not length_ok(seg.masked, target):
            probs.append("length is implausible compared with the source (omission or addition)")
        for e in g.missing(seg.matches, target):
            probs.append(f'"{e.en[0]}" must be rendered as "{e.preferred}"'
                         + (f' (or: {", ".join(v["term"] for v in e.variants)})' if e.variants else ""))
        return probs

    # ---- main entry
    def translate_segments(self, texts, lang):
        """Translate segment strings. Returns [Seg] in order; seg.target already has placeholders restored."""
        g = self.glossary(lang)
        segs = [Seg(t) for t in texts]
        todo = []
        for s in segs:
            s.masked, s.ph = segment.protect(s.text, lang)
            s.matches = g.match(s.masked)
            hit = self.store.tm_get(lang, s.text)
            if hit:
                tgt, origin = hit
                if origin == "church" or not g.missing(s.matches, tgt):
                    s.target, s.origin = tgt, "tm:" + origin
                    continue
            todo.append(s)

        mt, llm = self._first("mt"), self._first("llm")
        need_llm, drafts = [], []
        for s in todo:
            if llm and (len(s.masked) > LONG_SEGMENT or not mt):
                need_llm.append(s)
            elif mt:
                drafts.append(s)
            else:
                s.flags.append("no backend available")
        if drafts:
            outs = mt.translate([s.masked for s in drafts], lang)
            for s, o in zip(drafts, outs):
                s.draft, s.origin = o, mt.name
        redo = []
        for s in drafts:
            probs = self.problems(s, s.draft, g)
            if not probs:
                s.target = s.draft
            elif llm:
                s.flags = probs
                redo.append(s)
            else:
                s.target = s.draft
                s.flags = ["needs_review"] + probs
        if need_llm:
            self._llm_translate(need_llm, lang, g)
        if redo:
            self._llm_postedit(redo, lang, g)

        for s in segs:
            s.target = segment.restore(s.target, s.ph) if s.target else s.text
            if s.origin and not s.origin.startswith("tm:") and not s.flags:
                self.store.tm_put(lang, s.text, s.target, s.origin, commit=False)
        self.store.db.commit()
        return segs

    # ---- LLM paths (batched)
    def _batches(self, items):
        batch, chars = [], 0
        for it in items:
            size = len(it.masked)
            if batch and (len(batch) >= config.LLM_BATCH_SEGMENTS or chars + size > config.LLM_BATCH_CHARS):
                yield batch
                batch, chars = [], 0
            batch.append(it)
            chars += size
        if batch:
            yield batch

    def _terms_for(self, batch):
        seen, out = set(), []
        for s in batch:
            for m in s.matches:
                if m.entry.id not in seen:
                    seen.add(m.entry.id)
                    out.append(m.entry.brief())
        return out

    def _llm_translate(self, items, lang, g):
        llm = self._first("llm")
        for batch in self._batches(items):
            try:
                outs = llm.translate([s.masked for s in batch], lang, terms=self._terms_for(batch))
            except Exception as e:
                for s in batch:
                    s.flags = [f"ollama error: {type(e).__name__}"]
                continue
            retry = []
            for s, o in zip(batch, outs):
                probs = self.problems(s, o, g)
                s.draft, s.origin = o, llm.name
                if not probs:
                    s.target = o
                else:
                    s.flags = probs
                    retry.append(s)
            if retry:
                self._llm_postedit(retry, lang, g)

    def _llm_postedit(self, items, lang, g):
        """One selective retry with explicit feedback; keep the best output and flag if still failing."""
        llm = self._first("llm")
        for batch in self._batches(items):
            payload = [{"src": s.masked, "draft": s.draft, "terms": [m.entry.brief() for m in s.matches],
                        "problems": s.flags} for s in batch]
            try:
                outs = llm.postedit(payload, lang)
            except Exception as e:
                for s in batch:
                    s.target = s.draft
                    s.flags = ["needs_review", f"ollama error: {type(e).__name__}"] + s.flags
                continue
            for s, o in zip(batch, outs):
                probs = self.problems(s, o, g)
                if not probs:
                    s.target, s.flags = o, []
                    s.origin = (s.origin or "mt") + "+" + llm.name
                else:
                    s.target = o if len(probs) < len(s.flags) else s.draft
                    s.flags = ["needs_review"] + probs

    # ---- documents
    def translate_document(self, text: str, lang: str):
        blocks = segment.split_document(text)
        segs_idx = [b for b in blocks if b.is_seg]
        results = self.translate_segments([b.text for b in segs_idx], lang)
        for b, r in zip(segs_idx, results):
            b.target, b.meta = r.target, {"origin": r.origin or "none", "flags": r.flags}
        return blocks, results

    def doc_id(self, name: str, lang: str, text: str) -> str:
        return hashlib.sha1(f"{name}|{lang}|{self.glossary(lang).version}|{text[:5000]}".encode()).hexdigest()[:10]

    def save_job(self, doc_id, lang, src_path, blocks, results, out_path=None):
        job_dir = config.HOME / "jobs" / doc_id
        job_dir.mkdir(parents=True, exist_ok=True)
        out = job_dir / f"output.{lang}.md"
        out.write_text(segment.join_blocks(blocks), encoding="utf-8")
        report = [{"i": i, "origin": r.origin or "none", "flags": r.flags, "src": r.text, "tgt": r.target}
                  for i, r in enumerate(results)]
        (job_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        final = out
        if out_path:
            from pathlib import Path
            final = Path(out_path)
            final.parent.mkdir(parents=True, exist_ok=True)
            final.write_text(out.read_text(encoding="utf-8"), encoding="utf-8")
        self.store.job_put(doc_id, lang, src_path, str(final), len(results))
        return final

    @staticmethod
    def summarize(results):
        origins = Counter((r.origin or "none").split("+")[0] for r in results)
        flagged = [i for i, r in enumerate(results) if r.flags]
        return {"segments": len(results), "origins": dict(origins), "needs_review": flagged}
