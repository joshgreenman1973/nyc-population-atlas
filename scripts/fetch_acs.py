"""
Fetch every ACS table this atlas needs, for New York City as a whole
(place:51000) and for each of the five boroughs (counties), and write the raw
estimate values to data_raw.json.

Source: U.S. Census Bureau, American Community Survey 2020-2024 5-year
estimates (api.census.gov). 5-year is used for stability across small
subgroups. Medians come from the citywide "place" geography because medians
cannot be summed across boroughs.

The API key is used here only, for a one-time local pull, and is NOT written
into any output. Run:  python3 fetch_acs.py <CENSUS_API_KEY>
"""
import json
import os
import sys
import time
import urllib.request
import urllib.parse

YEAR = "2024"
DATASET = "acs/acs5"
KEY = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CENSUS_API_KEY", "")
if not KEY:
    sys.exit("Usage: python3 fetch_acs.py <CENSUS_API_KEY>")

BASE = f"https://api.census.gov/data/{YEAR}/{DATASET}"

# Boroughs: county FIPS within state 36 (New York)
BOROUGHS = {
    "005": "Bronx",
    "047": "Brooklyn",      # Kings
    "061": "Manhattan",     # New York
    "081": "Queens",
    "085": "Staten Island", # Richmond
}
CITY_PLACE = "51000"

# Detailed tables pulled whole via group()
GROUP_TABLES = [
    "B01001",  # Sex by age
    "B02001",  # Race
    "B03002",  # Hispanic or Latino origin by race
    "B05001",  # Citizenship status
    "B05002",  # Place of birth by nativity and citizenship
    "B05006",  # Place of birth for the foreign-born population
    "B06009",  # Educational attainment by nativity (unused fallback)
    "B04006",  # People reporting ancestry
    "C16001",  # Language spoken at home
    "B11001",  # Household type
    "B12002",  # Sex by marital status by age (use B12001 subset)
    "B12001",  # Sex by marital status (15+)
    "B15003",  # Educational attainment (25+)
    "B14007",  # School enrollment by detailed level
    "B08301",  # Means of transportation to work
    "B08303",  # Travel time to work
    "B23025",  # Employment status (16+)
    "B25003",  # Tenure (owner/renter)
    "B25024",  # Units in structure
    "B19001",  # Household income brackets
    "B17001",  # Poverty status by sex by age
    "B21001",  # Veteran status (18+)
    "B18101",  # Disability status by sex by age
    "B27010",  # Health insurance coverage by type by age
    "B09019",  # Household relationship (detailed)
    "B25007",  # Tenure by age of householder
    "B14002",  # School enrollment by level by type (public/private)
    "C24010",  # Sex by occupation (employed 16+)
    "C24030",  # Sex by industry (employed 16+)
    "B25044",  # Tenure by vehicles available
    "B25070",  # Gross rent as a percentage of household income
    "B22010",  # Receipt of Food Stamps/SNAP by household
    "B24080",  # Sex by class of worker (employed 16+)
    "B07001",  # Geographical mobility in the past year by age
    "B28002",  # Presence and types of internet subscriptions
    "B28003",  # Presence of a computer and type of internet subscription
    "B13002",  # Women 15-50 who had a birth in the past 12 months
    "B10051",  # Grandparents living with own grandchildren under 18
]

# Single-value estimates (can't be summed for medians -> use the city place)
SINGLES = [
    "B01003_001E",  # Total population
    "B01002_001E",  # Median age
    "B19013_001E",  # Median household income
    "B19301_001E",  # Per capita income
    "B25077_001E",  # Median home value
    "B25064_001E",  # Median gross rent
    "B25010_001E",  # Average household size
    "B11001_001E",  # Total households
    "B25001_001E",  # Total housing units
    "B25002_003E",  # Vacant housing units
]


def parse_num(x):
    """ACS values are mostly ints but medians/averages are floats; -/null -> None."""
    if x is None:
        return None
    try:
        i = int(x)
        return i
    except (ValueError, TypeError):
        try:
            return float(x)
        except (ValueError, TypeError):
            return None


def fetch(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            if attempt == 3:
                raise
            print(f"  retry {attempt+1} after error: {e}", flush=True)
            time.sleep(2 + attempt * 2)


def get(get_clause, geo_for, geo_in):
    qs = urllib.parse.urlencode({"get": get_clause, "for": geo_for, "in": geo_in})
    return fetch(f"{BASE}?{qs}&key={KEY}")


def rows_to_dict(rows, id_col):
    """Return {geoid: {var: int_or_None}} for all E variables in the response."""
    headers = rows[0]
    out = {}
    idx = headers.index(id_col)
    for r in rows[1:]:
        geoid = r[idx]
        d = {}
        for j, h in enumerate(headers):
            if (h.endswith("E") and not h.endswith("EA") and h[0] in "BCS") or h in SINGLES:
                d[h] = parse_num(r[j])
        out[geoid] = d
    return out


def main():
    data = {"meta": {"year": YEAR, "dataset": DATASET}, "city": {}, "boroughs": {}}

    counties = ",".join(BOROUGHS.keys())

    # --- group tables ---
    for i, tbl in enumerate(GROUP_TABLES, 1):
        print(f"[{i}/{len(GROUP_TABLES)}] group({tbl})", flush=True)
        # city (place)
        city = get(f"group({tbl})", f"place:{CITY_PLACE}", "state:36")
        cd = rows_to_dict(city, "place")
        data["city"].update(cd.get(CITY_PLACE, {}))
        # boroughs (counties)
        bor = get(f"group({tbl})", f"county:{counties}", "state:36")
        bd = rows_to_dict(bor, "county")
        for fips, name in BOROUGHS.items():
            data["boroughs"].setdefault(name, {}).update(bd.get(fips, {}))

    # --- single-value estimates ---
    print("singles", flush=True)
    getc = ",".join(["NAME"] + SINGLES)
    city = get(getc, f"place:{CITY_PLACE}", "state:36")
    cd = rows_to_dict(city, "place")
    data["city"].update(cd.get(CITY_PLACE, {}))
    bor = get(getc, f"county:{counties}", "state:36")
    bd = rows_to_dict(bor, "county")
    for fips, name in BOROUGHS.items():
        data["boroughs"].setdefault(name, {}).update(bd.get(fips, {}))

    out_path = os.path.join(os.path.dirname(__file__), "..", "data_raw.json")
    with open(out_path, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    print(f"wrote {out_path}: city vars={len(data['city'])}", flush=True)


if __name__ == "__main__":
    main()
