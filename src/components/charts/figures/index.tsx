/**
 * Which datasets get an "Interactive" section on their /graphics page,
 * above the PNG gallery. Adding a figure is a data change to this file,
 * the same pattern src/lib/data-explorer.ts uses for datasets themselves.
 */

import { AgreementFacetsFigure } from "./agreement-facets-figure";
import { BirthDecadeFigure } from "./birth-decade-figure";
import { NetChangeFigure } from "./net-change-figure";
import { PidOverTimeFigure } from "./pid-over-time-figure";
import { SwitchingCurrentCompositionFigure } from "./switching-current-composition-figure";
import { SwitchingRaisedCohortFigure } from "./switching-raised-cohort-figure";

export const DATASET_FIGURES: Record<string, React.ComponentType[]> = {
  "state-of-theology": [AgreementFacetsFigure],
  "pew-religious-landscape-study": [
    NetChangeFigure,
    SwitchingCurrentCompositionFigure,
    SwitchingRaisedCohortFigure,
    BirthDecadeFigure,
  ],
  "ces-stacked-2006-2018": [PidOverTimeFigure],
};
