/**
 * Per-wave disclosure copy for the footer that appears on every screen of
 * the quiz. Sponsor and fielder are fixed; sample size and margin of error
 * vary by wave and are not present in the State of Theology workbook, so
 * they live here rather than in data.json.
 *
 * `sampleSize` and `marginOfError` are `null` until filled in with the
 * figures Ligonier/Lifeway publish for that wave — the footer renders an
 * honest "not yet on file" rather than a guessed number. Fill these in from
 * the wave's methodology note before this quiz goes out.
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
    sampleSize: null,
    marginOfError: null,
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
