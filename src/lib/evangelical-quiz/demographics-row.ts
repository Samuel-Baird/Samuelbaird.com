/**
 * Mapping between a Demographics value and the database columns that hold
 * it. Split out from demographics.ts (which the quiz ships to the browser)
 * because nothing client-side needs to know column names, and split out
 * from the server actions because the account's editor at /me/quiz needs to
 * read a profile row too.
 *
 * The columns live on both `profiles` and `evangelical_quiz_runs` -
 * migrations 0046, 0047, 0048.
 */

import { validateDemographics, type Demographics } from "./demographics";

/**
 * One string so a select can never drift from the row shape the mapper
 * below expects.
 */
export const DEMOGRAPHIC_COLUMNS =
  "age, birth_decade, gender, hispanic, race, education, marital_status, country, us_state, tradition_slug";

export type DemographicRow = {
  age?: number | null;
  birth_decade?: string | null;
  gender?: string | null;
  hispanic?: string | null;
  race?: string | null;
  education?: string | null;
  marital_status?: string | null;
  country?: string | null;
  us_state?: string | null;
  /** Migration 0046's name for the religion slug; see 0047 on why it kept it. */
  tradition_slug?: string | null;
};

/** Row -> Demographics, validated on the way through. */
export function demographicsFromRow(row: DemographicRow | null | undefined): Demographics {
  return validateDemographics({
    age: row?.age ?? null,
    birthDecade: row?.birth_decade ?? null,
    gender: row?.gender ?? null,
    hispanic: row?.hispanic ?? null,
    race: row?.race ?? null,
    education: row?.education ?? null,
    maritalStatus: row?.marital_status ?? null,
    state: row?.us_state ?? null,
    country: row?.country ?? null,
    religionSlug: row?.tradition_slug ?? null,
  });
}

/**
 * Demographics -> row. `age` is deliberately absent: the intake stopped
 * asking for it when birth_decade (RLS BIRTHDECADE) took over, so writing
 * the always-null value back would erase what older profiles recorded.
 */
export function demographicColumns(d: Demographics) {
  return {
    birth_decade: d.birthDecade,
    gender: d.gender,
    hispanic: d.hispanic,
    race: d.race,
    education: d.education,
    marital_status: d.maritalStatus,
    country: d.country,
    us_state: d.state,
    tradition_slug: d.religionSlug,
  };
}
