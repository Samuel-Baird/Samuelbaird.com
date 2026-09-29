import csv
import json
import pathlib
import re
import pandas as pd

ROOT = pathlib.Path(__file__).parent.parent.parent
LDS_JSON = ROOT / "docs/datasets/lds-units-by-country/country-stats.json"

FUNNY_DIR = pathlib.Path("D:/latter-day-stats-data/funny")
BANANA_CSV = FUNNY_DIR / "banana-production.csv"
BEDS_CSV = FUNNY_DIR / "beds/API_SH.MED.BEDS.ZS_DS2_en_csv_v2_413810.csv"
MILITARY_CSV = FUNNY_DIR / "military/API_MS.MIL.TOTL.P1_DS2_en_csv_v2_362772.csv"
VOLCANOES_XLS = FUNNY_DIR / "GVP_Volcano_List_Holocene_202609291629.xls"
FOREST_CSV = FUNNY_DIR / "FAO_GFRA.csv"
NUCLEAR_XLSX = FUNNY_DIR / "nuclear reactor data.xlsx"

# New datasets
FRESHWATER_DIR = FUNNY_DIR / "Annual freshwater withdrawals"
CEREAL_DIR = FUNNY_DIR / "API_AG.PRD.CREL.MT_DS2_en_csv_v2_46939"
PATENTS_DIR = FUNNY_DIR / "API_IP.PAT.RESD_DS2_en_csv_v2_434388"
TOURISTS_DIR = FUNNY_DIR / "API_ST.INT.ARVL_DS2_en_csv_v2_421778"

OUT_JSON = ROOT / "docs/datasets/misc/misc-comparisons/comparison.json"

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
    if name in church_names: return name
    if name in MANUAL_MAPPING and MANUAL_MAPPING[name] in church_names: return MANUAL_MAPPING[name]
    for c in church_names:
        if c in name or name in c: return c
    return name

def load_banana_data():
    latest = {}
    with open(BANANA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity = row["Entity"].strip()
            code = row.get("Code", "").strip()
            if not code or code.startswith("OWID_") or "(FAO)" in entity: continue
            try:
                year = int(row["Year"])
                tonnes = float(row["Bananas - Production (tonnes)"].strip())
            except (ValueError, KeyError): continue
            if entity not in latest or year > latest[entity][0]:
                latest[entity] = (year, tonnes)
    return {k: v[1] for k, v in latest.items()}

def get_latest_wb(file_path):
    if not file_path or not file_path.exists(): return {}
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
    with open(VOLCANOES_XLS, 'r', encoding='utf-8') as f: content = f.read()
    rows = re.findall(r'<Row>(.*?)</Row>', content, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<Cell[^>]*><Data[^>]*>(.*?)</Data></Cell>', row, re.DOTALL)
        if len(cells) >= 3:
            country = cells[2].strip()
            for c in country.split('-'):
                c = c.strip()
                if c and c != "Country": counts[c] = counts.get(c, 0) + 1
    return counts

def parse_simple_csv(file_path, country_col, val_col):
    if not file_path or not file_path.exists(): return {}
    res = {}
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            c = row.get(country_col)
            if c:
                val = row.get(val_col, "")
                if val.strip(): res[c] = float(val)
    return res

def parse_nuclear():
    try:
        df = pd.read_excel(NUCLEAR_XLSX)
        counts = df['Country'].value_counts().to_dict()
        return counts
    except:
        return {}

def find_wb_csv(dir_path):
    if not dir_path.exists(): return None
    files = list(dir_path.glob("API_*.csv"))
    return files[0] if files else None

def main():
    with open(LDS_JSON, encoding="utf-8") as f:
        lds_raw = json.load(f)
    church_names = set(lds_raw["countries"].keys())

    def mm(raw): return {map_name(k, church_names): v for k, v in raw.items()}

    banana_mapped = mm(load_banana_data())
    beds_mapped = mm(get_latest_wb(BEDS_CSV))
    military_mapped = mm(get_latest_wb(MILITARY_CSV))
    volcano_mapped = mm(get_volcano_counts())

    forest_mapped = mm(parse_simple_csv(FOREST_CSV, "REF_AREA_LABEL", "OBS_VALUE"))
    nuclear_mapped = mm(parse_nuclear())
    
    freshwater_mapped = mm(get_latest_wb(find_wb_csv(FRESHWATER_DIR)))
    cereal_mapped = mm(get_latest_wb(find_wb_csv(CEREAL_DIR)))
    patents_mapped = mm(get_latest_wb(find_wb_csv(PATENTS_DIR)))
    tourists_mapped = mm(get_latest_wb(find_wb_csv(TOURISTS_DIR)))

    LDS_STAT_FIELDS = [
        "members", "congregations", "wards", "branches",
        "stakes", "districts", "missions", "temples", "family_history_centers",
    ]

    countries_out = {}
    for country, lds in lds_raw["countries"].items():
        entry = {}
        for field in LDS_STAT_FIELDS:
            entry[f"lds_{field}"] = lds.get(field, 0) or 0

        if country in banana_mapped: entry["banana_tonnes"] = round(banana_mapped[country], 2)
        if country in beds_mapped: entry["hospital_beds_per_1000"] = round(beds_mapped[country], 2)
        if country in military_mapped: entry["armed_forces"] = int(military_mapped[country])
        if country in volcano_mapped: entry["volcanoes"] = volcano_mapped[country]
        if country in forest_mapped: entry["forest_area_1000_ha"] = round(forest_mapped[country], 2)
        if country in nuclear_mapped: entry["nuclear_reactors"] = int(nuclear_mapped[country])
        
        if country in freshwater_mapped: entry["freshwater_withdrawals"] = round(freshwater_mapped[country], 2)
        if country in cereal_mapped: entry["cereal_production_mt"] = round(cereal_mapped[country], 2)
        if country in patents_mapped: entry["patent_applications"] = int(patents_mapped[country])
        if country in tourists_mapped: entry["tourist_arrivals"] = int(tourists_mapped[country])

        countries_out[country] = entry

    output = {
        "source": "LDS stats; FAOSTAT; World Bank; Smithsonian GVP; PRIS",
        "lds_year": lds_raw.get("as_of", "2025"),
        "countries": countries_out,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("Built comparison.json")

if __name__ == "__main__":
    main()
