"""
Transform data_raw.json (raw ACS estimate values) into data.json: clean,
labeled population breakdowns the atlas page renders.

All ACS figures are 2020-2024 5-year estimates for New York City
(place:51000) and its five boroughs. Historical decennial counts and borough
land areas are hardcoded from the sources cited in METHODOLOGY.md.
"""
import json
import os
import urllib.request

HERE = os.path.dirname(__file__)
RAW = json.load(open(os.path.join(HERE, "..", "data_raw.json")))
LABELS = {}
for fn in os.listdir(os.path.join(HERE, "labels")):
    if fn.endswith(".json"):
        LABELS[fn[:-5]] = json.load(open(os.path.join(HERE, "labels", fn)))["variables"]

CITY = RAW["city"]
BORO = RAW["boroughs"]


def v(code):
    return CITY.get(code) or 0


def lbl(code):
    tbl = code.split("_")[0]
    return LABELS[tbl][code]["label"].replace("Estimate!!", "").replace("Total:!!", "").rstrip(":")


def series(codes):
    return [{"label": lbl(c), "value": v(c)} for c in codes]


# ---- headline totals ----
totals = {
    "population": v("B01003_001E"),
    "medianAge": v("B01002_001E"),
    "medianHHIncome": v("B19013_001E"),
    "perCapitaIncome": v("B19301_001E"),
    "medianHomeValue": v("B25077_001E"),
    "medianGrossRent": v("B25064_001E"),
    "avgHHSize": RAW["city"].get("B25010_001E"),
    "households": v("B11001_001E"),
    "housingUnits": v("B25001_001E"),
    "vacantUnits": v("B25002_003E"),
}

# ---- boroughs ----
LAND_SQMI = {  # NYC DCP / Census land area, square miles
    "Bronx": 42.10, "Brooklyn": 69.38, "Manhattan": 22.66,
    "Queens": 108.53, "Staten Island": 58.37,
}
boroughs = []
for name, d in BORO.items():
    pop = d.get("B01003_001E") or 0
    boroughs.append({
        "name": name,
        "population": pop,
        "landSqMi": LAND_SQMI[name],
        "density": round(pop / LAND_SQMI[name]),
        "medianAge": d.get("B01002_001E"),
        "medianHHIncome": d.get("B19013_001E"),
        "foreignBorn": d.get("B05002_013E") or 0,
        "medianRent": d.get("B25064_001E"),
    })
boroughs.sort(key=lambda b: -b["population"])

# ---- decennial history (US Census / NYC Dept of City Planning) ----
history = [
    [1790, 33131], [1800, 60515], [1810, 96373], [1820, 123706],
    [1830, 202589], [1840, 312710], [1850, 515547], [1860, 813669],
    [1870, 942292], [1880, 1206299], [1890, 1515301], [1900, 3437202],
    [1910, 4766883], [1920, 5620048], [1930, 6930446], [1940, 7454995],
    [1950, 7891957], [1960, 7781984], [1970, 7894862], [1980, 7071639],
    [1990, 7322564], [2000, 8008278], [2010, 8175133], [2020, 8804190],
]
history = [{"year": y, "population": p} for y, p in history]

# ---- sex by age (pyramid, 5-year bands) ----
# Male base codes 3..25, Female 27..49; combine split bands into standard 5s
BANDS = [
    ("0-4",   ["003"], ["027"]),
    ("5-9",   ["004"], ["028"]),
    ("10-14", ["005"], ["029"]),
    ("15-19", ["006", "007"], ["030", "031"]),
    ("20-24", ["008", "009", "010"], ["032", "033", "034"]),
    ("25-29", ["011"], ["035"]),
    ("30-34", ["012"], ["036"]),
    ("35-39", ["013"], ["037"]),
    ("40-44", ["014"], ["038"]),
    ("45-49", ["015"], ["039"]),
    ("50-54", ["016"], ["040"]),
    ("55-59", ["017"], ["041"]),
    ("60-64", ["018", "019"], ["042", "043"]),
    ("65-69", ["020", "021"], ["044", "045"]),
    ("70-74", ["022"], ["046"]),
    ("75-79", ["023"], ["047"]),
    ("80-84", ["024"], ["048"]),
    ("85+",   ["025"], ["049"]),
]
sex_age = []
for band, m, f in BANDS:
    male = sum(v(f"B01001_{c}E") for c in m)
    female = sum(v(f"B01001_{c}E") for c in f)
    sex_age.append({"band": band, "male": male, "female": female})
total_male = v("B01001_002E")
total_female = v("B01001_026E")

# ---- race & ethnicity (B03002) ----
race = [
    {"label": "White", "value": v("B03002_003E")},
    {"label": "Black", "value": v("B03002_004E")},
    {"label": "Asian", "value": v("B03002_006E")},
    {"label": "Some other race", "value": v("B03002_008E")},
    {"label": "Two or more races", "value": v("B03002_009E")},
    {"label": "American Indian / Alaska Native", "value": v("B03002_005E")},
    {"label": "Native Hawaiian / Pacific Islander", "value": v("B03002_007E")},
]
race.sort(key=lambda x: -x["value"])
hispanic = [
    {"label": "Hispanic or Latino (any race)", "value": v("B03002_012E")},
    {"label": "Not Hispanic or Latino", "value": v("B03002_002E")},
]

# ---- nativity & citizenship (B05001) ----
citizenship = [
    {"label": "Born in the United States", "value": v("B05001_002E")},
    {"label": "Born in Puerto Rico / U.S. territories", "value": v("B05001_003E")},
    {"label": "Born abroad to American parents", "value": v("B05001_004E")},
    {"label": "Naturalized U.S. citizen", "value": v("B05001_005E")},
    {"label": "Not a U.S. citizen", "value": v("B05001_006E")},
]
foreign_born = v("B05002_013E")
native = v("B05002_002E")
nativity = {"native": native, "foreignBorn": foreign_born,
            "foreignBornPct": round(100 * foreign_born / (native + foreign_born), 1)}

# region of birth for the foreign-born
region_birth = [
    {"label": "Latin America", "value": v("B05002_019E") + v("B05002_026E")},
    {"label": "Asia", "value": v("B05002_016E") + v("B05002_023E")},
    {"label": "Europe", "value": v("B05002_015E") + v("B05002_022E")},
    {"label": "Africa", "value": v("B05002_017E") + v("B05002_024E")},
    {"label": "Northern America", "value": v("B05002_020E") + v("B05002_027E")},
    {"label": "Oceania", "value": v("B05002_018E") + v("B05002_025E")},
]
region_birth.sort(key=lambda x: -x["value"])

# ---- country of birth: top leaves of B05006 ----
def leaves(table, mindepth=2):
    out = []
    for code, meta in LABELS[table].items():
        if not code.endswith("E") or code == "NAME":
            continue
        label = meta["label"]
        if label.rstrip().endswith(":"):
            continue  # not a leaf
        depth = label.count("!!")
        if depth < mindepth:
            continue
        name = label.split("!!")[-1].rstrip(":")
        out.append({"label": name, "value": v(code)})
    out.sort(key=lambda x: -x["value"])
    return out

COUNTRY_CLEAN = {
    "China, excluding Hong Kong and Taiwan": "China",
    "Other Eastern Africa": "Other Eastern Africa",
}
ANCESTRY_SKIP = {"Other groups", "Unclassified or not reported"}
country_birth = [{"label": COUNTRY_CLEAN.get(c["label"], c["label"]), "value": c["value"]}
                 for c in leaves("B05006")][:20]
ancestry = [c for c in leaves("B04006", mindepth=1) if c["label"] not in ANCESTRY_SKIP][:20]

# ---- language spoken at home (5+) ----
lang_total = v("C16001_001E")
language = [
    {"label": "Only English", "value": v("C16001_002E")},
    {"label": "Spanish", "value": v("C16001_003E")},
    {"label": "Chinese", "value": v("C16001_021E")},
    {"label": "Russian / Polish / Slavic", "value": v("C16001_012E")},
    {"label": "Other Indo-European", "value": v("C16001_015E")},
    {"label": "French / Haitian Creole", "value": v("C16001_006E")},
    {"label": "Other Asian / Pacific", "value": v("C16001_030E")},
    {"label": "Korean", "value": v("C16001_018E")},
    {"label": "Bengali / other South Asian is in Other Indo-Euro", "value": 0},
    {"label": "Arabic", "value": v("C16001_033E")},
    {"label": "Tagalog", "value": v("C16001_027E")},
    {"label": "German / West Germanic", "value": v("C16001_009E")},
    {"label": "Vietnamese", "value": v("C16001_024E")},
    {"label": "Other / unspecified", "value": v("C16001_036E")},
]
language = [x for x in language if x["value"] > 0]
language.sort(key=lambda x: -x["value"])
# limited English proficiency: sum of "less than very well"
lep = sum(v(f"C16001_{c}E") for c in
          ["005", "008", "011", "014", "017", "020", "023", "026", "029", "032", "035", "038"])
english = {"total5plus": lang_total, "onlyEnglish": v("C16001_002E"),
           "limitedEnglish": lep,
           "limitedEnglishPct": round(100 * lep / lang_total, 1)}

# ---- households (B11001) ----
household = [
    {"label": "Married-couple family", "value": v("B11001_003E")},
    {"label": "Single householder, living alone", "value": v("B11001_008E")},
    {"label": "Female householder, no spouse", "value": v("B11001_006E")},
    {"label": "Nonfamily, not alone (roommates)", "value": v("B11001_009E")},
    {"label": "Male householder, no spouse", "value": v("B11001_005E")},
]
household.sort(key=lambda x: -x["value"])

# ---- marital status (15+) combine sexes ----
marital = [
    {"label": "Never married", "value": v("B12001_003E") + v("B12001_012E")},
    {"label": "Married, spouse present", "value": v("B12001_005E") + v("B12001_014E")},
    {"label": "Divorced", "value": v("B12001_010E") + v("B12001_019E")},
    {"label": "Widowed", "value": v("B12001_009E") + v("B12001_018E")},
    {"label": "Separated / spouse absent", "value": v("B12001_006E") + v("B12001_015E")},
]
marital.sort(key=lambda x: -x["value"])

# ---- education (25+) grouped ----
edu_total = v("B15003_001E")
lths = sum(v(f"B15003_{c:03d}E") for c in range(2, 17))
education = [
    {"label": "Less than high school", "value": lths},
    {"label": "High school graduate / GED", "value": v("B15003_017E") + v("B15003_018E")},
    {"label": "Some college / associate's", "value": v("B15003_019E") + v("B15003_020E") + v("B15003_021E")},
    {"label": "Bachelor's degree", "value": v("B15003_022E")},
    {"label": "Graduate or professional degree", "value": v("B15003_023E") + v("B15003_024E") + v("B15003_025E")},
]
bachelors_plus = v("B15003_022E") + v("B15003_023E") + v("B15003_024E") + v("B15003_025E")
edu_summary = {"pop25plus": edu_total, "bachelorsPlus": bachelors_plus,
               "bachelorsPlusPct": round(100 * bachelors_plus / edu_total, 1)}

# ---- commute to work ----
commute = [
    {"label": "Subway or elevated rail", "value": v("B08301_012E")},
    {"label": "Bus", "value": v("B08301_011E")},
    {"label": "Drove alone", "value": v("B08301_003E")},
    {"label": "Worked from home", "value": v("B08301_021E")},
    {"label": "Walked", "value": v("B08301_019E")},
    {"label": "Carpooled", "value": v("B08301_004E")},
    {"label": "Commuter rail", "value": v("B08301_013E")},
    {"label": "Taxi / ride-hailing", "value": v("B08301_016E")},
    {"label": "Bicycle", "value": v("B08301_018E")},
    {"label": "Ferry", "value": v("B08301_015E")},
]
commute.sort(key=lambda x: -x["value"])

# travel time to work
travel_time = series([f"B08303_{c:03d}E" for c in range(2, 14)])

# ---- employment (16+) ----
emp_total = v("B23025_001E")
employed = v("B23025_004E")
unemployed = v("B23025_005E")
labor_force = v("B23025_003E")
employment = {
    "pop16plus": emp_total,
    "employed": employed,
    "unemployed": unemployed,
    "notInLaborForce": v("B23025_007E"),
    "laborForceParticipation": round(100 * v("B23025_002E") / emp_total, 1),
    "unemploymentRate": round(100 * unemployed / labor_force, 1),
}

# ---- housing tenure ----
tenure = [
    {"label": "Renter-occupied", "value": v("B25003_003E")},
    {"label": "Owner-occupied", "value": v("B25003_002E")},
]
renter_pct = round(100 * v("B25003_003E") / v("B25003_001E"), 1)

# units in structure
units_struct = [
    {"label": "1-unit detached (house)", "value": v("B25024_002E")},
    {"label": "1-unit attached (rowhouse)", "value": v("B25024_003E")},
    {"label": "2 units", "value": v("B25024_004E")},
    {"label": "3-4 units", "value": v("B25024_005E")},
    {"label": "5-9 units", "value": v("B25024_006E")},
    {"label": "10-19 units", "value": v("B25024_007E")},
    {"label": "20-49 units", "value": v("B25024_008E")},
    {"label": "50+ units (highrise)", "value": v("B25024_009E")},
]

# ---- household income brackets ----
income = series([f"B19001_{c:03d}E" for c in range(2, 18)])

# ---- poverty ----
below = v("B17001_002E")
pov_total = v("B17001_001E")
# child poverty (under 18): male under5..16-17 = 004..009 ; female 018..023
child_below = sum(v(f"B17001_{c:03d}E") for c in [4, 5, 6, 7, 8, 9, 18, 19, 20, 21, 22, 23])
child_total = child_below + sum(v(f"B17001_{c:03d}E") for c in [33, 34, 35, 36, 37, 38, 47, 48, 49, 50, 51, 52])
poverty = {
    "belowPoverty": below,
    "povertyRate": round(100 * below / pov_total, 1),
    "childPovertyRate": round(100 * child_below / child_total, 1) if child_total else None,
}

# ---- veterans ----
veterans = {"count": v("B21001_002E"),
            "rate": round(100 * v("B21001_002E") / v("B21001_001E"), 1)}

# ---- disability ----
dis_codes = ["004", "007", "010", "013", "016", "019", "023", "026", "029", "032", "035", "038"]
with_dis = sum(v(f"B18101_{c}E") for c in dis_codes)
disability = {"count": with_dis,
              "rate": round(100 * with_dis / v("B18101_001E"), 1)}

# ---- health insurance ----
uninsured = v("B27010_017E") + v("B27010_033E") + v("B27010_050E") + v("B27010_066E")
health = {"uninsured": uninsured,
          "uninsuredRate": round(100 * uninsured / v("B27010_001E"), 1)}

# ---- school enrollment (3+) ----
enrolled_total = v("B14007_002E")
school = [
    {"label": "Nursery / preschool", "value": v("B14007_003E")},
    {"label": "Kindergarten", "value": v("B14007_004E")},
    {"label": "Grades 1-8", "value": sum(v(f"B14007_{c:03d}E") for c in range(5, 13))},
    {"label": "Grades 9-12", "value": sum(v(f"B14007_{c:03d}E") for c in range(13, 17))},
    {"label": "College (undergraduate)", "value": v("B14007_017E")},
    {"label": "Graduate / professional school", "value": v("B14007_018E")},
]

# ---- occupation (C24010, employed 16+) sum male+female (female offset 36) ----
occ = lambda m: v(f"C24010_{m:03d}E") + v(f"C24010_{m+36:03d}E")
occupation = [
    {"label": "Management, business, science & arts", "value": occ(3)},
    {"label": "Service", "value": occ(19)},
    {"label": "Sales & office", "value": occ(27)},
    {"label": "Natural resources, construction & maintenance", "value": occ(30)},
    {"label": "Production, transportation & material moving", "value": occ(34)},
]
occupation.sort(key=lambda x: -x["value"])

# ---- industry (C24030) sum male+female (female offset 27) ----
ind = lambda m: v(f"C24030_{m:03d}E") + v(f"C24030_{m+27:03d}E")
industry = [
    {"label": "Educational services, health care & social assistance", "value": ind(21)},
    {"label": "Professional, scientific & management", "value": ind(17)},
    {"label": "Retail trade", "value": ind(9)},
    {"label": "Finance, insurance & real estate", "value": ind(14)},
    {"label": "Arts, entertainment, recreation & food services", "value": ind(24)},
    {"label": "Transportation, warehousing & utilities", "value": ind(10)},
    {"label": "Construction", "value": ind(6)},
    {"label": "Information", "value": ind(13)},
    {"label": "Other services", "value": ind(27)},
    {"label": "Public administration", "value": ind(28)},
    {"label": "Manufacturing", "value": ind(7)},
    {"label": "Wholesale trade", "value": ind(8)},
    {"label": "Agriculture & mining", "value": ind(3)},
]
industry.sort(key=lambda x: -x["value"])

# ---- school type: public vs private, K-12 (B14002, female offset 24) ----
bpub = lambda m: v(f"B14002_{m:03d}E") + v(f"B14002_{m+24:03d}E")
levels = [("Kindergarten", 8, 9), ("Grades 1-4", 11, 12),
          ("Grades 5-8", 14, 15), ("Grades 9-12", 17, 18)]
by_level = [{"label": lab, "public": bpub(pu), "private": bpub(pr)} for lab, pu, pr in levels]
k12_pub = sum(l["public"] for l in by_level)
k12_priv = sum(l["private"] for l in by_level)
k12_total = k12_pub + k12_priv
# all enrolled 3+ (nursery through grad), public share of everything
all_pub = sum(bpub(m) for m in (5, 8, 11, 14, 17, 20, 23))
all_priv = sum(bpub(m) for m in (6, 9, 12, 15, 18, 21, 24))
school_type = {
    "k12Total": k12_total, "k12Public": k12_pub, "k12Private": k12_priv,
    "k12PublicShare": round(100 * k12_pub / k12_total, 1),
    "allEnrolled": all_pub + all_priv, "allPublic": all_pub,
    "allPublicShare": round(100 * all_pub / (all_pub + all_priv), 1),
    "byLevel": by_level,
}

# ---- rent burden (B25070) ----
rb_computed = v("B25070_001E") - v("B25070_011E")
burden30 = sum(v(f"B25070_{c:03d}E") for c in (7, 8, 9, 10))
burden50 = v("B25070_010E")
rent_burden = {
    "computed": rb_computed,
    "rate30": round(100 * burden30 / rb_computed, 1),
    "rate50": round(100 * burden50 / rb_computed, 1),
    "count30": burden30, "count50": burden50,
}

# ---- car ownership (B25044) — household vs person, and by borough ----
# Household-level car-free rate is the ACS measure. Hunter College's key point
# is that because car-owning households are LARGER, a slim majority of *people*
# live in a household with a vehicle even though a minority of households own one.
no_veh = v("B25044_003E") + v("B25044_010E")
car_by_boro = []
for name, bd in BORO.items():
    tot = bd.get("B25044_001E") or 0
    nov = (bd.get("B25044_003E") or 0) + (bd.get("B25044_010E") or 0)
    if tot:
        car_by_boro.append({"label": name, "value": round(100 * (1 - nov / tot), 1)})
car_by_boro.sort(key=lambda x: -x["value"])
car_free = {
    "count": no_veh,
    "rate": round(100 * no_veh / v("B25044_001E"), 1),          # % of households car-free
    "ownRate": round(100 * (1 - no_veh / v("B25044_001E")), 1),  # % of households with a car
    "byBorough": car_by_boro,
    # Sourced separately (different vintage) — attributed to Hunter on the page.
    "hunter": {
        "peopleWithVehiclePct": 54,
        "householdsWithVehiclePct": 45,
        "vehiclesPerHH": 0.62,
        "totalVehicles": 2060000,
        "dataYears": "2018–2022",
        "source": 'Hunter College Dept. of Urban Policy & Planning, '
                  '"Car Ownership in NYC: By the Numbers" (2024)',
    },
}

# ---- SNAP / food assistance (B22010) ----
snap_hh = v("B22010_002E")
snap = {"count": snap_hh, "rate": round(100 * snap_hh / v("B22010_001E"), 1)}

# ---- current labor market from the U.S. Bureau of Labor Statistics (LAUS) ----
def fetch_bls():
    try:
        body = json.dumps({"seriesid": [
            "LAUCT365100000000003",  # unemployment rate
            "LAUCT365100000000005",  # employment
            "LAUCT365100000000006",  # labor force
        ]}).encode()
        req = urllib.request.Request(
            "https://api.bls.gov/publicAPI/v1/timeseries/data/",
            data=body, headers={"Content-Type": "application/json"})
        r = json.load(urllib.request.urlopen(req, timeout=40))
        d = {s["seriesID"]: s["data"][0] for s in r["Results"]["series"]}
        rate = d["LAUCT365100000000003"]
        return {
            "unemploymentRate": float(rate["value"]),
            "period": f'{rate["periodName"]} {rate["year"]}',
            "employed": int(float(d["LAUCT365100000000005"]["value"])),
            "laborForce": int(float(d["LAUCT365100000000006"]["value"])),
            "source": "U.S. Bureau of Labor Statistics, Local Area Unemployment "
                      "Statistics (New York city, not seasonally adjusted)",
        }
    except Exception as e:  # noqa: BLE001
        print("BLS fetch failed:", e)
        return None
bls_labor = fetch_bls()

out = {
    "meta": {
        "source": "U.S. Census Bureau, American Community Survey 2020-2024 5-year estimates",
        "geography": "New York City (place 51000) and five boroughs (counties)",
        "historySource": "U.S. Census Bureau decennial counts; NYC Dept. of City Planning",
        "acsYear": RAW["meta"]["year"],
    },
    "totals": totals,
    "boroughs": boroughs,
    "history": history,
    "sexAge": {"bands": sex_age, "totalMale": total_male, "totalFemale": total_female},
    "race": race,
    "hispanic": hispanic,
    "citizenship": citizenship,
    "nativity": nativity,
    "regionOfBirth": region_birth,
    "countryOfBirth": country_birth,
    "ancestry": ancestry,
    "language": language,
    "english": english,
    "household": household,
    "marital": marital,
    "education": education,
    "eduSummary": edu_summary,
    "school": school,
    "commute": commute,
    "travelTime": travel_time,
    "employment": employment,
    "tenure": tenure,
    "renterPct": renter_pct,
    "unitsInStructure": units_struct,
    "income": income,
    "poverty": poverty,
    "veterans": veterans,
    "disability": disability,
    "health": health,
    "occupation": occupation,
    "industry": industry,
    "schoolType": school_type,
    "rentBurden": rent_burden,
    "carFree": car_free,
    "snap": snap,
    "blsLabor": bls_labor,
}

# ---- immigration timeline (bar-chart race) ----
# Curated historical country-of-birth series, 1900-2023, ported from the
# nyc-immigration-horserace project. Sources: 1910 & 1930 decennial census;
# NYC Dept. of City Planning "Newest New Yorkers" 2013 & 2026; ACS B05006.
tl_path = os.path.join(HERE, "immigration_timeline.json")
if os.path.exists(tl_path):
    tl = json.load(open(tl_path))
    out["immigrationTimeline"] = {
        "years": tl["years"],
        "countries": tl["countries"],
        "note": tl["meta"].get("note", ""),
        "caution": tl["meta"].get("caution", []),
    }
    print(f"immigration timeline: {len(tl['countries'])} countries, "
          f"{tl['years'][0]}-{tl['years'][-1]}")

out_path = os.path.join(HERE, "..", "docs", "data.json")
with open(out_path, "w") as f:
    json.dump(out, f, separators=(",", ":"))
print(f"wrote {out_path}")
print(f"population={totals['population']:,}  foreign-born={nativity['foreignBornPct']}%  "
      f"renters={renter_pct}%  bachelors+={edu_summary['bachelorsPlusPct']}%")
print("top countries:", ", ".join(f"{c['label']}" for c in country_birth[:5]))
print("top languages:", ", ".join(f"{c['label']}" for c in language[:5]))
print("top ancestry:", ", ".join(f"{c['label']}" for c in ancestry[:5]))
