"""
Renders the ten-largest-us-churches-2035 dataset's one chart: a log-scale
dumbbell comparing each denomination's last-reported membership against its
2035 straight-line projection. See scripts/flagship-charts/common.py's
render_dumbbell_log docstring for the chart shape and why log scale is
required here.

Usage:
    python scripts/ten-largest-us-churches-2035/build_data.py
    python scripts/ten-largest-us-churches-2035/render_chart.py \
        --out public/data-explorer/ten-largest-us-churches-2035/projected-2035.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_dumbbell_log  # noqa: E402

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "docs/datasets/ten-largest-us-churches-2035/denominations.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    data = json.loads(DATA_PATH.read_text())
    denominations = data["denominations"]
    order = data["denomination_order"]

    # Display order: largest current (last-reported) membership first, so
    # the chart reads "biggest church at top" - the same "largest churches"
    # framing the dataset is named for - rather than sorted by projected
    # change or by the JSON's own build order.
    rows = sorted(order, key=lambda s: denominations[s]["last_reported_members"], reverse=True)

    # Short labels for the chart's own y-axis (long formal names would clip
    # against the canvas edge or crowd the "Presbyterian Church (USA)"/
    # "...in America" pair together) - the JSON's own `name` field keeps the
    # full formal name for the dataset page and alt text.
    CHART_LABELS = {
        "catholic-church": "Catholic Church",
        "united-methodist-church": "United Methodist Church",
        "lds-church": "LDS Church",
        "elca": "ELCA",
        "lcms": "LCMS",
        "orthodox-christian": "Orthodox Christian (est.)",
        "episcopal-church": "Episcopal Church",
        "pcusa": "PCUSA",
        "cogic": "Church of God in Christ",
        "pca": "PCA",
    }
    row_labels = {s: CHART_LABELS[s] for s in order}
    start_values = {s: denominations[s]["last_reported_members"] for s in order}
    end_values = {s: denominations[s]["projected_2035_members"] for s in order}
    low_confidence_rows = {s for s in order if denominations[s]["confidence"] == "low"}

    render_dumbbell_log(
        rows=rows,
        row_labels=row_labels,
        start_values=start_values,
        end_values=end_values,
        low_confidence_rows=low_confidence_rows,
        title="Ten Largest U.S.-Rooted Churches, Projected to 2035",
        subtitle="Last reported membership vs. a straight-line trend extended to 2035",
        caption_paragraphs=[
            "Each dot is that denomination's own most recently reported membership figure "
            "(years vary by body, 2016-2025); each triangle is a simple ordinary-least-"
            "squares line through that body's own historical figures, extended to 2035. "
            "This is a blunt straight-line extrapolation, not a demographic forecast - it "
            "can't see a schism, policy shift, or rate change that hasn't happened yet in "
            "the data. LDS Church figures are worldwide, not U.S.-only. Starred (*) "
            "entries have low-confidence sourcing: Catholic figures vary 5-15M by "
            "methodology; Orthodox and COGIC figures are sparse and, for COGIC, diverge "
            "roughly 5-6x from independent U.S. Religion Census counts. See "
            "docs/datasets/ten-largest-us-churches-2035/README.md for every figure's "
            "exact citation.",
            "Modeled after Ryan Burge's GSS-based American-religion projections: "
            "gist.github.com/ryanburge/e785275206cd12584b73eb4ec9b3ad52",
        ],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
