/**
 * Per-wave disclosure copy for the footer that appears on every screen of
 * the quiz. Sponsor and fielder are fixed; sample size and margin of error
 * vary by wave and are not present in the State of Theology workbook, so
 * they live here rather than in data.json.
 *
 * `sampleSize` and `marginOfError` are `null` until filled in with the
 * figures Ligonier/Lifeway publish for that wave — the footer renders an
 * honest "not yet on file" rather than a guessed number.
 *
 * 2025: n=3,001, fielded Jan 6-15, 2025; sampling error does not exceed
 * +/-1.9% at 95% confidence (subgroup margins are higher, unquantified in
 * the source). Confirmed against both the Lifeway Research white paper
 * ("2025 State of American Theology Study — Research Report", Methodology
 * section, https://research.lifeway.com/wp-content/uploads/2025/09/Ligonier-State-of-Theology-2025-White-Paper.pdf)
 * and the survey's own self-published methodology at thestateoftheology.com,
 * which additionally notes the panel was demographically balanced and
 * weighted on gender, age, ethnicity, income, region, and religion — see
 * the fuller methodology list on the dataset's Data Explorer page
 * (src/lib/data-explorer.ts) for that exact wording.
 *
 * 2022: figure not yet sourced — the arian item is the only 2022-wave
 * question in this quiz and it needs its own methodology citation before
 * shipping a number here.
 */
export type SurveyWaveMeta = {
  year: number;
  sponsor: string;
  fielder: string;
  sampleSize: number | null;
  marginOfError: string | null;
};

export const SURVEY_WAVES: Record<number, SurveyWaveMeta> = {
  2025: {
    year: 2025,
    sponsor: "Ligonier Ministries",
    fielder: "Lifeway Research",
    sampleSize: 3001,
    marginOfError: "±1.9% overall (95% confidence); higher within subgroups",
  },
  2022: {
    year: 2022,
    sponsor: "Ligonier Ministries",
    fielder: "Lifeway Research",
    sampleSize: null,
    marginOfError: null,
  },
};

export function waveMeta(year: number): SurveyWaveMeta {
  return (
    SURVEY_WAVES[year] ?? {
      year,
      sponsor: "Ligonier Ministries",
      fielder: "Lifeway Research",
      sampleSize: null,
      marginOfError: null,
    }
  );
}
