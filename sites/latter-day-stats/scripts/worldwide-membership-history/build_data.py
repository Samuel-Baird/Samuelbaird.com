"""
Builds the full worldwide Church membership series, 1830-2025 - the
site's second "mixed data" entry. Unlike the U.S.-only timeline
(scripts/us-membership-growth-2000-2025/), this one has NO gaps: every
year from the Church's 1830 founding onward is documented in a single
coherent source lineage, per Wikipedia's "Membership history of the
Church of Jesus Christ of Latter-day Saints" article, itself sourced to
"the 2013 Church Almanac" for 1830-2011 and the Church's own annual
statistical reports for 2012-2025. All 196 values below were transcribed
directly from that article's own table (year-end figures; 1830 uses the
Dec. 31, 1830 figure of 280, not the Apr. 6, 1830 organizing-day figure of
6, so the series stays one-figure-per-calendar-year throughout).

2025's figure (17,887,212) independently matches the Church's own current
newsroom country page (facts-and-statistics/country/united-states and
the worldwide facts-and-statistics page), fetched separately - a real
cross-check, not just copied from one source twice.

Usage: python scripts/worldwide-membership-history/build_data.py
"""
import json

MEMBERSHIP_BY_YEAR = {
    1830: 280, 1831: 680, 1832: 2661, 1833: 3140, 1834: 4372, 1835: 8835,
    1836: 13293, 1837: 16282, 1838: 17881, 1839: 16460, 1840: 16865,
    1841: 19856, 1842: 23564, 1843: 25980, 1844: 26146, 1845: 30332,
    1846: 33993, 1847: 34694, 1848: 40477, 1849: 48160, 1850: 51839,
    1851: 52165, 1852: 52640, 1853: 64154, 1854: 68429, 1855: 63974,
    1856: 63881, 1857: 55236, 1858: 55755, 1859: 57038, 1860: 61082,
    1861: 66211, 1862: 68780, 1863: 71770, 1864: 74348, 1865: 76771,
    1866: 77884, 1867: 81124, 1868: 84622, 1869: 88432, 1870: 90130,
    1871: 95596, 1872: 98152, 1873: 101538, 1874: 103916, 1875: 107167,
    1876: 111111, 1877: 115065, 1878: 125046, 1879: 128386, 1880: 133628,
    1881: 140733, 1882: 145604, 1883: 151593, 1884: 158242, 1885: 164130,
    1886: 166653, 1887: 173029, 1888: 180294, 1889: 183144, 1890: 188263,
    1891: 195445, 1892: 200961, 1893: 214534, 1894: 222369, 1895: 231116,
    1896: 241427, 1897: 255736, 1898: 267251, 1899: 271681, 1900: 283765,
    1901: 292931, 1902: 299105, 1903: 304901, 1904: 324289, 1905: 332048,
    1906: 345014, 1907: 357913, 1908: 371472, 1909: 377279, 1910: 398478,
    1911: 407291, 1912: 417555, 1913: 431607, 1914: 454718, 1915: 466238,
    1916: 477321, 1917: 488038, 1918: 495962, 1919: 507961, 1920: 525987,
    1921: 548803, 1922: 566358, 1923: 575896, 1924: 597861, 1925: 613572,
    1926: 623909, 1927: 644745, 1928: 655686, 1929: 663652, 1930: 670017,
    1931: 688435, 1932: 703949, 1933: 717619, 1934: 730738, 1935: 746384,
    1936: 760690, 1937: 767752, 1938: 784764, 1939: 803528, 1940: 862664,
    1941: 892080, 1942: 917715, 1943: 937050, 1944: 954004, 1945: 979454,
    1946: 996505, 1947: 1016170, 1948: 1041970, 1949: 1078671, 1950: 1111314,
    1951: 1147157, 1952: 1189053, 1953: 1246362, 1954: 1302240, 1955: 1357274,
    1956: 1416731, 1957: 1488314, 1958: 1555799, 1959: 1616088, 1960: 1693180,
    1961: 1823661, 1962: 1965786, 1963: 2117451, 1964: 2234916, 1965: 2395932,
    1966: 2480899, 1967: 2614340, 1968: 2684073, 1969: 2807456, 1970: 2930810,
    1971: 3090953, 1972: 3218908, 1973: 3306658, 1974: 3409987, 1975: 3572202,
    1976: 3742749, 1977: 3969220, 1978: 4166854, 1979: 4404121, 1980: 4639822,
    1981: 4920449, 1982: 5162619, 1983: 5351724, 1984: 5641054, 1985: 5919483,
    1986: 6166974, 1987: 6394314, 1988: 6721210, 1989: 7308444, 1990: 7761179,
    1991: 8089848, 1992: 8404087, 1993: 8689168, 1994: 9024368, 1995: 9338859,
    1996: 9692441, 1997: 10071783, 1998: 10354241, 1999: 10752986, 2000: 11068861,
    2001: 11394522, 2002: 11721548, 2003: 11985254, 2004: 12275822, 2005: 12560869,
    2006: 12868606, 2007: 13193999, 2008: 13508509, 2009: 13824854, 2010: 14131467,
    2011: 14441346, 2012: 14782473, 2013: 15082028, 2014: 15372337, 2015: 15634199,
    2016: 15882417, 2017: 16118169, 2018: 16313735, 2019: 16565036, 2020: 16663663,
    2021: 16805400, 2022: 17002461, 2023: 17255394, 2024: 17509781, 2025: 17887212,
}


def main():
    years = sorted(MEMBERSHIP_BY_YEAR)
    out = {
        "source": "Wikipedia, \"Membership history of the Church of Jesus Christ of "
                  "Latter-day Saints\" (year-end figures), itself sourced to the 2013 "
                  "Church Almanac for 1830-2011 and the Church's own annual statistical "
                  "reports for 2012-2025.",
        "method": "Complete year-end series, no gaps or interpolation - every year from "
                  "the Church's 1830 founding is documented in this source lineage. "
                  "2025's figure independently matches the Church's own current newsroom "
                  "statistics page.",
        "year_order": years,
        "series": {str(y): {"members": MEMBERSHIP_BY_YEAR[y], "status": "reported"} for y in years},
    }
    with open("docs/datasets/worldwide-membership-history/membership-by-year.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"{years[0]}  {MEMBERSHIP_BY_YEAR[years[0]]:>12,}")
    print(f"1947  {MEMBERSHIP_BY_YEAR[1947]:>12,}  (crossed 1 million)")
    print(f"2000  {MEMBERSHIP_BY_YEAR[2000]:>12,}")
    print(f"{years[-1]}  {MEMBERSHIP_BY_YEAR[years[-1]]:>12,}")
    print(f"\n{len(years)} years, {years[0]}-{years[-1]}")
    print("Wrote docs/datasets/worldwide-membership-history/membership-by-year.json")


if __name__ == "__main__":
    main()
