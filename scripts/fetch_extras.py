"""
Fetch the atlas's non-ACS official extras into scripts/extras.json:

1. pep   — U.S. Census Bureau Population Estimates Program (vintage 2024),
           components of change (births, deaths, international & domestic
           migration) summed across the five boroughs, July 2020 -> July 2024.
           Source CSV: co-est2024-alldata.csv (census.gov).
2. names — NYC DOHMH "Popular Baby Names" (civil birth registration),
           NYC Open Data 25th-nujf. Top names, latest available year.
3. dogs  — NYC DOHMH Dog Licensing dataset, NYC Open Data nu7n-tubp.
           Licenses ISSUED in the latest complete year (the dataset repeats
           rows across annual extracts, so raw row counts double-count).
4. gq    — 2020 Decennial Census (DHC table P18): group-quarters population
           by major type, summed across sex and age, NYC place 51000.

Run: python3 fetch_extras.py <CENSUS_API_KEY>
"""
import csv
import io
import json
import os
import sys
import urllib.parse
import urllib.request

KEY = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CENSUS_API_KEY", "")
HERE = os.path.dirname(__file__)
BOROS = {"005", "047", "061", "081", "085"}


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "nyc-population-atlas/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def soda(dataset, query):
    url = f"https://data.cityofnewyork.us/resource/{dataset}.json?{urllib.parse.urlencode(query)}"
    return json.loads(get(url))


def fetch_pep():
    raw = get("https://www2.census.gov/programs-surveys/popest/datasets/"
              "2020-2024/counties/totals/co-est2024-alldata.csv")
    rows = csv.DictReader(io.StringIO(raw.decode("latin-1")))
    years = ["2021", "2022", "2023", "2024"]  # 2020 column is a partial (Apr-Jul) period
    tot = {k: 0 for k in ["births", "deaths", "intl", "domestic"]}
    by_year = {y: {k: 0 for k in tot} for y in years}
    pop2024 = pop2020 = 0
    for r in rows:
        if r["STATE"] == "36" and r["COUNTY"] in BOROS:
            pop2024 += int(r["POPESTIMATE2024"])
            pop2020 += int(r["POPESTIMATE2020"])
            for y in years:
                vals = {"births": int(r[f"BIRTHS{y}"]), "deaths": int(r[f"DEATHS{y}"]),
                        "intl": int(r[f"INTERNATIONALMIG{y}"]),
                        "domestic": int(r[f"DOMESTICMIG{y}"])}
                for k, v in vals.items():
                    tot[k] += v
                    by_year[y][k] += v
    return {"period": "July 2020 – July 2024", "vintage": 2024,
            "pop2020": pop2020, "pop2024": pop2024,
            "cumulative": tot, "byYear": by_year}


def fetch_names():
    rows = soda("25th-nujf", {"$limit": "60000"})
    latest = max(int(r["brth_yr"]) for r in rows)
    agg = {}
    for r in rows:
        if int(r["brth_yr"]) != latest:
            continue
        name = r["nm"].strip().title()
        sex = r["gndr"].strip().upper()[:1]
        agg.setdefault(sex, {})
        agg[sex][name] = agg[sex].get(name, 0) + int(r["cnt"])
    out = {"year": latest}
    for sex, label in (("F", "girls"), ("M", "boys")):
        top = sorted(agg.get(sex, {}).items(), key=lambda kv: -kv[1])[:10]
        out[label] = [{"label": n, "value": c} for n, c in top]
    return out


def fetch_dogs():
    yr_rows = soda("nu7n-tubp", {
        "$select": "date_extract_y(licenseissueddate) as y, count(1) as n",
        "$group": "y", "$order": "y DESC", "$limit": "30"})
    years = sorted(int(r["y"]) for r in yr_rows if r.get("y"))
    latest = years[-2] if len(years) > 1 else years[-1]  # last COMPLETE year
    where = (f"licenseissueddate between '{latest}-01-01T00:00:00' "
             f"and '{latest}-12-31T23:59:59'")
    total = int(soda("nu7n-tubp", {"$select": "count(1) as n", "$where": where})[0]["n"])
    junk = "('UNKNOWN','NAME NOT PROVIDED','NAME','NONE','N/A','.')"
    names = soda("nu7n-tubp", {
        "$select": "upper(animalname) as nm, count(1) as n",
        "$where": where + f" AND upper(animalname) not in {junk} AND animalname is not null",
        "$group": "nm", "$order": "n DESC", "$limit": "10"})
    breeds = soda("nu7n-tubp", {
        "$select": "breedname, count(1) as n",
        "$where": where + " AND breedname is not null AND upper(breedname) != 'UNKNOWN'",
        "$group": "breedname", "$order": "n DESC", "$limit": "10"})
    return {"year": latest, "issued": total,
            "names": [{"label": r["nm"].title(), "value": int(r["n"])} for r in names],
            "breeds": [{"label": r["breedname"], "value": int(r["n"])} for r in breeds]}


def fetch_gq():
    url = ("https://api.census.gov/data/2020/dec/dhc?get=group(P18)"
           f"&for=place:51000&in=state:36&key={KEY}")
    rows = json.loads(get(url))
    headers, vals = rows[0], rows[1]
    labels = json.loads(get("https://api.census.gov/data/2020/dec/dhc/groups/P18.json"))["variables"]
    NICE = [
        ("Correctional facilities for adults", "Adult correctional facilities"),
        ("Juvenile facilities", "Juvenile facilities"),
        ("Nursing facilities", "Nursing facilities"),
        ("Other institutional facilities", "Other institutional"),
        ("College/University student housing", "College dorms"),
        ("Military quarters", "Military quarters"),
        ("Other noninstitutional facilities", "Other group housing (incl. shelters)"),
    ]
    sums = {}
    total = 0
    for h, v in zip(headers, vals):
        if not (h.startswith("P18_") and h.endswith("N")):
            continue
        lab = labels[h]["label"]
        if h == "P18_001N":
            total = int(v)
        for needle, nice in NICE:
            if lab.split("!!")[-1].startswith(needle):
                sums[nice] = sums.get(nice, 0) + int(v)
    types = sorted(({"label": k, "value": v} for k, v in sums.items()),
                   key=lambda x: -x["value"])
    return {"total2020": total, "types": types,
            "source": "2020 Decennial Census, DHC table P18"}


def fetch_couples():
    url = ("https://api.census.gov/data/2020/dec/dhc?get="
           "PCT15_001N,PCT15_003N,PCT15_004N,PCT15_005N,PCT15_006N,"
           "PCT15_008N,PCT15_009N,PCT15_010N,PCT15_011N"
           f"&for=place:51000&in=state:36&key={KEY}")
    rows = json.loads(get(url))
    d = dict(zip(rows[0], [int(x) for x in rows[1][:-2]] + rows[1][-2:]))
    return {
        "marriedOpposite": d["PCT15_003N"], "marriedSame": d["PCT15_004N"],
        "cohabOpposite": d["PCT15_008N"], "cohabSame": d["PCT15_009N"],
        "sameSexTotal": d["PCT15_004N"] + d["PCT15_009N"],
        "maleMale": d["PCT15_005N"] + d["PCT15_010N"],
        "femaleFemale": d["PCT15_006N"] + d["PCT15_011N"],
        "source": "2020 Decennial Census, DHC table PCT15",
    }


def main():
    out = {}
    for key, fn in [("pep", fetch_pep), ("names", fetch_names),
                    ("dogs", fetch_dogs), ("gq", fetch_gq),
                    ("couples", fetch_couples)]:
        print(f"fetching {key}...", flush=True)
        out[key] = fn()
    path = os.path.join(HERE, "extras.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"wrote {path}")
    print("pep cumulative:", out["pep"]["cumulative"])
    print("names", out["names"]["year"], ":",
          out["names"]["girls"][0], out["names"]["boys"][0])
    print("dogs", out["dogs"]["year"], "issued:", out["dogs"]["issued"],
          "top:", out["dogs"]["names"][0])
    print("gq total:", out["gq"]["total2020"], "types:",
          [(t["label"], t["value"]) for t in out["gq"]["types"]])


if __name__ == "__main__":
    main()
