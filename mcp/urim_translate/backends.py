"""Pluggable translation backends. Add one by subclassing and registering in make_backends()."""
import json

import httpx

from . import config


class Backend:
    name = "base"
    kind = "mt"          # "mt" = fast draft translator, "llm" = terminology-aware post-editor

    def available(self) -> tuple[bool, str]:
        return False, "not implemented"

    def translate(self, texts, lang):
        """Plain translation of masked segments. Returns a list the same length as `texts`."""
        raise NotImplementedError


class ArgosBackend(Backend):
    name = "argos"

    def available(self):
        try:
            import argostranslate.translate as t
        except Exception as e:  # not installed
            return False, f"argostranslate not installed ({type(e).__name__})"
        langs = {l.code: l for l in t.get_installed_languages()}
        if "en" not in langs:
            return False, "no Argos packages installed (en->pt / en->es)"
        have = [t.to_lang.code for t in langs["en"].translations_from] if hasattr(langs["en"], "translations_from") else []
        if not have:
            return False, "no en->* Argos packages installed"
        return True, "installed targets: " + ", ".join(have)

    def translate(self, texts, lang):
        import argostranslate.translate as t
        return [t.translate(x, "en", config.ARGOS_CODE[lang]) for x in texts]


class LibreTranslateBackend(Backend):
    name = "libretranslate"

    def available(self):
        if not config.LIBRETRANSLATE_URL:
            return False, "libretranslate_url not set"
        try:
            httpx.get(config.LIBRETRANSLATE_URL.rstrip("/") + "/languages", timeout=3).raise_for_status()
            return True, config.LIBRETRANSLATE_URL
        except Exception as e:
            return False, f"unreachable ({type(e).__name__})"

    def translate(self, texts, lang):
        r = httpx.post(config.LIBRETRANSLATE_URL.rstrip("/") + "/translate", timeout=120,
                       json={"q": texts, "source": "en", "target": lang, "format": "text"})
        r.raise_for_status()
        out = r.json()["translatedText"]
        return out if isinstance(out, list) else [out]


class OllamaBackend(Backend):
    """Local LLM (default qwen3.5:4b). Used for terminology-sensitive work and post-editing."""
    name = "ollama"
    kind = "llm"

    def available(self):
        try:
            r = httpx.get(config.OLLAMA_URL + "/api/tags", timeout=3)
            r.raise_for_status()
            names = [m["name"] for m in r.json().get("models", [])]
            if not any(n == config.OLLAMA_MODEL or n.startswith(config.OLLAMA_MODEL.split(":")[0] + ":" + config.OLLAMA_MODEL.split(":")[-1])
                       for n in names):
                return False, f"model {config.OLLAMA_MODEL} not pulled (run: ollama pull {config.OLLAMA_MODEL})"
            return True, config.OLLAMA_MODEL
        except Exception as e:
            return False, f"ollama not reachable ({type(e).__name__})"

    def _chat(self, system, user, n):
        schema = {"type": "object", "properties": {"t": {"type": "array", "items": {"type": "string"},
                                                          "minItems": n, "maxItems": n}}, "required": ["t"]}
        r = httpx.post(config.OLLAMA_URL + "/api/chat", timeout=600, json={
            "model": config.OLLAMA_MODEL, "stream": False, "think": False, "format": schema,
            "options": {"temperature": 0.1},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
        r.raise_for_status()
        return json.loads(r.json()["message"]["content"])["t"]

    @staticmethod
    def _terms(terms):
        return "\n".join(f'- "{t["en"]}" -> "{t["use"]}"' + (f' (also acceptable: {", ".join(t["also"])})' if t.get("also") else "")
                         for t in terms)

    def _system(self, lang):
        return (f"You translate English Latter-day Saint texts into {config.UI_LANGS[lang]}. "
                "Use the required term renderings exactly (inflect for gender/number only). "
                "Keep every ⟦n⟧ token unchanged and in place. Do not add or drop content. "
                'Reply as JSON {"t": [...]} with one string per input, same order.')

    def translate(self, texts, lang, terms=None):
        """texts: masked segments; terms: [brief-dicts] relevant to the whole batch."""
        user = (("Required terms:\n" + self._terms(terms) + "\n\n") if terms else "") + \
            "Translate each item:\n" + json.dumps(texts, ensure_ascii=False)
        return self._chat(self._system(lang), user, len(texts))

    def postedit(self, items, lang):
        """items: [{"src", "draft", "terms", "problems"}]. Returns corrected translations."""
        payload = [{"src": i["src"], "draft": i["draft"], "problems": i["problems"]} for i in items]
        terms = {t["en"]: t for i in items for t in i["terms"]}
        user = ("Required terms:\n" + self._terms(list(terms.values())) + "\n\n"
                "Each item has an English source, a draft translation, and problems found in the draft. "
                "Return a corrected translation for each item that fixes the problems and keeps the rest of the draft "
                "where it is already correct.\n" + json.dumps(payload, ensure_ascii=False))
        return self._chat(self._system(lang), user, len(items))


def make_backends():
    reg = {"argos": ArgosBackend, "libretranslate": LibreTranslateBackend, "ollama": OllamaBackend}
    return [reg[n]() for n in config.BACKENDS if n in reg]
