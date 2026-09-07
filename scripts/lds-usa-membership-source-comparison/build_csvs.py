import csv, os

OUT = r"C:\work\latter-day-stats\docs\datasets\lds-usa-membership-source-comparison"
os.makedirs(OUT, exist_ok=True)

HEADER = ["year","membership","geography","statistic_type","reporting_date",
          "publication_year","source_name","source_url","source_detail","notes"]

def write_csv(fname, rows):
    path = os.path.join(OUT, fname)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(HEADER)
        for r in rows:
            w.writerow(r)
    print("wrote", path, len(rows), "rows")

WB = "https://web.archive.org/web/"
SRC_NEWSROOM = "Church Newsroom"
SRC_ALMANAC = "Deseret News Church Almanac"
SRC_ARDA = "Yearbook of American and Canadian Churches via ARDA"
SRC_CENSUS = "U.S. Religion Census"

# ---------------------------------------------------------------------------
# 1. Church Newsroom
# ---------------------------------------------------------------------------
newsroom_rows = [
    ["2010","6144582","United States","membership","",
     "2012", SRC_NEWSROOM,
     WB+"20120213212915/http://www.mormonnewsroom.org:80/facts-and-statistics/country/united-states",
     "mormonnewsroom.org country page, \"Total Church Membership\" field; Wayback capture 2012-02-13",
     "Page stamped \"UPDATED on 07 APRIL 2011\"; presumed to reflect the year-end-2010 total (per the usual post-April-General-Conference reporting cadence), but the page does not explicitly state an \"as of\" statistical date, only the update-post date. Year assignment (2010) is inferred, not stated by the source."],

    ["2011","6229233","United States","membership","2011-12-31",
     "2013", SRC_NEWSROOM,
     WB+"20130116064203/http://www.mormonnewsroom.org/facts-and-statistics/country/united-states/",
     "mormonnewsroom.org country page; Wayback capture 2013-01-16",
     "Page explicitly stamped \"UPDATED on 31 DECEMBER 2011\"."],

    ["2012","6321416","United States","membership","",
     "2014", SRC_NEWSROOM,
     WB+"20140220021910/http://www.mormonnewsroom.org:80/facts-and-statistics/country/united-states",
     "mormonnewsroom.org country page (redesigned layout); Wayback capture 2014-02-20",
     "No explicit as-of date on page. Year inferred as capture_year minus 2, following the offset observed in the two explicitly-dated snapshots above (2012->2010, 2013->2011); not stated by the source."],

    ["2013","6398889","United States","membership","",
     "2015", SRC_NEWSROOM,
     WB+"20150219101228/http://www.mormonnewsroom.org:80/facts-and-statistics/country/united-states",
     "mormonnewsroom.org country page; Wayback capture 2015-02-19",
     "No explicit as-of date on page. Year inferred (capture_year minus 2); not stated by the source."],

    ["2014","6466267","United States","membership","",
     "2016", SRC_NEWSROOM,
     WB+"20160113162525/http://www.mormonnewsroom.org/facts-and-statistics/country/united-states",
     "mormonnewsroom.org country page; Wayback capture 2016-01-13",
     "No explicit as-of date on page. Year inferred (capture_year minus 2); not stated by the source."],

    ["2015","6531656","United States","membership","",
     "2017", SRC_NEWSROOM,
     WB+"20170314111618/http://www.mormonnewsroom.org/facts-and-statistics/country/united-states",
     "mormonnewsroom.org country page; Wayback capture 2017-03-14",
     "No explicit as-of date on page. Year inferred (capture_year minus 2); not stated by the source."],

    ["2016","6592195","United States","membership","",
     "2018", SRC_NEWSROOM,
     WB+"20180314005846/https://www.mormonnewsroom.org/facts-and-statistics/country/united-states",
     "mormonnewsroom.org country page (post-2018-rebrand URL, still mormonnewsroom.org domain); Wayback capture 2018-03-14",
     "No explicit as-of date on page. Year inferred (capture_year minus 2); not stated by the source."],

    ["2017","6681829","United States","membership","",
     "2019", SRC_NEWSROOM,
     WB+"20190628015016/https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/united-states",
     "newsroom.churchofjesuschrist.org country page (post-rebrand domain), stat-tile layout; Wayback captures 2019-06-28 and 2020-01-04 both show this identical value",
     "No explicit as-of date on page. Year inferred (capture_year minus 2, using the earlier capture). Value unchanged between the two captures spanning ~6 months, indicating no update to the posted figure in that window."],

    ["2019","6721032","United States","membership","",
     "2021", SRC_NEWSROOM,
     WB+"20210118011439/https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/united-states",
     "newsroom.churchofjesuschrist.org country page; Wayback captures 2021-01-18 and 2022-01-17 both show this identical value",
     "No explicit as-of date on page. Year inferred (capture_year minus 2, using the earlier capture). Value unchanged for a full year between captures, a longer stall than in other periods, plausibly reflecting a COVID-era reporting lag."],

    ["2021","6763019","United States","membership","",
     "2023", SRC_NEWSROOM,
     WB+"20230105022042/https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/united-states",
     "newsroom.churchofjesuschrist.org country page; Wayback capture 2023-01-05",
     "No explicit as-of date on page. Year inferred (capture_year minus 2); not stated by the source. First increase after the multi-year stall noted above."],

    ["2022","6868793","United States","membership","",
     "2024", SRC_NEWSROOM,
     WB+"20240416195315/https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/united-states",
     "newsroom.churchofjesuschrist.org country page; Wayback captures 2024-04-16 and 2025-01-15 both show this identical value",
     "No explicit as-of date on page. Year inferred (capture_year minus 2, using the earlier capture); captured shortly after the April 2024 General Conference."],

    ["2025","6929770","United States","membership","2025-12-31",
     "2026", SRC_NEWSROOM,
     "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/united-states",
     "Live page (accessed 2026-09-06), redesigned churchofjesuschrist.org \"facts and statistics\" template; explicit \"Last Updated On 31 Dec 2025\"",
     "Only observation with a fully explicit, unambiguous as-of date. Independently corroborated by a September 2026 Church News/Deseret News article reporting approximately 6.93 million U.S. members at year-end 2025. Note the capture-year-minus-1 offset here differs from the capture-year-minus-2 pattern seen in earlier years -- the reporting lag appears to have shortened over time rather than staying fixed; this is an observation about reporting cadence, not a correction of any other row."],
]

write_csv("church_newsroom_usa_membership.csv", newsroom_rows)

# ---------------------------------------------------------------------------
# 2. Deseret News Church Almanac
# ---------------------------------------------------------------------------
CUMORAH = "https://www.cumorah.com/countries/viewReports/58/United%20States"
almanac_rows = [
    ["1973","2530000","United States","membership","",
     "1974", SRC_ALMANAC, CUMORAH,
     "Deseret News 1974 Church Almanac, p.117 (\"Membership Distribution of the Church of Jesus Christ of Latter-day Saints 1973\" table, pp.116-117), as compiled by cumorah.com",
     "Rounded to the nearest 10,000 by the compiling site, not stated as the Almanac's own exact integer. Earliest Almanac-cited figure recovered for this ingestion. Not independently verified against a scanned page -- access to the original 1974 edition was blocked (see README)."],

    ["1983","3050000","United States","membership","",
     "", SRC_ALMANAC, CUMORAH,
     "Deseret News Church Almanac (specific edition/page not given by the compiling site)",
     "Rounded figure; cumorah.com's compiled table gives no per-row Almanac edition or page citation for this year."],

    ["1987","4100000","United States","membership","",
     "", SRC_ALMANAC, CUMORAH,
     "Deseret News Church Almanac (specific edition/page not given by the compiling site)",
     "Rounded figure; no per-row Almanac edition or page citation given by the compiling site."],

    ["1993","4520000","United States","membership","",
     "", SRC_ALMANAC, CUMORAH,
     "Deseret News Church Almanac (specific edition/page not given by the compiling site)",
     "Rounded figure; no per-row Almanac edition or page citation given by the compiling site."],

    ["1997","4920000","United States","membership","",
     "", SRC_ALMANAC, CUMORAH,
     "Deseret News Church Almanac (specific edition/page not given by the compiling site)",
     "Rounded figure; no per-row Almanac edition or page citation given by the compiling site."],

    ["2000","5210000","United States","membership","",
     "", SRC_ALMANAC, CUMORAH,
     "Deseret News Church Almanac (specific edition/page not given by the compiling site)",
     "Rounded figure; no per-row Almanac edition or page citation given by the compiling site. A separate, non-Almanac source (an encyclopedia entry of unclear methodology) gives a materially different figure (~4.42 million) for the same nominal year 2000; that figure is NOT included here because it could not be confirmed as Almanac-derived -- see README for discussion."],

    ["2002","5410000","United States","membership","",
     "", SRC_ALMANAC, CUMORAH,
     "Deseret News Church Almanac (specific edition/page not given by the compiling site)",
     "Rounded figure; no per-row Almanac edition or page citation given by the compiling site."],

    ["2004","5600000","United States","membership","",
     "", SRC_ALMANAC, CUMORAH,
     "Deseret News Church Almanac (specific edition/page not given by the compiling site)",
     "Rounded figure; no per-row Almanac edition or page citation given by the compiling site."],

    ["2006","5780000","United States","membership","",
     "", SRC_ALMANAC, CUMORAH,
     "Deseret News Church Almanac (specific edition/page not given by the compiling site)",
     "Rounded figure; no per-row Almanac edition or page citation given by the compiling site."],

    ["2007","5873408","United States","membership","",
     "", SRC_ALMANAC, "https://www.rickety.us/lds/us/",
     "Not directly stated by any source found; arithmetically derived by subtracting the site's published \"2009\" and \"2008\" year-over-year delta columns (84,862 and 100,637) from the confirmed 2009 total of 6,058,907",
     "DERIVED value, not a number any source states outright for this year -- flagged as low-confidence per the source's own delta-column arithmetic rather than presented as independently verified."],

    ["2008","5974045","United States","membership","",
     "", SRC_ALMANAC, "https://www.rickety.us/lds/us/",
     "Not directly stated by any source found; arithmetically derived by subtracting the site's published \"2009\" year-over-year delta column (84,862) from the confirmed 2009 total of 6,058,907",
     "DERIVED value, same caveat as the 2007 row. For comparison, a separately-sourced cumorah.com row (also in this file) gives a rounded ~5,970,000 for a nearby nominal year, which is roughly consistent in magnitude but not a confirmation of this specific derived figure."],

    ["2009","6058907","United States","membership","2010-01-01",
     "2011", SRC_ALMANAC, "https://www.rickety.us/2010/12/united-states-lds-church-membership-statistics/",
     "Deseret News 2011 Church Almanac, as quoted/compiled by rickety.us: \"I have updated the United States LDS Membership table using numbers obtained from the Deseret News 2011 Church Almanac\"",
     "Directly stated total, corroborated across two independent rickety.us pages (the December 2010 blog post and the persistent /lds/us/ data page). Highest-confidence modern-era figure recovered for this file."],

    ["2010","6144582","United States","membership","2011-01-01",
     "2012", SRC_ALMANAC, "https://www.rickety.us/2011/12/u-s-lds-membership-statistics/",
     "Deseret News 2012 Church Almanac, p.324, as quoted/compiled by rickety.us: \"the Church's U.S. membership was 6,144,582 as of January 1, 2011\"",
     "IMPORTANT CAVEAT: rickety.us's own footnote on its /lds/us/ data page states that \"the totals for the U.S. on page 324 of the 2012 Almanac incorrectly used totals from the 2011 Almanac\" -- i.e. this printed figure may be a reprint/misprint of the prior year's total rather than a genuinely updated Jan-1-2011 count. Retained here exactly as reported, per this project's provenance rules; not corrected."],

    ["2010","6144582","United States","membership","",
     "", SRC_ALMANAC, CUMORAH,
     "Deseret News Church Almanac (specific edition/page not given by the compiling site); value matches the 2012-Almanac figure quoted by rickety.us above",
     "Independent corroboration of the same number via a second compiler, but inherits the same page-324 misprint caveat noted in the row above; retained as a separate observation rather than merged, since it comes from a different compiling source."],
]
write_csv("church_almanac_usa_membership.csv", almanac_rows)

# ---------------------------------------------------------------------------
# 3. ARDA / Yearbook of American and Canadian Churches
# ---------------------------------------------------------------------------
ARDA_URL = "https://www.thearda.com/us-religion/group-profiles/groups?D=211"
ARDA_DETAIL = ("ARDA group profile, \"Church of Jesus Christ of Latter-day Saints, Members (1925-2010)\" chart; "
               "data drawn from the National Council of Churches Historic Archive CD and print editions of the "
               "Yearbook of American and Canadian Churches. Values extracted from the page's client-side chart "
               "data object (window.line_chart_OverTimeMem_data); no single Yearbook edition/year is cited "
               "per data point by ARDA -- presented as one compiled series.")

arda_data = [
    (1925,535659,""),(1929,596108,""),
    (1931,468386,"Value is lower than both the neighboring 1929 (596,108) and 1933 (638,761) figures; retained as reported, flagged as a possible dip/discontinuity."),
    (1933,638761,""),(1935,666594,""),(1937,690401,""),(1939,724401,""),(1941,816774,""),
    (1944,870346,""),(1946,911279,""),(1947,916789,""),(1950,1111314,""),
    (1952,1077285,"Value is lower than both the neighboring 1950 (1,111,314) and 1953 (1,179,887) figures; retained as reported, flagged as a possible dip/discontinuity."),
    (1953,1179887,""),(1955,1230021,""),(1956,1289581,""),(1957,1339638,""),(1958,1394729,""),
    (1959,1457735,""),(1960,1486887,""),(1961,1595390,""),(1962,1682096,""),(1963,1787896,""),
    (1964,1850000,"Round number (1,850,000) suggests this may be an estimate rather than a precise count, unlike most neighboring years."),
    (1965,1789175,"Value is lower than 1964 (1,850,000) and far below 1966 (2,480,899); part of a 1965-1967 discontinuity cluster. Retained as reported."),
    (1966,2480899,"Sharp spike far above both 1965 (1,789,175) and 1967 (1,891,965); a clear discontinuity, very likely a data or transcription error in the underlying Yearbook edition, but retained exactly as reported per this project's rules."),
    (1967,1891965,""),(1968,1930811,""),(1970,2073146,""),(1971,2133072,""),(1972,2185810,""),
    (1973,2208045,""),(1974,2267866,""),(1975,2336715,""),(1976,2391892,""),(1977,2486261,""),
    (1978,2952000,"Spike above both 1977 (2,486,261) and 1979 (2,706,000); the round number also suggests an estimate rather than a precise count."),
    (1979,2706000,""),(1980,2811000,""),
    (1981,3490000,"Large single-year jump from 1980 (2,811,000); flagged as an unusually large increase, retained as reported."),
    (1982,3510000,""),(1983,3602000,""),(1985,3860000,""),
    (1987,4000000,"Round number, likely a rounded/estimated figure rather than a precise count."),
    (1989,4175400,""),(1990,4267000,""),(1991,4336000,""),(1992,4430000,""),(1993,4520000,""),
    (1994,4613000,""),(1995,4711500,""),
    (1996,4800000,"Round number, likely a rounded/estimated figure rather than a precise count."),
    (1997,4923100,""),
    (1999,4593136,"Value is lower than both 1997 (4,923,100) and 2000 (5,208,827); retained as reported, flagged as a possible dip/discontinuity."),
    (2000,5208827,""),(2001,5310598,""),(2002,5410544,""),(2003,5503192,""),(2004,5599177,""),
    (2005,5690672,""),(2006,5779316,""),(2007,5873408,""),(2008,5974041,""),(2009,6058907,""),
    (2010,6157238,"Differs from the U.S. Religion Census's independently-sourced 2010 figure of 6,144,582 (different source and methodology; see us_religion_census_lds_membership.csv). Not reconciled here."),
]
arda_rows = []
for year, membership, extra_note in arda_data:
    note = "Data taken directly from ARDA's compiled chart series; no gaps were filled -- years absent here (e.g. 1926-28, 1930, 1932, 1934, 1936, 1938, 1940, 1942-43, 1945, 1948-49, 1951, 1954, 1969, 1984, 1986, 1988, 1998) are simply not present in the source series."
    if extra_note:
        note = extra_note + " " + note
    arda_rows.append([str(year), str(membership), "United States", "inclusive membership", "",
                       "", SRC_ARDA, ARDA_URL, ARDA_DETAIL, note])
write_csv("arda_yearbook_usa_membership.csv", arda_rows)

# ---------------------------------------------------------------------------
# 4. U.S. Religion Census
# ---------------------------------------------------------------------------
census_rows = [
    ["1952","845689","United States (national total)","adherents","",
     "1952", SRC_CENSUS, "https://www.usreligioncensus.org/report1.php?year=1952",
     "\"Single-year report - all denominations\" tool, row for \"Church of Jesus Christ of Latter-day Saints, The\"",
     "Denomination label used: \"Church of Jesus Christ of Latter-day Saints, The\", kept distinct from \"Community of Christ\" (106,009 adherents that year) in the same table. The \"Congregations\" field shows 0 for LDS this year, almost certainly meaning the count was not submitted/available for this group rather than a literal zero; flagged rather than silently omitted."],

    ["1971","2133072","United States (national total)","adherents","",
     "1971", SRC_CENSUS, "https://www.usreligioncensus.org/report1.php?year=1971",
     "\"Single-year report - all denominations\" tool, row for \"Church of Jesus Christ of Latter-day Saints, The\"",
     "\"Congregations\" field again shows 0 for LDS, likely not submitted/available for this group that year rather than literal. Note this figure is numerically identical to the ARDA/Yearbook 1971 figure in arda_yearbook_usa_membership.csv -- the two sources may share an underlying data submission for this year, but this is not confirmed and no merging has been done."],

    ["1980","2684744","United States (national total)","adherents","",
     "1980", SRC_CENSUS, "https://www.usreligioncensus.org/report1.php?year=1980",
     "\"Single-year report - all denominations\" tool, row for \"Church of Jesus Christ of Latter-day Saints, The\"",
     "Congregations reported this year: 6,771."],

    ["1990","3540820","United States (national total)","adherents","",
     "1990", SRC_CENSUS, "https://www.usreligioncensus.org/report1.php?year=1990",
     "\"Single-year report - all denominations\" tool, row for \"Church of Jesus Christ of Latter-day Saints, The\"",
     "Congregations reported this year: 9,208."],

    ["2000","4224026","United States (national total)","adherents","",
     "2000", SRC_CENSUS, "https://www.usreligioncensus.org/report1.php?year=2000",
     "\"Single-year report - all denominations\" tool, row for \"Church of Jesus Christ of Latter-day Saints, The\"",
     "Congregations reported this year: 11,515. Note this \"adherents\" figure (4,224,026) is well below the Church's own membership figure for the same nominal year reported elsewhere (~5.2 million per Newsroom/ARDA compilations); reflects a methodological difference in how adherents are counted/estimated by the Religion Census, not an error -- see README."],

    ["2010","6144582","United States (national total)","adherents","",
     "2010", SRC_CENSUS, "https://www.usreligioncensus.org/report1.php?year=2010",
     "\"Single-year report - all denominations\" tool, row for \"Church of Jesus Christ of Latter-day Saints, The\"; this is the same official 2010 U.S. Religion Census denomination table also published in print/PDF form",
     "Congregations reported this year: 13,601. The direct PDF URL given in the task brief (2010_US_Religion_Census.pdf) returned a 404 during research; this figure was instead confirmed via USRC's own dynamic report tool, a first-party USRC data product. Numerically identical to the Church Almanac's reported year-end-2010/Jan-1-2011 figure in church_almanac_usa_membership.csv -- not reconciled here, just noted."],

    ["2020","6721031","United States (national total)","adherents","",
     "2020", SRC_CENSUS, "https://www.usreligioncensus.org/sites/default/files/2023-06/2020_USRC_Group_Detail.xlsx",
     "Sheet \"2020 Group by Nation\", row Group Code 151, \"Church of Jesus Christ of Latter-day Saints\" (file updated 2023-06-23 per the site)",
     "Congregations reported this year: 14,567. Adherents as % of total US adherents: 4.17%; as % of total US population: 2.03%. Denomination label in this file omits \"The\" and the trailing comma used in earlier years' labels but refers to the same entity."],
]
write_csv("us_religion_census_lds_membership.csv", census_rows)

print("DONE")
