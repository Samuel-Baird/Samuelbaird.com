/**
 * The quiz's optional demographic intake: option lists, types, and
 * validation. Isomorphic on purpose - the intake screen renders these
 * client-side with zero network (the quiz stays fully playable offline
 * and anonymously), and the server actions validate against the same
 * lists before anything is written.
 *
 * TRADITION_OPTIONS mirrors the `traditions` table seeded in migration
 * 0046 - that table exists for FK integrity and admin joins; this constant
 * is the runtime source. Change both together (a data change, per the
 * original spec: swapping in the full Pew taxonomy later must not be a
 * schema change).
 */

export type TraditionOption = {
  slug: string;
  label: string;
  /**
   * The quiz-matchable tradition this slug corresponds to, or null.
   * Powers the admin crosstab's self-reported-vs-matched agreement
   * diagonal.
   */
  pewCategory: "Evangelical" | "Black Protestant" | "Mainline" | "Roman Catholic" | null;
};

export const TRADITION_OPTIONS: TraditionOption[] = [
  { slug: "evangelical_protestant", label: "Evangelical Protestant", pewCategory: "Evangelical" },
  { slug: "mainline_protestant", label: "Mainline Protestant", pewCategory: "Mainline" },
  { slug: "historically_black_protestant", label: "Historically Black Protestant", pewCategory: "Black Protestant" },
  { slug: "roman_catholic", label: "Roman Catholic", pewCategory: "Roman Catholic" },
  { slug: "latter_day_saint", label: "Latter-day Saint", pewCategory: null },
  { slug: "orthodox_christian", label: "Orthodox Christian", pewCategory: null },
  { slug: "other_christian", label: "Other Christian", pewCategory: null },
  { slug: "jewish", label: "Jewish", pewCategory: null },
  { slug: "muslim", label: "Muslim", pewCategory: null },
  { slug: "other_religion", label: "Another religion", pewCategory: null },
  { slug: "atheist_agnostic", label: "Atheist / agnostic", pewCategory: null },
  { slug: "nothing_in_particular", label: "Nothing in particular", pewCategory: null },
  { slug: "prefer_not_to_say", label: "Prefer not to say", pewCategory: null },
];

export const GENDER_OPTIONS = [
  { slug: "male", label: "Male" },
  { slug: "female", label: "Female" },
  { slug: "other", label: "Other" },
  { slug: "prefer_not_to_say", label: "Prefer not to say" },
] as const;

/** All fields optional - every part of the intake is skippable. */
export type Demographics = {
  age: number | null;
  gender: string | null;
  traditionSlug: string | null;
};

export const EMPTY_DEMOGRAPHICS: Demographics = {
  age: null,
  gender: null,
  traditionSlug: null,
};

const TRADITION_SLUGS = new Set(TRADITION_OPTIONS.map((t) => t.slug));
const GENDER_SLUGS = new Set<string>(GENDER_OPTIONS.map((g) => g.slug));

/**
 * Coerces untrusted demographic input to a valid Demographics: an
 * out-of-range age or unknown slug becomes null rather than an error,
 * since every field is optional anyway - garbage in, absence out.
 */
export function validateDemographics(d: Partial<Demographics> | null | undefined): Demographics {
  const age =
    typeof d?.age === "number" && Number.isInteger(d.age) && d.age >= 1 && d.age <= 110
      ? d.age
      : null;
  const gender = typeof d?.gender === "string" && GENDER_SLUGS.has(d.gender) ? d.gender : null;
  const traditionSlug =
    typeof d?.traditionSlug === "string" && TRADITION_SLUGS.has(d.traditionSlug)
      ? d.traditionSlug
      : null;
  return { age, gender, traditionSlug };
}

/**
 * The disclosure line the original spec requires above the intake.
 * Religious affiliation is special-category personal data; saying plainly
 * what happens to it costs one sentence.
 */
export const DEMOGRAPHICS_DISCLOSURE =
  "Your answers are stored anonymously and used for aggregate research. You can skip this question.";
