import type { QuizFigure, QuizQuestion } from "./types";

/**
 * Quiz for /eternal-increase-timeline. The six questions are the six the
 * portrait hall reads each speaker against, put to the reader instead; the
 * figures' answers are the positions documented on that timeline, so a match
 * here is traceable to sources on the page below.
 */

const T = "/eternal-increase-timeline";

export const ETERNAL_INCREASE_QUESTIONS: QuizQuestion[] = [
  {
    id: "ei-father",
    timeline: T,
    short: "A Father above the Father",
    prompt: "Did God the Father himself have a Father?",
    options: [
      {
        id: "chain",
        label: "Yes — an endless line of Gods, with no first one",
        note: "Each God was once as we are, taught by the God before him.",
      },
      {
        id: "one-link",
        label: "He received what he has as Christ received it — but I would not go further back",
        note: "One link past the Son, and no claim about where the line ends.",
      },
      {
        id: "self-made",
        label: "No — he rose to godhood, but there was no God above him",
        note: "Godhood attained by his own exertions, not inherited from a Father.",
      },
      {
        id: "always-god",
        label: "No — he has always been God, from everlasting to everlasting",
      },
      {
        id: "not-revealed",
        label: "Little has been revealed, and I would not speculate",
      },
    ],
  },
  {
    id: "ei-mortal",
    timeline: T,
    short: "God once a man",
    prompt: "Was God the Father once a mortal man, living on an earth as we do?",
    options: [
      {
        id: "yes-mortal",
        label: "Yes — he lived a mortal life and died, as Christ did",
      },
      {
        id: "exalted-man",
        label: "He is an exalted, perfected Man — but I would not describe his past",
        note: "The title is affirmed; the biography is left alone.",
      },
      { id: "always-god", label: "No — he was never anything other than God" },
      { id: "not-revealed", label: "I do not know, and I do not think it has been revealed" },
    ],
  },
  {
    id: "ei-increase",
    timeline: T,
    short: "Endless posterity",
    prompt: "What is promised to the exalted by “a continuation of the seeds forever”?",
    options: [
      {
        id: "spirit-children",
        label: "Spirit children without end, and worlds to put them on",
      },
      {
        id: "seeds-unspecified",
        label: "An endless increase — though I would not say exactly of what",
        note: "The scriptural promise, held without filling in the mechanism.",
      },
      {
        id: "family-only",
        label: "Eternal life with the family you already have",
        note: "Increase read as the family relation continuing, not as new offspring.",
      },
      { id: "none", label: "Nothing of the kind — exaltation is not about posterity" },
    ],
  },
  {
    id: "ei-spirit-birth",
    timeline: T,
    short: "How spirits are made",
    prompt: "Where do our spirits come from?",
    options: [
      {
        id: "born",
        label: "Literally begotten and born to heavenly parents",
      },
      {
        id: "organized",
        label: "Organized from intelligence that was never created and cannot be",
        note: "We were always there in some form; God shaped rather than made us.",
      },
      {
        id: "both",
        label: "Both — begotten as spirits, from elements that always existed",
      },
      { id: "not-revealed", label: "The Lord has not explained this" },
    ],
  },
  {
    id: "ei-progression",
    timeline: T,
    short: "Whether God progresses",
    prompt: "Does God still progress?",
    options: [
      {
        id: "learns",
        label: "Yes — he is progressing eternally, and so are his children",
      },
      {
        id: "kingdoms-only",
        label: "Only in kingdoms and dominions — never in knowledge or power",
        note: "His creations multiply; his attributes are already complete.",
      },
      {
        id: "complete",
        label: "No — having attained godhood there is nothing left to gain",
      },
      { id: "not-revealed", label: "I have no position on this" },
    ],
  },
  {
    id: "ei-mother",
    timeline: T,
    short: "A Mother in Heaven",
    prompt: "Is there a Mother in Heaven, and what may be said about her?",
    options: [
      {
        id: "yes-central",
        label: "Yes, and she belongs in how we teach and talk about heaven",
      },
      {
        id: "yes-reticent",
        label: "Yes — but reverence means saying very little about her",
      },
      {
        id: "not-revealed",
        label: "I would not make a claim either way",
      },
    ],
  },
];

/**
 * Every position below is the one documented for that speaker on this
 * timeline; where a speaker never addressed a question, the key is omitted
 * rather than guessed, and scoring skips it.
 */
export const ETERNAL_INCREASE_FIGURES: QuizFigure[] = [
  {
    id: "joseph-smith",
    timeline: T,
    kind: "person",
    name: "Joseph Smith",
    qualifier: "1805–1844",
    blurb:
      "You reach the chain the way he did — by following an argument out to its end — while holding that intelligence itself was never made.",
    answers: {
      "ei-father": "chain",
      "ei-mortal": "yes-mortal",
      "ei-increase": "seeds-unspecified",
      "ei-spirit-birth": "organized",
      "ei-progression": "learns",
    },
  },
  {
    id: "brigham-young",
    timeline: T,
    kind: "person",
    name: "Brigham Young",
    qualifier: "1801–1877",
    blurb:
      "The boldest version of the doctrine: Gods without beginning, spirits literally born, and a God who is still going.",
    answers: {
      "ei-father": "chain",
      "ei-mortal": "yes-mortal",
      "ei-increase": "spirit-children",
      "ei-spirit-birth": "born",
      "ei-progression": "learns",
      "ei-mother": "yes-reticent",
    },
  },
  {
    id: "orson-pratt",
    timeline: T,
    kind: "person",
    name: "Orson Pratt",
    qualifier: "1811–1881",
    blurb:
      "A systematizer: the persons regress forever, but God — properly speaking — is complete knowledge, and complete knowledge cannot grow.",
    answers: {
      "ei-father": "chain",
      "ei-mortal": "yes-mortal",
      "ei-increase": "spirit-children",
      "ei-spirit-birth": "born",
      "ei-progression": "complete",
      "ei-mother": "yes-central",
    },
  },
  {
    id: "george-q-cannon",
    timeline: T,
    kind: "person",
    name: "George Q. Cannon",
    qualifier: "1827–1901",
    blurb:
      "Expansive about where we are going, careful about where God came from — and sure that posterity is the substance of glory.",
    answers: {
      "ei-father": "one-link",
      "ei-mortal": "exalted-man",
      "ei-increase": "spirit-children",
      "ei-spirit-birth": "born",
      "ei-mother": "yes-reticent",
    },
  },
  {
    id: "charles-w-penrose",
    timeline: T,
    kind: "person",
    name: "Charles W. Penrose",
    qualifier: "1832–1925",
    blurb:
      "A God who fought his way up from the depths by his own exertions — mortality behind him, but no genealogy above him.",
    answers: {
      "ei-father": "self-made",
      "ei-mortal": "yes-mortal",
      "ei-increase": "spirit-children",
      "ei-spirit-birth": "both",
      "ei-progression": "complete",
    },
  },
  {
    id: "orson-f-whitney",
    timeline: T,
    kind: "person",
    name: "Orson F. Whitney",
    qualifier: "1855–1931",
    blurb:
      "The poet: God found himself among intelligences that cannot be created, and a Heavenly Mother is argued for out in the open.",
    answers: {
      "ei-father": "self-made",
      "ei-mortal": "yes-mortal",
      "ei-increase": "seeds-unspecified",
      "ei-spirit-birth": "organized",
      "ei-mother": "yes-central",
    },
  },
  {
    id: "joseph-fielding-smith",
    timeline: T,
    kind: "person",
    name: "Joseph Fielding Smith",
    qualifier: "1876–1972",
    blurb:
      "Affirm the old cosmology, then police what may be inferred from it: a Father above the Father, but a God who never learns.",
    answers: {
      "ei-father": "chain",
      "ei-mortal": "yes-mortal",
      "ei-increase": "spirit-children",
      "ei-spirit-birth": "born",
      "ei-progression": "kingdoms-only",
      "ei-mother": "yes-central",
    },
  },
  {
    id: "spencer-w-kimball",
    timeline: T,
    kind: "person",
    name: "Spencer W. Kimball",
    qualifier: "1895–1985",
    blurb:
      "Godhood preached as destiny rather than argued as metaphysics — the promise is loud, the machinery is left alone.",
    answers: {
      "ei-father": "not-revealed",
      "ei-mortal": "yes-mortal",
      "ei-increase": "seeds-unspecified",
      "ei-spirit-birth": "born",
      "ei-progression": "not-revealed",
      "ei-mother": "yes-central",
    },
  },
  {
    id: "bruce-r-mcconkie",
    timeline: T,
    kind: "person",
    name: "Bruce R. McConkie",
    qualifier: "1915–1985",
    blurb:
      "The encyclopedist: the whole chain stated more literally than anyone — and a hard line against a God who could still be learning.",
    answers: {
      "ei-father": "chain",
      "ei-mortal": "exalted-man",
      "ei-increase": "spirit-children",
      "ei-spirit-birth": "born",
      "ei-progression": "kingdoms-only",
      "ei-mother": "yes-reticent",
    },
  },
  {
    id: "dallin-h-oaks",
    timeline: T,
    kind: "person",
    name: "Dallin H. Oaks",
    qualifier: "b. 1932",
    blurb:
      "The modern reticence: heavenly parents as the first premise, and a firm rule against teaching as doctrine what has not been revealed.",
    answers: {
      "ei-father": "not-revealed",
      "ei-mortal": "not-revealed",
      "ei-increase": "family-only",
      "ei-spirit-birth": "not-revealed",
      "ei-progression": "not-revealed",
      "ei-mother": "yes-reticent",
    },
  },
];
