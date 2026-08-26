"""
Shared constants for the VOTER Survey Panel "ideas" graphics -
docs/datasets/ryan-burge/VOTER_PANEL_IDEAS.md. Imported by the three
voter_ideas_*.py compute scripts (not a render script - this file has no
matplotlib dependency), so the same group definitions/thin-group exclusion
used for the already-shipped voter_stranger.py and voter_matrices.py stay
in exactly one place across the new scripts too.

Note the actual file only contains four waves - baseline (~2011), 2012,
2016, 2017 - not the 2018-2020 waves the dataset's own description
mentions for the wider VOTER Survey program; confirmed by inspecting the
.dta's own column suffixes (867 columns, none named *_2018/*_2019/*_2020
except one 2017-wave item asking about *intended* 2018 vote). Every
longitudinal idea here is scoped to the waves that actually exist.
"""

DTA = "data/ryan-burge/tier1-strong/voter_survey_panel.dta"

RELIGION_LABELS = {
    1: "Protestant", 2: "Catholic", 3: "Mormon", 5: "Jewish",
    7: "Buddhist", 9: "Atheist", 10: "Agnostic",
    11: "Nothing in particular", 12: "Something else",
}
EXCLUDED_TOO_THIN = {4: "Orthodox", 6: "Muslim", 8: "Hindu"}
GROUP_ORDER = ["Mormon", "Protestant", "Catholic", "Jewish", "Buddhist",
               "Atheist", "Agnostic", "Nothing in particular", "Something else"]
