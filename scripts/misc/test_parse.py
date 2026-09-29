import csv
import pathlib
import xml.etree.ElementTree as ET

# World Bank CSV parsing
def get_latest_wb(file_path):
    latest = {}
    with open(file_path, newline='', encoding='utf-8') as f:
        # Skip the first 4 rows
        for _ in range(4):
            next(f)
        reader = csv.DictReader(f)
        years = [str(y) for y in range(1960, 2026)]
        for row in reader:
            country = row['Country Name']
            # Find the latest year with data
            for year in reversed(years):
                if year in row and row[year].strip():
                    latest[country] = float(row[year])
                    break
    return latest

beds = get_latest_wb(r"D:\latter-day-stats-data\funny\beds\API_SH.MED.BEDS.ZS_DS2_en_csv_v2_413810.csv")
military = get_latest_wb(r"D:\latter-day-stats-data\funny\military\API_MS.MIL.TOTL.P1_DS2_en_csv_v2_362772.csv")

print(f"Beds: {len(beds)} countries, USA: {beds.get('United States')}")
print(f"Military: {len(military)} countries, USA: {military.get('United States')}")

# Volcanoes XML parsing
def get_volcano_counts(file_path):
    counts = {}
    # the file is SpreadsheetML
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    import re
    # naive parsing: find all <Row> blocks, then find the 3rd cell's <Data> value
    rows = re.findall(r'<Row>(.*?)</Row>', content, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<Cell[^>]*><Data[^>]*>(.*?)</Data></Cell>', row, re.DOTALL)
        if len(cells) >= 3:
            country = cells[2].strip()
            # Some volcanoes might span countries, e.g. "Chile-Argentina"
            for c in country.split('-'):
                c = c.strip()
                if c and c != "Country":
                    counts[c] = counts.get(c, 0) + 1
    return counts

volcanoes = get_volcano_counts(r"D:\latter-day-stats-data\funny\GVP_Volcano_List_Holocene_202609291629.xls")
print(f"Volcanoes: {len(volcanoes)} countries, USA: {volcanoes.get('United States')}")
