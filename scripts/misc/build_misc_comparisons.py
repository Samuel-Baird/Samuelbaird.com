import csv
import json
import pathlib
import sys
import re

ROOT = pathlib.Path(__file__).parent.parent.parent
LDS_JSON = ROOT / "docs/datasets/lds-units-by-country/country-stats.json"
BANANA_CSV = pathlib.Path("D:/latter-day-stats-data/funny/banana-production.csv")
BEDS_CSV = pathlib.Path(r"D:\latter-day-stats-data\funny\beds\API_SH.MED.BEDS.ZS_DS2_en_csv_v2_413810.csv")
MILITARY_CSV = pathlib.Path(r"D:\latter-day-stats-data\funny\military\API_MS.MIL.TOTL.P1_DS2_en_csv_v2_362772.csv")
VOLCANOES_XLS = pathlib.Path(r"D:\latter-day-stats-data\funny\GVP_Volcano_List_Holocene_202609291629.xls")
OUT_JSON = ROOT / "docs/datasets/misc/misc-comparisons/comparison.json"

TRUCKLOAD_TONNES = 20

# Manual mappings for known divergences (World Bank, OWID, Volcanoes -> Church)
MANUAL_MAPPING = {
    "Congo": "Republic of the Congo",
    "Congo, Rep.": "Republic of the Congo",
    "Democratic Republic of Congo": "Democratic Republic of the Congo",
    "Congo, Dem. Rep.": "Democratic Republic of the Congo",
    "Cote d'Ivoire": "Cote d'Ivoire",
    "Côte d'Ivoire": "Cote d'Ivoire",
    "Timor": "Timor-Leste",
    "Czechia": "Czech Republic",
    "North Macedonia": "Macedonia",
    "Eswatini": "Swaziland",
    "Cabo Verde": "Cape Verde",
    "Micronesia (country)": "Micronesia",
    "Egypt, Arab Rep.": "Egypt",
    "Iran, Islamic Rep.": "Iran",
    "Russian Federation": "Russia",
    "Venezuela, RB": "Venezuela",
    "Korea, Rep.": "South Korea",
    "Korea, Dem. People's Rep.": "North Korea",
    "Slovak Republic": "Slovakia",
    "Syrian Arab Republic": "Syria",
    "Yemen, Rep.": "Yemen",
    "Lao PDR": "Laos",
    "Turkiye": "Turkey",
    "Türkiye": "Turkey",
    "Kyrgyz Republic": "Kyrgyzstan",
    "Bahamas, The": "Bahamas",
    "Gambia, The": "Gambia",
    "Syria": "Syria",
    "Macao SAR, China": "Macau",
    "Hong Kong SAR, China": "Hong Kong",
    "Taiwan, China": "Taiwan",
}

def map_name(name, church_names):
    name = name.strip()
    if name in church_names:
        return name
    if name in MANUAL_MAPPING and MANUAL_MAPPING[name] in church_names:
        return MANUAL_MAPPING[name]
    # some reverse mapping logic
    for c in church_names:
        if c in name or name in c:
            return c
    return name

def load_banana_data():
    latest = {}
    with open(BANANA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity = row["Entity"].strip()
            code = row.get("Code", "").strip()
            if not code or code.startswith("OWID_") or "(FAO)" in entity:
                continue
            try:
                year = int(row["Year"])
                tonnes = float(row["Bananas - Production (tonnes)"].strip())
            except (ValueError, KeyError):
                continue
            if entity not in latest or year > latest[entity][0]:
                latest[entity] = (year, tonnes)
    return {k: v[1] for k, v in latest.items()}

def get_latest_wb(file_path):
    latest = {}
    with open(file_path, newline='', encoding='utf-8') as f:
        for _ in range(4): next(f)
        reader = csv.DictReader(f)
        years = [str(y) for y in range(1960, 2026)]
        for row in reader:
            country = row['Country Name']
            for year in reversed(years):
                if year in row and row[year].strip():
                    latest[country] = float(row[year])
                    break
    return latest

def get_volcano_counts():
    counts = {}
    with open(VOLCANOES_XLS, 'r', encoding='utf-8') as f:
        content = f.read()
    rows = re.findall(r'<Row>(.*?)</Row>', content, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<Cell[^>]*><Data[^>]*>(.*?)</Data></Cell>', row, re.DOTALL)
        if len(cells) >= 3:
            country = cells[2].strip()
            for c in country.split('-'):
                c = c.strip()
                if c and c != "Country":
                    counts[c] = counts.get(c, 0) + 1
    return counts

def main():
    with open(LDS_JSON, encoding="utf-8") as f:
        lds_raw = json.load(f)
    lds_countries = lds_raw["countries"]
    church_names = set(lds_countries.keys())

    banana_raw = load_banana_data()
    beds_raw = get_latest_wb(BEDS_CSV)
    military_raw = get_latest_wb(MILITARY_CSV)
    volcano_raw = get_volcano_counts()

    # Map names
    banana_mapped = {map_name(k, church_names): v for k, v in banana_raw.items()}
    beds_mapped = {map_name(k, church_names): v for k, v in beds_raw.items()}
    military_mapped = {map_name(k, church_names): v for k, v in military_raw.items()}
    volcano_mapped = {map_name(k, church_names): v for k, v in volcano_raw.items()}

    LDS_STAT_FIELDS = [
        "members", "congregations", "wards", "branches",
        "stakes", "districts", "missions", "temples", "family_history_centers",
    ]

    countries_out = {}
    for country, lds in lds_countries.items():
        entry = {}
        for field in LDS_STAT_FIELDS:
            entry[f"lds_{field}"] = lds.get(field, 0) or 0

        # Bananas
        if country in banana_mapped:
            entry["banana_tonnes"] = round(banana_mapped[country], 2)
            entry["banana_truckloads"] = round(banana_mapped[country] / TRUCKLOAD_TONNES, 2)
        
        # Beds
        if country in beds_mapped:
            entry["hospital_beds_per_1000"] = round(beds_mapped[country], 2)

        # Military
        if country in military_mapped:
            entry["armed_forces"] = int(military_mapped[country])

        # Volcanoes
        if country in volcano_mapped:
            entry["volcanoes"] = volcano_mapped[country]

        countries_out[country] = entry

    output = {
        "source": "LDS: Church facts-and-statistics; Bananas: FAOSTAT; Beds & Military: World Bank; Volcanoes: Smithsonian GVP",
        "lds_year": lds_raw.get("as_of", "2025"),
        "truckload_tonnes": TRUCKLOAD_TONNES,
        "countries": countries_out,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("Built comparison.json")

if __name__ == "__main__":
    main()
