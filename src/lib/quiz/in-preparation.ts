import type { QuizFigure, QuizQuestion } from "./types";

/**
 * Quizzes for the three timelines still in preparation.
 *
 * These have no sources gathered yet, so a reader is matched to a named
 * theological *position* rather than to a person: the positions below are
 * standard descriptive categories, and nothing here attributes a view to any
 * individual ahead of the research. When each timeline's sources land, its
 * figures become the speakers on it, the way the eternal-increase quiz works.
 *
 * The options are written to describe rather than to commend. A reader should
 * be able to find their own view stated in terms they would accept.
 */

const FAMILY = "/family-proclamation-timeline";
const BAPTISM = "/baptism-timeline";
const SACRAMENT = "/sacrament-timeline";

export const FAMILY_QUESTIONS: QuizQuestion[] = [
  {
    id: "fam-gender",
    timeline: FAMILY,
    short: "Gender and eternity",
    prompt: "Is gender an eternal characteristic?",
    options: [
      {
        id: "essential",
        label: "Yes — an essential characteristic of premortal, mortal, and eternal identity",
      },
      {
        id: "eternal-unelaborated",
        label: "Eternal in some sense, though what it amounts to has never been spelled out",
      },
      {
        id: "mortal",
        label: "Sex and gender as we experience them belong to mortal life",
      },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
  {
    id: "fam-form",
    timeline: FAMILY,
    short: "Family form and exaltation",
    prompt: "What does exaltation require of the form a family takes?",
    options: [
      {
        id: "sealed-marriage",
        label: "The sealing of a man and a woman by priesthood authority",
      },
      {
        id: "ordinarily",
        label: "Ordinarily that — but I would leave room for what has not been explained",
      },
      {
        id: "covenant-first",
        label: "Covenant faithfulness is the thing; family form is not what decides it",
      },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
  {
    id: "fam-status",
    timeline: FAMILY,
    short: "Status of the Proclamation",
    prompt: "What kind of document is “The Family: A Proclamation to the World”?",
    options: [
      { id: "revelation", label: "A revelation, and binding doctrine" },
      {
        id: "inspired-counsel",
        label: "Inspired counsel that carries real weight without being canonized",
      },
      {
        id: "statement",
        label: "A statement of the Church's position at the time it was issued",
      },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
  {
    id: "fam-change",
    timeline: FAMILY,
    short: "Whether teaching develops",
    prompt:
      "On questions about same-sex relationships and family, do you expect the Church's teaching to develop?",
    options: [
      {
        id: "fixed",
        label: "No — this is a doctrinal boundary rather than a policy",
      },
      {
        id: "practice-may-soften",
        label: "The doctrine stands, but practice and pastoral approach can keep changing",
      },
      {
        id: "development",
        label: "Yes — I expect development here, as on other questions historically",
      },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
];

export const FAMILY_FIGURES: QuizFigure[] = [
  {
    id: "fam-essentialist",
    timeline: FAMILY,
    kind: "position",
    name: "The Proclamation as revelation",
    qualifier: "Essentialist reading",
    blurb:
      "Gender is an eternal essence, the sealed marriage of a man and a woman is the form exaltation takes, and the document is revelation rather than policy.",
    answers: {
      "fam-gender": "essential",
      "fam-form": "sealed-marriage",
      "fam-status": "revelation",
      "fam-change": "fixed",
    },
  },
  {
    id: "fam-reticent",
    timeline: FAMILY,
    kind: "position",
    name: "Ordinarily, but not absolutely",
    qualifier: "Reticent reading",
    blurb:
      "The pattern is affirmed and the exceptions are left to God: binding counsel held alongside an admission that much about the next life has not been explained.",
    answers: {
      "fam-gender": "eternal-unelaborated",
      "fam-form": "ordinarily",
      "fam-status": "inspired-counsel",
      "fam-change": "practice-may-soften",
    },
  },
  {
    id: "fam-developmental",
    timeline: FAMILY,
    kind: "position",
    name: "A developmental reading",
    qualifier: "Historically-minded",
    blurb:
      "Teaching on the family is read as it developed in time, so a statement is understood in its moment and further development is expected rather than ruled out.",
    answers: {
      "fam-gender": "mortal",
      "fam-form": "covenant-first",
      "fam-status": "statement",
      "fam-change": "development",
    },
  },
];

export const BAPTISM_QUESTIONS: QuizQuestion[] = [
  {
    id: "bap-effect",
    timeline: BAPTISM,
    short: "What baptism does",
    prompt: "What does baptism actually accomplish?",
    options: [
      {
        id: "regeneration",
        label: "It works the new birth and the remission of sins",
        note: "The washing effects what it signifies.",
      },
      {
        id: "covenant",
        label: "It is the covenant by which a person enters the household of God",
      },
      {
        id: "symbol",
        label: "It is an outward sign of a change already worked inwardly",
      },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
  {
    id: "bap-necessity",
    timeline: BAPTISM,
    short: "Whether it is required",
    prompt: "Is baptism necessary for salvation?",
    options: [
      { id: "necessary", label: "Necessary, without exception for the accountable" },
      {
        id: "ordinarily",
        label: "Ordinarily necessary — God provides for those who never had the chance",
      },
      { id: "obedience", label: "Not a condition of salvation; it is obedience and witness" },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
  {
    id: "bap-subjects",
    timeline: BAPTISM,
    short: "Who may be baptized",
    prompt: "Who is a fit subject for baptism?",
    options: [
      {
        id: "accountable",
        label: "Those old enough to repent and choose it",
      },
      {
        id: "infants",
        label: "Infants too — the covenant reaches the household, not only the adult",
      },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
  {
    id: "bap-validity",
    timeline: BAPTISM,
    short: "Whose baptism counts",
    prompt: "Whose baptism is valid?",
    options: [
      {
        id: "authority",
        label: "Only one performed by someone holding authority to perform it",
      },
      {
        id: "trinitarian",
        label: "Any baptism in the name of the Father, the Son, and the Holy Ghost",
      },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
];

export const BAPTISM_FIGURES: QuizFigure[] = [
  {
    id: "bap-regenerationist",
    timeline: BAPTISM,
    kind: "position",
    name: "Baptismal regeneration",
    qualifier: "Sacramental",
    blurb:
      "The water does something: the ordinance effects the new birth rather than picturing it, and the covenant reaches the whole household, infants included.",
    answers: {
      "bap-effect": "regeneration",
      "bap-necessity": "necessary",
      "bap-subjects": "infants",
      "bap-validity": "trinitarian",
    },
  },
  {
    id: "bap-covenantal",
    timeline: BAPTISM,
    kind: "position",
    name: "Covenant entry by authority",
    qualifier: "Restorationist",
    blurb:
      "Baptism is the gate into covenant, required of the accountable and valid only when performed by authority — with provision made for those who never had the opportunity.",
    answers: {
      "bap-effect": "covenant",
      "bap-necessity": "necessary",
      "bap-subjects": "accountable",
      "bap-validity": "authority",
    },
  },
  {
    id: "bap-symbolic",
    timeline: BAPTISM,
    kind: "position",
    name: "An outward sign",
    qualifier: "Symbolic",
    blurb:
      "The change comes first and the baptism testifies to it: a believer's ordinance, meaningful as obedience and witness rather than as a cause of anything.",
    answers: {
      "bap-effect": "symbol",
      "bap-necessity": "obedience",
      "bap-subjects": "accountable",
      "bap-validity": "trinitarian",
    },
  },
];

export const SACRAMENT_QUESTIONS: QuizQuestion[] = [
  {
    id: "sac-presence",
    timeline: SACRAMENT,
    short: "The emblems",
    prompt: "What are the bread and the water — or the bread and the wine?",
    options: [
      {
        id: "real-presence",
        label: "Christ is truly present in them",
      },
      {
        id: "spiritual",
        label: "Christ is really received, but spiritually and by faith",
      },
      {
        id: "memorial",
        label: "Bread and water; the whole meaning is remembrance",
      },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
  {
    id: "sac-liturgy",
    timeline: SACRAMENT,
    short: "Liturgical register",
    prompt: "How should the rite be conducted?",
    options: [
      {
        id: "high",
        label: "With ceremony — set words, vested ministers, a formal rite",
      },
      {
        id: "middle",
        label: "With some fixed form, kept simple",
      },
      {
        id: "low",
        label: "As plainly as possible — a set prayer and nothing added",
      },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
  {
    id: "sac-effect",
    timeline: SACRAMENT,
    short: "What partaking does",
    prompt: "What happens to the person who partakes?",
    options: [
      { id: "grace", label: "Grace is conveyed through the ordinance itself" },
      { id: "covenant", label: "Covenants already made are renewed" },
      { id: "remembrance", label: "Christ is called to mind and the will is stirred" },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
  {
    id: "sac-table",
    timeline: SACRAMENT,
    short: "Who may partake",
    prompt: "Who may administer and receive it?",
    options: [
      {
        id: "authority",
        label: "Administered only by authority; received by those in good standing",
      },
      { id: "open", label: "Open to any believer who comes in good conscience" },
      { id: "unsure", label: "I do not have a settled view" },
    ],
  },
];

export const SACRAMENT_FIGURES: QuizFigure[] = [
  {
    id: "sac-high",
    timeline: SACRAMENT,
    kind: "position",
    name: "High sacramentalism",
    qualifier: "Real presence",
    blurb:
      "The rite is the thing: Christ truly present, grace conveyed in the act, and a ceremony whose form carries the meaning rather than getting in its way.",
    answers: {
      "sac-presence": "real-presence",
      "sac-liturgy": "high",
      "sac-effect": "grace",
      "sac-table": "authority",
    },
  },
  {
    id: "sac-spiritual",
    timeline: SACRAMENT,
    kind: "position",
    name: "Spiritual presence",
    qualifier: "Received by faith",
    blurb:
      "Something real is received and it is received by faith — a middle way that keeps the grace without locating it in the elements themselves.",
    answers: {
      "sac-presence": "spiritual",
      "sac-liturgy": "middle",
      "sac-effect": "grace",
      "sac-table": "open",
    },
  },
  {
    id: "sac-covenant",
    timeline: SACRAMENT,
    kind: "position",
    name: "Covenant renewal, plainly done",
    qualifier: "Low liturgy",
    blurb:
      "A set prayer, plain emblems, no ceremony added — and the weight carried by the covenant being renewed rather than by anything happening to the bread.",
    answers: {
      "sac-presence": "memorial",
      "sac-liturgy": "low",
      "sac-effect": "covenant",
      "sac-table": "authority",
    },
  },
  {
    id: "sac-memorial",
    timeline: SACRAMENT,
    kind: "position",
    name: "Memorial",
    qualifier: "Remembrance",
    blurb:
      "Do this in remembrance: the ordinance works on the memory and the will, and its power is what it calls to mind rather than what it confers.",
    answers: {
      "sac-presence": "memorial",
      "sac-liturgy": "low",
      "sac-effect": "remembrance",
      "sac-table": "open",
    },
  },
];
