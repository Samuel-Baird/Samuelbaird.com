"""Build knowledge/learning/books/<slug>.toc.json (chapter -> pdf/printed start page).

usage: python -I scripts/kb_toc.py
Chapter titles and printed start pages are transcribed by hand from each book's
printed Contents (below). The PDF start page is then found by locating the
chapter title near the top of a page in the local text cache, searching forward
from the end of the front matter. Only refs are stored, never book text.
A wrong match shows up as an inconsistent (pdf - printed) offset in the output.
"""
import json, re, pathlib, sys, collections

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent / "knowledge"

# slug -> (first pdf page to search, [(chapter id, title, printed start page)])
SPECS = {
    "chance": (14, [
        (1, "Introduction: Learning to Change", 1), (2, "The Study of Learning and Behavior", 33),
        (3, "Pavlovian Conditioning", 55), (4, "Pavlovian Applications", 97),
        (5, "Operant Learning: Reinforcement", 129), (6, "Reinforcement: Beyond Habit", 172),
        (7, "Schedules of Reinforcement", 197), (8, "Operant Learning: Punishment", 236),
        (9, "Operant Applications", 261), (10, "Observational Learning", 287),
        (11, "Generalization, Discrimination, and Stimulus Control", 324), (12, "Forgetting", 357),
        (13, "The Limits of Learning", 391),
        ("Glossary", "Glossary", 412), ("References", "References", 420)]),
    "olson-ramirez": (14, [
        (1, "What Is Learning?", 3), (2, "Approaches to the Study of Learning", 15),
        (3, "Early Notions About Learning", 31), (4, "Edward Lee Thorndike", 57),
        (5, "Burrhus Frederic Skinner", 81), (6, "Clark Leonard Hull", 127),
        (7, "Ivan Petrovich Pavlov", 165), (8, "Edwin Ray Guthrie", 211),
        (9, "William Kaye Estes", 237), (10, "Gestalt Theory", 265), (11, "Jean Piaget", 295),
        (12, "Edward Chace Tolman", 315), (13, "Albert Bandura", 343),
        (14, "Donald Olding Hebb", 377), (15, "Robert C. Bolles and Evolutionary Psychology", 415),
        (16, "A Final Word", 449),
        ("Glossary", "Glossary", 459), ("References", "References", 490)]),
    "mazur-odum": (16, [
        (1, "History, Background, and Basic Concepts", 1), (2, "Innate Behavior Patterns and Habituation", 28),
        (3, "Basic Principles of Classical Conditioning", 54), (4, "Theories and Research on Classical Conditioning", 79),
        (5, "Basic Principles of Operant Conditioning", 106), (6, "Reinforcement Schedules: Experimental Analyses", 135),
        (7, "Avoidance and Punishment", 163), (8, "Theories and Research on Operant Conditioning", 191),
        (9, "Stimulus Control and Concept Learning", 221), (10, "Comparative Cognition", 249),
        (11, "Observational Learning and Motor Skills", 279), (12, "Choice", 313),
        ("Glossary", "Glossary", 342)]),
    "gluck": (22, [
        (1, "The Psychology of Learning and Memory", 1), (2, "The Neuroscience of Learning and Memory", 35),
        (3, "Habituation, Sensitization, and Familiarization", 71), (4, "Classical Conditioning", 115),
        (5, "Operant Conditioning", 167), (6, "Generalization, Discrimination Learning, and Concept Formation", 213),
        (7, "Episodic and Semantic Memory", 267), (8, "Skill Memory", 311),
        (9, "Working Memory and Cognitive Control", 351), (10, "Emotional Influences on Learning and Memory", 395),
        (11, "Social Learning and Memory", 439), (12, "Development and Aging", 473)]),
    "domjan-delamater": (16, [
        (1, "Basic Concepts and Definitions", 3), (2, "The Substrate for Learning: Unconditioned Behavior", 17),
        (3, "Habituation and Sensitization", 31), (4, "Pavlovian Conditioning: Basic Concepts", 45),
        (5, "Stimulus Relations in Pavlovian Conditioning", 63), (6, "Pavlovian Conditioning Mechanisms and Theories", 83),
        (7, "Instrumental or Operant Conditioning", 101), (8, "Schedules of Reinforcement", 121),
        (9, "Theories of Reinforcement", 139), (10, "Extinction of Conditioned Behavior", 155),
        (11, "Punishment", 173), (12, "Avoidance Learning", 189), (13, "Stimulus Control of Behavior", 207),
        (14, "Memory Mechanisms", 225),
        ("Glossary", "Glossary", 245), ("References", "References", 261)]),
    "dehouwer-hughes": (18, [
        (0, "Introduction: What Is Learning and How Can We Study It", 1),
        (1, "Effects of Regularities in the Presence of a Single Stimulus", 37),
        (2, "Classical Conditioning: Effects of Regularities in the Presence of Multiple Stimuli", 57),
        (3, "Operant Conditioning: Effects of Regularities in the Presence of Stimuli and Behavior", 117),
        (4, "Complex Forms of Learning: Joint Effects of Multiple Regularities", 181),
        (5, "Applied Learning Psychology: Using the Principles of Learning to Improve", 199),
        ("Glossary", "Glossary", 247), ("Notes", "Notes", 259), ("References", "References", 267)]),
}

# De Houwer & Hughes chapter openers start with a learning-objectives box, so the title
# is not on the page; offset checked by hand (printed page 2 is pdf 17, openers are "After reading this chapter").
OFFSET_OVERRIDE = {"dehouwer-hughes": 15, "olson-ramirez": 17}

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

out_dir = ROOT / "learning" / "books"
out_dir.mkdir(parents=True, exist_ok=True)
for slug, (min_pdf, chapters) in SPECS.items():
    cache = ROOT / "cache" / f"{slug}.pages.jsonl"
    if not cache.exists():
        print(slug, "cache missing, skipped")
        continue
    pages = {}
    for l in cache.open(encoding="utf-8"):
        p = json.loads(l)
        pages[p["pdf"]] = p
    # 1) loose pass: first page after the front matter whose top shows the title -> offset votes
    cursor, votes = min_pdf, collections.Counter()
    for ch, title, printed in chapters:
        key = norm(title)[:40]
        for n in sorted(pages):
            if n >= cursor and key in norm(pages[n]["text"][:700]):
                votes[n - printed] += 1
                cursor = n + 1
                break
    mode = OFFSET_OVERRIDE.get(slug) or votes.most_common(1)[0][0]
    # 2) strict pass: the page at printed + mode (+-2) must show the title near its top
    result, bad = [], []
    for ch, title, printed in chapters:
        key = norm(title)[:40]
        found = None
        for d in (0,):
            n = printed + mode + d
            if n in pages and key in norm(pages[n]["text"][:900]):
                found = n
                break
        if found is None:
            bad.append(ch)
        result.append({"ch": ch, "title": title, "printed": printed, "pdf": found if found else printed + mode})
    json.dump({"slug": slug, "offset": mode, "chapters": result}, open(out_dir / f"{slug}.toc.json", "w", encoding="utf-8"), indent=1)
    print(slug, "offset", mode, "votes", votes.most_common(3), "| opener title not at top of expected page (many openers show an epigraph or objectives box first; spot-check by hand):", bad)
