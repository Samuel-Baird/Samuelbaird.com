/**
 * The quiz's optional demographic intake: option lists, types, and
 * validation. Isomorphic on purpose - the intake screen renders these
 * client-side with zero network (the quiz stays fully playable offline
 * and anonymously), and the server actions validate against the same
 * lists before anything is written.
 *
 * Every list here mirrors a variable in Pew Research Center's 2023-24
 * Religious Landscape Study, so answers collected on this site can be read
 * against Pew's national numbers with no recoding step in between. The
 * `rls` field on each option records which code it corresponds to. See
 * docs/datasets/pew-rls-2023-24/ for the source documents, the machine-
 * readable codebook, and the field-to-variable table.
 *
 *   Pew Research Center. 2025. "2023-24 Religious Landscape Study (RLS)
 *   Dataset." doi: 10.58094/3kwb-bf52.
 *
 * RELIGION_OPTIONS mirrors the `traditions` table seeded in migration 0046
 * and extended in 0047 - that table exists for FK integrity and admin
 * joins; this constant is the runtime source. Change both together (a data
 * change, per the original spec: swapping in the full Pew taxonomy was
 * never meant to be a schema change).
 */

/** The quiz's four matchable traditions - the scoring side of the crosstab. */
export type QuizTradition = "Evangelical" | "Black Protestant" | "Mainline" | "Roman Catholic";

/**
 * RELTRAD, the top of Pew's DENOM -> FAMILY -> RELTRAD hierarchy, used
 * here as the picker's option groups. Protestants get three groups rather
 * than one because that is the split RELTRAD itself makes.
 */
export type ReligionGroup =
  | "Evangelical Protestant"
  | "Mainline Protestant"
  | "Historically Black Protestant"
  | "Catholic"
  | "Other Christian"
  | "Non-Christian faiths"
  | "Religiously unaffiliated"
  | "No answer";

export const RELIGION_GROUPS: ReligionGroup[] = [
  "Evangelical Protestant",
  "Mainline Protestant",
  "Historically Black Protestant",
  "Catholic",
  "Other Christian",
  "Non-Christian faiths",
  "Religiously unaffiliated",
  "No answer",
];

export type ReligionOption = {
  slug: string;
  label: string;
  group: ReligionGroup;
  /**
   * The RLS `FAMILY` code this option corresponds to, or null where the
   * site's list has no Pew counterpart (only "Prefer not to say", which is
   * a refusal rather than Pew's 999 "no information" back-code).
   */
  rlsFamily: number | null;
  /**
   * The quiz-matchable tradition, or null. Powers the admin crosstab's
   * self-reported-vs-matched agreement diagonal. Derived from the group,
   * which is why every option in a Protestant or Catholic group has one.
   */
  quizTradition: QuizTradition | null;
  /**
   * Hidden from the picker but still resolvable for display. Set on slugs
   * that predate the RLS taxonomy and are still referenced by rows recorded
   * before the switch - a stored slug must never render as a raw string in
   * the admin views.
   */
  retired?: boolean;
};

/**
 * Pew's FAMILY variable, complete: RELTRAD with the denominational detail
 * for Protestants, the family detail for other faiths, and the atheist /
 * agnostic / nothing-in-particular split for the unaffiliated.
 *
 * FAMILY rather than DENOMREC2 (86 codes) because FAMILY is the finest
 * level a person can pick for themselves off a list - Pew reaches DENOMREC2
 * by branching questions plus a back-coding pass, which one dropdown can't
 * reproduce. Each Protestant family appears once per tradition, exactly as
 * FAMILY codes it, so "Baptist" under the evangelical group and "Baptist"
 * under the mainline group are different codes and different answers.
 *
 * Slugs are stable identifiers stored in the database; the labels are the
 * only part safe to reword.
 */
export const RELIGION_OPTIONS: ReligionOption[] = [
  // Evangelical Protestant tradition - FAMILY 1-18.
  ep("baptist_evangelical", "Baptist", 1),
  ep("methodist_evangelical", "Methodist", 2),
  ep("nondenominational_evangelical", "Nondenominational", 3),
  ep("lutheran_evangelical", "Lutheran", 4),
  ep("presbyterian_evangelical", "Presbyterian", 5),
  ep("pentecostal_evangelical", "Pentecostal", 6),
  ep("episcopalian_evangelical", "Anglican / Episcopalian", 7),
  ep("restorationist_evangelical", "Restorationist (Churches of Christ, Christian Churches)", 8),
  ep("congregational_evangelical", "Congregational", 9),
  ep("holiness_evangelical", "Holiness (Nazarene, Free Methodist)", 10),
  ep("reformed_evangelical", "Reformed", 11),
  ep("adventist_evangelical", "Adventist", 12),
  ep("anabaptist_evangelical", "Anabaptist (Mennonite, Brethren, Amish)", 13),
  ep("pietist_evangelical", "Pietist", 14),
  ep("friends_evangelical", "Friends / Quaker", 15),
  ep("other_evangelical_fundamentalist", "Other evangelical or fundamentalist", 16),
  ep("evangelical_protestant", "No particular denomination", 18),

  // Mainline Protestant tradition - FAMILY 34-45.
  mp("baptist_mainline", "Baptist", 34),
  mp("methodist_mainline", "Methodist", 35),
  mp("nondenominational_mainline", "Nondenominational", 36),
  mp("lutheran_mainline", "Lutheran", 37),
  mp("presbyterian_mainline", "Presbyterian", 38),
  mp("episcopalian_mainline", "Anglican / Episcopalian", 39),
  mp("restorationist_mainline", "Restorationist (Disciples of Christ)", 40),
  mp("congregational_mainline", "Congregational (United Church of Christ)", 41),
  mp("reformed_mainline", "Reformed", 42),
  mp("anabaptist_mainline", "Anabaptist (Mennonite, Brethren, Amish)", 43),
  mp("friends_mainline", "Friends / Quaker", 44),
  mp("mainline_protestant", "No particular denomination", 45),

  // Historically Black Protestant tradition - FAMILY 67-72.
  hbp("baptist_black_protestant", "Baptist", 67),
  hbp("methodist_black_protestant", "Methodist (AME, AME Zion, CME)", 68),
  hbp("pentecostal_black_protestant", "Pentecostal (Church of God in Christ)", 69),
  hbp("holiness_black_protestant", "Holiness", 70),
  hbp("nondenominational_black_protestant", "Nondenominational", 71),
  hbp("historically_black_protestant", "No particular denomination", 72),

  // Catholic - FAMILY 101.
  {
    slug: "roman_catholic",
    label: "Catholic",
    group: "Catholic",
    rlsFamily: 101,
    quizTradition: "Roman Catholic",
  },

  // Other Christian traditions - RELTRAD 20000/30000/40001/40002,
  // FAMILY 102-106.
  oc("latter_day_saint", "Latter-day Saint (Mormon)", 102),
  oc("orthodox_christian", "Orthodox Christian", 103),
  oc("jehovahs_witness", "Jehovah's Witness", 104),
  oc("metaphysical_christian", "Metaphysical (Christian Science, Unity, New Thought)", 105),
  oc("other_christian", "Another Christian tradition", 106),

  // Non-Christian faiths - FAMILY 201-208. Pew splits these across three
  // RELTRAD categories (world religions, other world religions, other
  // faiths); one group here, since the distinction is analytic rather than
  // something a respondent would recognize about themselves.
  of("jewish", "Jewish", 201),
  of("muslim", "Muslim", 202),
  of("buddhist", "Buddhist", 203),
  of("hindu", "Hindu", 204),
  of("other_religion", "Another world religion (Sikh, Bahá'í, Jain, and others)", 205),
  of("unitarian_liberal_faith", "Unitarian or another liberal faith", 206),
  of("new_age", "New Age, Pagan, or Wiccan", 207),
  of("native_american_religion", "Native American religion", 208),

  // Religiously unaffiliated - FAMILY 301-303, the UNAFFILDETAIL split.
  un("atheist", "Atheist", 301),
  un("agnostic", "Agnostic", 302),
  un("nothing_in_particular", "Nothing in particular", 303),

  // No Pew counterpart: a refusal, not Pew's 999 "no information" back-code.
  {
    slug: "prefer_not_to_say",
    label: "Prefer not to say",
    group: "No answer",
    rlsFamily: null,
    quizTradition: null,
  },

  // Retired: predates the RLS taxonomy, which splits it into atheist (301)
  // and agnostic (302). Kept so rows recorded before the switch still
  // resolve to a label.
  {
    slug: "atheist_agnostic",
    label: "Atheist / agnostic",
    group: "Religiously unaffiliated",
    rlsFamily: null,
    quizTradition: null,
    retired: true,
  },
];

function ep(slug: string, label: string, rlsFamily: number): ReligionOption {
  return { slug, label, group: "Evangelical Protestant", rlsFamily, quizTradition: "Evangelical" };
}
function mp(slug: string, label: string, rlsFamily: number): ReligionOption {
  return { slug, label, group: "Mainline Protestant", rlsFamily, quizTradition: "Mainline" };
}
function hbp(slug: string, label: string, rlsFamily: number): ReligionOption {
  return {
    slug,
    label,
    group: "Historically Black Protestant",
    rlsFamily,
    quizTradition: "Black Protestant",
  };
}
function oc(slug: string, label: string, rlsFamily: number): ReligionOption {
  return { slug, label, group: "Other Christian", rlsFamily, quizTradition: null };
}
function of(slug: string, label: string, rlsFamily: number): ReligionOption {
  return { slug, label, group: "Non-Christian faiths", rlsFamily, quizTradition: null };
}
function un(slug: string, label: string, rlsFamily: number): ReligionOption {
  return { slug, label, group: "Religiously unaffiliated", rlsFamily, quizTradition: null };
}

/** Pickable options, in group order - what the intake's <optgroup>s render. */
export const RELIGION_OPTIONS_BY_GROUP: { group: ReligionGroup; options: ReligionOption[] }[] =
  RELIGION_GROUPS.map((group) => ({
    group,
    options: RELIGION_OPTIONS.filter((o) => o.group === group && !o.retired),
  })).filter((g) => g.options.length > 0);

const RELIGION_BY_SLUG = new Map(RELIGION_OPTIONS.map((o) => [o.slug, o]));

/** Resolves a stored slug for display, retired ones included. */
export function religionOption(slug: string | null | undefined): ReligionOption | undefined {
  return slug ? RELIGION_BY_SLUG.get(slug) : undefined;
}

/** RLS GENDER. Pew's wording; the slugs predate it and stay as they are. */
export const GENDER_OPTIONS = [
  { slug: "male", label: "A man", rlsGender: 1 },
  { slug: "female", label: "A woman", rlsGender: 2 },
  { slug: "other", label: "In some other way", rlsGender: 3 },
  { slug: "prefer_not_to_say", label: "Prefer not to say", rlsGender: null },
] as const;

/**
 * RLS BIRTHDECADE. Pew's own coarsening of birth year - the reason this
 * intake asks for a cohort rather than an age.
 *
 * The 2010s and 2020s have no RLS code: Pew surveys adults, so BIRTHDECADE
 * stops at the 2000s. This site's own floor is 13+ (COPPA, migration 0037),
 * which the 2010s are already inside of. Both cohorts carry a null code and
 * simply fall outside any comparison with Pew's national numbers, which is
 * the honest result rather than a bug.
 */
export const BIRTH_DECADE_OPTIONS = [
  { slug: "1940s_or_earlier", label: "1940s or earlier", rlsBirthDecade: 1 },
  { slug: "1950s", label: "1950s", rlsBirthDecade: 2 },
  { slug: "1960s", label: "1960s", rlsBirthDecade: 3 },
  { slug: "1970s", label: "1970s", rlsBirthDecade: 4 },
  { slug: "1980s", label: "1980s", rlsBirthDecade: 5 },
  { slug: "1990s", label: "1990s", rlsBirthDecade: 6 },
  { slug: "2000s", label: "2000s", rlsBirthDecade: 7 },
  { slug: "2010s", label: "2010s", rlsBirthDecade: null },
  { slug: "2020s", label: "2020s", rlsBirthDecade: null },
  { slug: "prefer_not_to_say", label: "Prefer not to say", rlsBirthDecade: null },
] as const;

/** RLS HISP, asked separately from race exactly as Pew asks it. */
export const HISPANIC_OPTIONS = [
  { slug: "yes", label: "Yes", rlsHisp: 1 },
  { slug: "no", label: "No", rlsHisp: 2 },
  { slug: "prefer_not_to_say", label: "Prefer not to say", rlsHisp: null },
] as const;

/** RLS RACECMB. */
export const RACE_OPTIONS = [
  { slug: "white", label: "White", rlsRace: 1 },
  { slug: "black", label: "Black or African American", rlsRace: 2 },
  { slug: "asian", label: "Asian or Asian American", rlsRace: 3 },
  { slug: "mixed", label: "Mixed race", rlsRace: 4 },
  { slug: "other", label: "Some other race", rlsRace: 5 },
  { slug: "prefer_not_to_say", label: "Prefer not to say", rlsRace: null },
] as const;

/** RLS EDUCREC. */
export const EDUCATION_OPTIONS = [
  { slug: "high_school_or_less", label: "High school or less", rlsEduc: 1 },
  { slug: "some_college", label: "Some college / associate's degree", rlsEduc: 2 },
  { slug: "college_graduate", label: "College graduate", rlsEduc: 3 },
  { slug: "postgraduate", label: "Master's degree or higher", rlsEduc: 4 },
  { slug: "prefer_not_to_say", label: "Prefer not to say", rlsEduc: null },
] as const;

/** RLS MARITAL. */
export const MARITAL_OPTIONS = [
  { slug: "married", label: "Married", rlsMarital: 1 },
  { slug: "living_with_partner", label: "Living with a partner", rlsMarital: 2 },
  { slug: "divorced", label: "Divorced", rlsMarital: 3 },
  { slug: "separated", label: "Separated", rlsMarital: 4 },
  { slug: "widowed", label: "Widowed", rlsMarital: 5 },
  { slug: "never_married", label: "Never been married", rlsMarital: 6 },
  { slug: "prefer_not_to_say", label: "Prefer not to say", rlsMarital: null },
] as const;

/**
 * Country of residence, as ISO 3166-1 alpha-2. The RLS has no counterpart -
 * it is a survey of U.S. adults, so residence is assumed - which is exactly
 * why this list exists: readers here are not all American, and recording
 * "not the U.S." is better than recording a blank state.
 *
 * Names are ICU's, generated by scripts/gen-country-options.mjs rather than
 * typed by hand. Committed as a literal because ICU data differs between
 * Node versions and browsers, and a disagreement over one name would be a
 * hydration mismatch. Slugs are stored in the database: an existing code
 * must never change meaning.
 */
export const COUNTRY_OPTIONS = [
  { slug: "AF", label: "Afghanistan" },
  { slug: "AX", label: "Åland Islands" },
  { slug: "AL", label: "Albania" },
  { slug: "DZ", label: "Algeria" },
  { slug: "AS", label: "American Samoa" },
  { slug: "AD", label: "Andorra" },
  { slug: "AO", label: "Angola" },
  { slug: "AI", label: "Anguilla" },
  { slug: "AQ", label: "Antarctica" },
  { slug: "AG", label: "Antigua and Barbuda" },
  { slug: "AR", label: "Argentina" },
  { slug: "AM", label: "Armenia" },
  { slug: "AW", label: "Aruba" },
  { slug: "AU", label: "Australia" },
  { slug: "AT", label: "Austria" },
  { slug: "AZ", label: "Azerbaijan" },
  { slug: "BS", label: "Bahamas" },
  { slug: "BH", label: "Bahrain" },
  { slug: "BD", label: "Bangladesh" },
  { slug: "BB", label: "Barbados" },
  { slug: "BY", label: "Belarus" },
  { slug: "BE", label: "Belgium" },
  { slug: "BZ", label: "Belize" },
  { slug: "BJ", label: "Benin" },
  { slug: "BM", label: "Bermuda" },
  { slug: "BT", label: "Bhutan" },
  { slug: "BO", label: "Bolivia" },
  { slug: "BA", label: "Bosnia and Herzegovina" },
  { slug: "BW", label: "Botswana" },
  { slug: "BV", label: "Bouvet Island" },
  { slug: "BR", label: "Brazil" },
  { slug: "IO", label: "British Indian Ocean Territory" },
  { slug: "VG", label: "British Virgin Islands" },
  { slug: "BN", label: "Brunei" },
  { slug: "BG", label: "Bulgaria" },
  { slug: "BF", label: "Burkina Faso" },
  { slug: "BI", label: "Burundi" },
  { slug: "KH", label: "Cambodia" },
  { slug: "CM", label: "Cameroon" },
  { slug: "CA", label: "Canada" },
  { slug: "CV", label: "Cape Verde" },
  { slug: "BQ", label: "Caribbean Netherlands" },
  { slug: "KY", label: "Cayman Islands" },
  { slug: "CF", label: "Central African Republic" },
  { slug: "TD", label: "Chad" },
  { slug: "CL", label: "Chile" },
  { slug: "CN", label: "China" },
  { slug: "CX", label: "Christmas Island" },
  { slug: "CC", label: "Cocos (Keeling) Islands" },
  { slug: "CO", label: "Colombia" },
  { slug: "KM", label: "Comoros" },
  { slug: "CG", label: "Congo - Brazzaville" },
  { slug: "CD", label: "Congo - Kinshasa" },
  { slug: "CK", label: "Cook Islands" },
  { slug: "CR", label: "Costa Rica" },
  { slug: "CI", label: "Côte d’Ivoire" },
  { slug: "HR", label: "Croatia" },
  { slug: "CU", label: "Cuba" },
  { slug: "CW", label: "Curaçao" },
  { slug: "CY", label: "Cyprus" },
  { slug: "CZ", label: "Czechia" },
  { slug: "DK", label: "Denmark" },
  { slug: "DJ", label: "Djibouti" },
  { slug: "DM", label: "Dominica" },
  { slug: "DO", label: "Dominican Republic" },
  { slug: "EC", label: "Ecuador" },
  { slug: "EG", label: "Egypt" },
  { slug: "SV", label: "El Salvador" },
  { slug: "GQ", label: "Equatorial Guinea" },
  { slug: "ER", label: "Eritrea" },
  { slug: "EE", label: "Estonia" },
  { slug: "SZ", label: "Eswatini" },
  { slug: "ET", label: "Ethiopia" },
  { slug: "FK", label: "Falkland Islands" },
  { slug: "FO", label: "Faroe Islands" },
  { slug: "FJ", label: "Fiji" },
  { slug: "FI", label: "Finland" },
  { slug: "FR", label: "France" },
  { slug: "GF", label: "French Guiana" },
  { slug: "PF", label: "French Polynesia" },
  { slug: "TF", label: "French Southern Territories" },
  { slug: "GA", label: "Gabon" },
  { slug: "GM", label: "Gambia" },
  { slug: "GE", label: "Georgia" },
  { slug: "DE", label: "Germany" },
  { slug: "GH", label: "Ghana" },
  { slug: "GI", label: "Gibraltar" },
  { slug: "GR", label: "Greece" },
  { slug: "GL", label: "Greenland" },
  { slug: "GD", label: "Grenada" },
  { slug: "GP", label: "Guadeloupe" },
  { slug: "GU", label: "Guam" },
  { slug: "GT", label: "Guatemala" },
  { slug: "GG", label: "Guernsey" },
  { slug: "GN", label: "Guinea" },
  { slug: "GW", label: "Guinea-Bissau" },
  { slug: "GY", label: "Guyana" },
  { slug: "HT", label: "Haiti" },
  { slug: "HM", label: "Heard and McDonald Islands" },
  { slug: "HN", label: "Honduras" },
  { slug: "HK", label: "Hong Kong SAR China" },
  { slug: "HU", label: "Hungary" },
  { slug: "IS", label: "Iceland" },
  { slug: "IN", label: "India" },
  { slug: "ID", label: "Indonesia" },
  { slug: "IR", label: "Iran" },
  { slug: "IQ", label: "Iraq" },
  { slug: "IE", label: "Ireland" },
  { slug: "IM", label: "Isle of Man" },
  { slug: "IL", label: "Israel" },
  { slug: "IT", label: "Italy" },
  { slug: "JM", label: "Jamaica" },
  { slug: "JP", label: "Japan" },
  { slug: "JE", label: "Jersey" },
  { slug: "JO", label: "Jordan" },
  { slug: "KZ", label: "Kazakhstan" },
  { slug: "KE", label: "Kenya" },
  { slug: "KI", label: "Kiribati" },
  { slug: "XK", label: "Kosovo" },
  { slug: "KW", label: "Kuwait" },
  { slug: "KG", label: "Kyrgyzstan" },
  { slug: "LA", label: "Laos" },
  { slug: "LV", label: "Latvia" },
  { slug: "LB", label: "Lebanon" },
  { slug: "LS", label: "Lesotho" },
  { slug: "LR", label: "Liberia" },
  { slug: "LY", label: "Libya" },
  { slug: "LI", label: "Liechtenstein" },
  { slug: "LT", label: "Lithuania" },
  { slug: "LU", label: "Luxembourg" },
  { slug: "MO", label: "Macao SAR China" },
  { slug: "MG", label: "Madagascar" },
  { slug: "MW", label: "Malawi" },
  { slug: "MY", label: "Malaysia" },
  { slug: "MV", label: "Maldives" },
  { slug: "ML", label: "Mali" },
  { slug: "MT", label: "Malta" },
  { slug: "MH", label: "Marshall Islands" },
  { slug: "MQ", label: "Martinique" },
  { slug: "MR", label: "Mauritania" },
  { slug: "MU", label: "Mauritius" },
  { slug: "YT", label: "Mayotte" },
  { slug: "MX", label: "Mexico" },
  { slug: "FM", label: "Micronesia" },
  { slug: "MD", label: "Moldova" },
  { slug: "MC", label: "Monaco" },
  { slug: "MN", label: "Mongolia" },
  { slug: "ME", label: "Montenegro" },
  { slug: "MS", label: "Montserrat" },
  { slug: "MA", label: "Morocco" },
  { slug: "MZ", label: "Mozambique" },
  { slug: "MM", label: "Myanmar (Burma)" },
  { slug: "NA", label: "Namibia" },
  { slug: "NR", label: "Nauru" },
  { slug: "NP", label: "Nepal" },
  { slug: "NL", label: "Netherlands" },
  { slug: "NC", label: "New Caledonia" },
  { slug: "NZ", label: "New Zealand" },
  { slug: "NI", label: "Nicaragua" },
  { slug: "NE", label: "Niger" },
  { slug: "NG", label: "Nigeria" },
  { slug: "NU", label: "Niue" },
  { slug: "NF", label: "Norfolk Island" },
  { slug: "KP", label: "North Korea" },
  { slug: "MK", label: "North Macedonia" },
  { slug: "MP", label: "Northern Mariana Islands" },
  { slug: "NO", label: "Norway" },
  { slug: "OM", label: "Oman" },
  { slug: "PK", label: "Pakistan" },
  { slug: "PW", label: "Palau" },
  { slug: "PS", label: "Palestinian Territories" },
  { slug: "PA", label: "Panama" },
  { slug: "PG", label: "Papua New Guinea" },
  { slug: "PY", label: "Paraguay" },
  { slug: "PE", label: "Peru" },
  { slug: "PH", label: "Philippines" },
  { slug: "PN", label: "Pitcairn Islands" },
  { slug: "PL", label: "Poland" },
  { slug: "PT", label: "Portugal" },
  { slug: "XA", label: "Pseudo-Accents" },
  { slug: "XB", label: "Pseudo-Bidi" },
  { slug: "PR", label: "Puerto Rico" },
  { slug: "QA", label: "Qatar" },
  { slug: "RE", label: "Réunion" },
  { slug: "RO", label: "Romania" },
  { slug: "RU", label: "Russia" },
  { slug: "RW", label: "Rwanda" },
  { slug: "WS", label: "Samoa" },
  { slug: "SM", label: "San Marino" },
  { slug: "ST", label: "São Tomé and Príncipe" },
  { slug: "CQ", label: "Sark" },
  { slug: "SA", label: "Saudi Arabia" },
  { slug: "SN", label: "Senegal" },
  { slug: "RS", label: "Serbia" },
  { slug: "SC", label: "Seychelles" },
  { slug: "SL", label: "Sierra Leone" },
  { slug: "SG", label: "Singapore" },
  { slug: "SX", label: "Sint Maarten" },
  { slug: "SK", label: "Slovakia" },
  { slug: "SI", label: "Slovenia" },
  { slug: "SB", label: "Solomon Islands" },
  { slug: "SO", label: "Somalia" },
  { slug: "ZA", label: "South Africa" },
  { slug: "GS", label: "South Georgia and South Sandwich Islands" },
  { slug: "KR", label: "South Korea" },
  { slug: "SS", label: "South Sudan" },
  { slug: "ES", label: "Spain" },
  { slug: "LK", label: "Sri Lanka" },
  { slug: "BL", label: "St. Barthélemy" },
  { slug: "SH", label: "St. Helena" },
  { slug: "KN", label: "St. Kitts and Nevis" },
  { slug: "LC", label: "St. Lucia" },
  { slug: "MF", label: "St. Martin" },
  { slug: "PM", label: "St. Pierre and Miquelon" },
  { slug: "VC", label: "St. Vincent and Grenadines" },
  { slug: "SD", label: "Sudan" },
  { slug: "SR", label: "Suriname" },
  { slug: "SJ", label: "Svalbard and Jan Mayen" },
  { slug: "SE", label: "Sweden" },
  { slug: "CH", label: "Switzerland" },
  { slug: "SY", label: "Syria" },
  { slug: "TW", label: "Taiwan" },
  { slug: "TJ", label: "Tajikistan" },
  { slug: "TZ", label: "Tanzania" },
  { slug: "TH", label: "Thailand" },
  { slug: "TL", label: "Timor-Leste" },
  { slug: "TG", label: "Togo" },
  { slug: "TK", label: "Tokelau" },
  { slug: "TO", label: "Tonga" },
  { slug: "TT", label: "Trinidad and Tobago" },
  { slug: "TN", label: "Tunisia" },
  { slug: "TR", label: "Türkiye" },
  { slug: "TM", label: "Turkmenistan" },
  { slug: "TC", label: "Turks and Caicos Islands" },
  { slug: "TV", label: "Tuvalu" },
  { slug: "UM", label: "U.S. Outlying Islands" },
  { slug: "VI", label: "U.S. Virgin Islands" },
  { slug: "UG", label: "Uganda" },
  { slug: "UA", label: "Ukraine" },
  { slug: "AE", label: "United Arab Emirates" },
  { slug: "GB", label: "United Kingdom" },
  { slug: "US", label: "United States" },
  { slug: "UY", label: "Uruguay" },
  { slug: "UZ", label: "Uzbekistan" },
  { slug: "VU", label: "Vanuatu" },
  { slug: "VA", label: "Vatican City" },
  { slug: "VE", label: "Venezuela" },
  { slug: "VN", label: "Vietnam" },
  { slug: "WF", label: "Wallis and Futuna" },
  { slug: "EH", label: "Western Sahara" },
  { slug: "YE", label: "Yemen" },
  { slug: "ZM", label: "Zambia" },
  { slug: "ZW", label: "Zimbabwe" },
] as const;

/**
 * RLS STATE: the 50 states plus DC, stored as the postal abbreviation
 * rather than Pew's FIPS-derived code, so the column reads plainly in an
 * export. Order is Pew's (FIPS, i.e. alphabetical by state name).
 */
export const STATE_OPTIONS = [
  { slug: "AL", label: "Alabama" },
  { slug: "AK", label: "Alaska" },
  { slug: "AZ", label: "Arizona" },
  { slug: "AR", label: "Arkansas" },
  { slug: "CA", label: "California" },
  { slug: "CO", label: "Colorado" },
  { slug: "CT", label: "Connecticut" },
  { slug: "DE", label: "Delaware" },
  { slug: "DC", label: "District of Columbia" },
  { slug: "FL", label: "Florida" },
  { slug: "GA", label: "Georgia" },
  { slug: "HI", label: "Hawaii" },
  { slug: "ID", label: "Idaho" },
  { slug: "IL", label: "Illinois" },
  { slug: "IN", label: "Indiana" },
  { slug: "IA", label: "Iowa" },
  { slug: "KS", label: "Kansas" },
  { slug: "KY", label: "Kentucky" },
  { slug: "LA", label: "Louisiana" },
  { slug: "ME", label: "Maine" },
  { slug: "MD", label: "Maryland" },
  { slug: "MA", label: "Massachusetts" },
  { slug: "MI", label: "Michigan" },
  { slug: "MN", label: "Minnesota" },
  { slug: "MS", label: "Mississippi" },
  { slug: "MO", label: "Missouri" },
  { slug: "MT", label: "Montana" },
  { slug: "NE", label: "Nebraska" },
  { slug: "NV", label: "Nevada" },
  { slug: "NH", label: "New Hampshire" },
  { slug: "NJ", label: "New Jersey" },
  { slug: "NM", label: "New Mexico" },
  { slug: "NY", label: "New York" },
  { slug: "NC", label: "North Carolina" },
  { slug: "ND", label: "North Dakota" },
  { slug: "OH", label: "Ohio" },
  { slug: "OK", label: "Oklahoma" },
  { slug: "OR", label: "Oregon" },
  { slug: "PA", label: "Pennsylvania" },
  { slug: "RI", label: "Rhode Island" },
  { slug: "SC", label: "South Carolina" },
  { slug: "SD", label: "South Dakota" },
  { slug: "TN", label: "Tennessee" },
  { slug: "TX", label: "Texas" },
  { slug: "UT", label: "Utah" },
  { slug: "VT", label: "Vermont" },
  { slug: "VA", label: "Virginia" },
  { slug: "WA", label: "Washington" },
  { slug: "WV", label: "West Virginia" },
  { slug: "WI", label: "Wisconsin" },
  { slug: "WY", label: "Wyoming" },
] as const;

/** All fields optional - every part of the intake is skippable. */
export type Demographics = {
  /**
   * Free-entry age, collected before the intake mirrored the RLS. No longer
   * asked - BIRTH_DECADE_OPTIONS replaced it - but still carried here so
   * rows recorded earlier survive a profile backfill unchanged.
   */
  age: number | null;
  birthDecade: string | null;
  gender: string | null;
  hispanic: string | null;
  race: string | null;
  education: string | null;
  maritalStatus: string | null;
  country: string | null;
  /** Only meaningful when country is US - see validateDemographics. */
  state: string | null;
  /** Stored in the `tradition_slug` column — see 0047 on why it kept that name. */
  religionSlug: string | null;
};

export const EMPTY_DEMOGRAPHICS: Demographics = {
  age: null,
  birthDecade: null,
  gender: null,
  hispanic: null,
  race: null,
  education: null,
  maritalStatus: null,
  country: null,
  state: null,
  religionSlug: null,
};

/** The one country the state question applies to. */
export const US_COUNTRY_SLUG = "US";

const slugSet = (options: readonly { slug: string }[]) => new Set(options.map((o) => o.slug));

const RELIGION_SLUGS = slugSet(RELIGION_OPTIONS);
const GENDER_SLUGS = slugSet(GENDER_OPTIONS);
const BIRTH_DECADE_SLUGS = slugSet(BIRTH_DECADE_OPTIONS);
const HISPANIC_SLUGS = slugSet(HISPANIC_OPTIONS);
const RACE_SLUGS = slugSet(RACE_OPTIONS);
const EDUCATION_SLUGS = slugSet(EDUCATION_OPTIONS);
const MARITAL_SLUGS = slugSet(MARITAL_OPTIONS);
const COUNTRY_SLUGS = slugSet(COUNTRY_OPTIONS);
const STATE_SLUGS = slugSet(STATE_OPTIONS);

const pick = (value: unknown, allowed: Set<string>): string | null =>
  typeof value === "string" && allowed.has(value) ? value : null;

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

  const country = pick(d?.country, COUNTRY_SLUGS);
  // The state question only applies to the U.S., and the intake disables it
  // elsewhere - but the client isn't what enforces that. Naming a country
  // other than the U.S. drops any state that came with it, so no row can
  // claim to be in Utah and Brazil at once. A null country leaves state
  // alone: rows recorded before this question existed have a state and no
  // country, and they're not wrong, just older.
  const state = pick(d?.state, STATE_SLUGS);

  return {
    age,
    birthDecade: pick(d?.birthDecade, BIRTH_DECADE_SLUGS),
    gender: pick(d?.gender, GENDER_SLUGS),
    hispanic: pick(d?.hispanic, HISPANIC_SLUGS),
    race: pick(d?.race, RACE_SLUGS),
    education: pick(d?.education, EDUCATION_SLUGS),
    maritalStatus: pick(d?.maritalStatus, MARITAL_SLUGS),
    country,
    state: country !== null && country !== US_COUNTRY_SLUG ? null : state,
    religionSlug: pick(d?.religionSlug, RELIGION_SLUGS),
  };
}

function code<K extends string>(
  options: readonly ({ slug: string } & { [P in K]: number | null })[],
  key: K,
  slug: string | null,
): number | null {
  if (slug === null) return null;
  return options.find((o) => o.slug === slug)?.[key] ?? null;
}

/**
 * The RLS numeric codes for one set of answers, for exports that get read
 * alongside Pew's own tables. Null wherever the reader skipped a question
 * or picked one of the site's non-Pew options ("prefer not to say"), which
 * is also how Pew's variables behave: a refusal has no substantive code.
 */
export function rlsCodes(d: Demographics) {
  return {
    FAMILY: code(RELIGION_OPTIONS, "rlsFamily", d.religionSlug),
    BIRTHDECADE: code(BIRTH_DECADE_OPTIONS, "rlsBirthDecade", d.birthDecade),
    GENDER: code(GENDER_OPTIONS, "rlsGender", d.gender),
    HISP: code(HISPANIC_OPTIONS, "rlsHisp", d.hispanic),
    RACECMB: code(RACE_OPTIONS, "rlsRace", d.race),
    EDUCREC: code(EDUCATION_OPTIONS, "rlsEduc", d.education),
    MARITAL: code(MARITAL_OPTIONS, "rlsMarital", d.maritalStatus),
  };
}

/** True when the reader answered nothing at all - a skip in every field. */
export function isEmptyDemographics(d: Demographics): boolean {
  return Object.values(d).every((v) => v === null);
}

/**
 * The disclosure line the original spec requires above the intake.
 * Religious affiliation is special-category personal data; saying plainly
 * what happens to it costs one sentence.
 */
export const DEMOGRAPHICS_DISCLOSURE =
  "Your answers are stored anonymously and used for aggregate research. Every question is optional — skip any of them, or the whole screen.";

/**
 * Why the intake asks what it asks, shown under the disclosure. These are
 * Pew's questions, and saying so is the honest framing: the point is
 * comparability, not curiosity.
 */
export const DEMOGRAPHICS_PROVENANCE =
  "These are the same questions Pew Research Center asks in its Religious Landscape Study, worded the same way, so answers here can be compared with a national sample.";
