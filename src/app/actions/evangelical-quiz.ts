"use server";

import { revalidatePath } from "next/cache";
import {
  matchTradition,
  percentileOf,
  QUIZ_DATA,
  scoreAnswers,
} from "@/lib/evangelical-quiz";
import {
  isEmptyDemographics,
  validateDemographics,
  type Demographics,
} from "@/lib/evangelical-quiz/demographics";
import {
  createSupabaseServerClient,
  createSupabaseServiceClient,
} from "@/lib/supabase/server";

const ITEM_SCALE_LENGTH = new Map(QUIZ_DATA.items.map((i) => [i.id, i.scale.length]));

type SaveAnswerInput = {
  itemId: string;
  responseIndex: number;
  currentPath?: string;
};

/**
 * Records one answer for a signed-in reader. This quiz is playable with no
 * account (see scripts/evangelical-quiz/README.md) - unlike the timeline
 * quiz's saveQuizAnswer, this never redirects an anonymous caller to
 * /login. The client only calls this once it already knows the reader is
 * signed in; a signed-out call is just a no-op, not an error, since a
 * client-side auth state could theoretically be stale by a request.
 */
export async function saveEvangelicalQuizAnswer(input: SaveAnswerInput) {
  const scaleLength = ITEM_SCALE_LENGTH.get(input.itemId);
  if (scaleLength === undefined || input.responseIndex < 0 || input.responseIndex >= scaleLength) {
    throw new Error("Unknown evangelical quiz item or response.");
  }

  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { saved: false as const };

  const { error } = await supabase.from("evangelical_quiz_answers").upsert(
    {
      user_id: user.id,
      item_id: input.itemId,
      response_index: input.responseIndex,
      data_version: QUIZ_DATA.data_version,
      updated_at: new Date().toISOString(),
    },
    { onConflict: "user_id,item_id" },
  );
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  return { saved: true as const };
}

type ClearInput = {
  currentPath?: string;
};

/** Deletes a signed-in reader's saved answers, e.g. to retake the quiz. */
export async function clearEvangelicalQuizAnswers(input: ClearInput = {}) {
  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { cleared: false as const };

  const { error } = await supabase
    .from("evangelical_quiz_answers")
    .delete()
    .eq("user_id", user.id);
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  return { cleared: true as const };
}

// ---------------------------------------------------------------------------
// Demographics + completed-run recording (migration 0046)
// ---------------------------------------------------------------------------

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

type DemographicsInput = Partial<Demographics> & { currentPath?: string };

/**
 * The demographic columns shared by `profiles` and `evangelical_quiz_runs`
 * (migrations 0046 and 0047). One string so a select can never drift from
 * the row shape the mapper below expects.
 */
const DEMOGRAPHIC_COLUMNS =
  "age, birth_decade, gender, hispanic, race, education, marital_status, us_state, tradition_slug";

type DemographicRow = {
  age?: number | null;
  birth_decade?: string | null;
  gender?: string | null;
  hispanic?: string | null;
  race?: string | null;
  education?: string | null;
  marital_status?: string | null;
  us_state?: string | null;
  tradition_slug?: string | null;
};

/** Row -> Demographics. `tradition_slug` is 0046's name for the religion. */
function demographicsFromRow(row: DemographicRow | null | undefined): Demographics {
  return validateDemographics({
    age: row?.age ?? null,
    birthDecade: row?.birth_decade ?? null,
    gender: row?.gender ?? null,
    hispanic: row?.hispanic ?? null,
    race: row?.race ?? null,
    education: row?.education ?? null,
    maritalStatus: row?.marital_status ?? null,
    state: row?.us_state ?? null,
    religionSlug: row?.tradition_slug ?? null,
  });
}

/**
 * Demographics -> row. `age` is deliberately absent: the intake stopped
 * asking for it when birth_decade (RLS BIRTHDECADE) took over, so writing
 * the always-null value back would erase what older profiles recorded.
 */
function demographicColumns(d: Demographics) {
  return {
    birth_decade: d.birthDecade,
    gender: d.gender,
    hispanic: d.hispanic,
    race: d.race,
    education: d.education,
    marital_status: d.maritalStatus,
    us_state: d.state,
    tradition_slug: d.religionSlug,
  };
}

/**
 * Saves a signed-in reader's optional demographics to their profile and
 * stamps demographics_updated_at - which doubles as the "already asked"
 * marker, so this is called on skip too (with all-null fields). Anonymous
 * callers are a no-op: their demographics live in localStorage until a
 * completed run snapshots them.
 */
export async function saveEvangelicalDemographics(input: DemographicsInput) {
  const d = validateDemographics(input);

  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { saved: false as const };

  const { error } = await supabase
    .from("profiles")
    .update({
      ...demographicColumns(d),
      demographics_updated_at: new Date().toISOString(),
    })
    .eq("id", user.id);
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  return { saved: true as const };
}

type RecordRunInput = {
  /** Client-generated UUID; a duplicate insert is treated as success. */
  runId: string;
  answers: Record<string, number>;
  /** Required when the caller is anonymous. */
  anonId?: string;
  /** Used only for anonymous callers; signed-in snapshots the profile. */
  demographics?: Partial<Demographics>;
};

/**
 * Records one completed run as an append-only snapshot. Score, percentile,
 * and tradition match are recomputed here from the submitted answers -
 * client-computed numbers are never trusted. Inserts via the service
 * client (the runs table is deny-all RLS); a repeat of the same runId is
 * treated as success so client retries are idempotent.
 */
export async function recordEvangelicalQuizRun(input: RecordRunInput) {
  if (!UUID_RE.test(input.runId)) throw new Error("Bad run id.");

  // Validate: every current item answered, nothing unknown, all in range.
  const answers: Record<string, number> = {};
  for (const item of QUIZ_DATA.items) {
    const r = input.answers?.[item.id];
    if (typeof r !== "number" || !Number.isInteger(r) || r < 0 || r >= item.scale.length) {
      throw new Error("Incomplete or invalid answers.");
    }
    answers[item.id] = r;
  }

  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  let demographics: Demographics;
  let anonId: string | null = null;
  if (user) {
    const { data: profile } = await supabase
      .from("profiles")
      .select(DEMOGRAPHIC_COLUMNS)
      .eq("id", user.id)
      .maybeSingle();
    demographics = demographicsFromRow(profile);
  } else {
    if (!input.anonId || !UUID_RE.test(input.anonId)) {
      throw new Error("Anonymous runs need an anon id.");
    }
    anonId = input.anonId;
    demographics = validateDemographics(input.demographics);
  }

  const score = scoreAnswers(QUIZ_DATA, answers);
  const percentile = percentileOf(QUIZ_DATA, score);
  const match = matchTradition(QUIZ_DATA, answers);

  const service = createSupabaseServiceClient();
  const { error } = await service.from("evangelical_quiz_runs").insert({
    id: input.runId,
    user_id: user?.id ?? null,
    anon_id: anonId,
    // The run snapshot keeps `age` - it's the one place the column is still
    // written, so a profile recorded before the RLS switch keeps its value.
    age: demographics.age,
    ...demographicColumns(demographics),
    answers,
    score,
    percentile,
    matched_tradition: match?.top.tradition ?? null,
    runner_up_tradition: match?.runnerUp.tradition ?? null,
    tie: match?.tie ?? false,
    data_version: QUIZ_DATA.data_version,
  });
  // 23505 = unique violation on id: the same completion retried. Success.
  if (error && error.code !== "23505") throw error;

  return { recorded: true as const };
}

/**
 * Attaches a signed-in reader's earlier anonymous runs to their account.
 * The anon UUID is 122 unguessable random bits that never left their
 * browser's localStorage, so possession is proof enough of ownership for
 * data this low-stakes. Also backfills profile demographics from the most
 * recent claimed run, but only if the profile has never had any.
 */
export async function claimEvangelicalQuizRuns(input: { anonId: string }) {
  if (!UUID_RE.test(input.anonId)) return { claimed: 0 };

  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { claimed: 0 };

  const service = createSupabaseServiceClient();
  const { data: claimed, error } = await service
    .from("evangelical_quiz_runs")
    .update({ user_id: user.id, anon_id: null })
    .eq("anon_id", input.anonId)
    .is("user_id", null)
    .select(`id, created_at, ${DEMOGRAPHIC_COLUMNS}`);
  if (error) throw error;
  if (!claimed || claimed.length === 0) return { claimed: 0 };

  const { data: profile } = await supabase
    .from("profiles")
    .select("demographics_updated_at")
    .eq("id", user.id)
    .maybeSingle();
  if (!profile?.demographics_updated_at) {
    const latest = [...claimed].sort((a, b) =>
      String(b.created_at).localeCompare(String(a.created_at)),
    )[0];
    const d = demographicsFromRow(latest);
    if (!isEmptyDemographics(d)) {
      await supabase
        .from("profiles")
        .update({
          // Unlike the intake, this backfill does carry `age` across: it's
          // restoring a snapshot, and an older run may be the only place
          // the value survives.
          age: d.age,
          ...demographicColumns(d),
          demographics_updated_at: new Date().toISOString(),
        })
        .eq("id", user.id);
    }
  }

  return { claimed: claimed.length };
}

/**
 * Deletes one of the signed-in reader's own completed runs - the per-run
 * delete on the history page. Ownership is enforced by the query, not
 * trust: the service client (runs are deny-all RLS) deletes only where
 * both the id and the caller's user_id match.
 */
export async function deleteEvangelicalQuizRun(input: {
  runId: string;
  currentPath?: string;
}) {
  if (!UUID_RE.test(input.runId)) return { deleted: false as const };

  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { deleted: false as const };

  const service = createSupabaseServiceClient();
  const { error } = await service
    .from("evangelical_quiz_runs")
    .delete()
    .eq("id", input.runId)
    .eq("user_id", user.id);
  if (error) throw error;

  if (input.currentPath) revalidatePath(input.currentPath);
  return { deleted: true as const };
}
