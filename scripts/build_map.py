"""
Bake a lean neighborhood (NTA) GeoJSON for the atlas's distribution map.

Geometry: NYC Neighborhood Tabulation Areas (2020), simplified.
Data: per-NTA American Community Survey 2020-2024 tabulations (population,
density, income, race/ethnicity, foreign-born, rent, vehicles), joined by NTA
code. Both inputs are prior NYC-data builds in this workspace; only the fields
the map actually renders are kept, and coordinates are rounded, to keep the
published file small.

Output: docs/nyc-ntas.geojson
"""
import json
import os

HERE = os.path.dirname(__file__)
EXP = os.path.abspath(os.path.join(HERE, "..", ".."))

GEOM = os.path.join(EXP, "nyc-data", "crime-per-walker", "nta_simplified.geojson")
DATA = os.path.join(EXP, "nyc-population-map", "docs", "ntas.geojson")

# Fields the map can shade (kept lean); label + display handled on the page.
FIELDS = [
    "pop_total", "pop_density", "median_hh_income", "median_age",
    "pct_foreign_born", "pct_hispanic", "pct_black_nh", "pct_asian_nh",
    "pct_white_nh", "median_gross_rent", "pct_no_vehicle", "pct_poverty",
]


def round_coords(obj, nd=5):
    if isinstance(obj, list):
        if obj and isinstance(obj[0], (int, float)):
            return [round(obj[0], nd), round(obj[1], nd)]
        return [round_coords(x, nd) for x in obj]
    return obj


def main():
    geom = json.load(open(GEOM))
    data = json.load(open(DATA))
    by_code = {f["properties"]["geoid"]: f["properties"] for f in data["features"]}

    out_features = []
    for f in geom["features"]:
        code = f["properties"]["nta"]
        src = by_code.get(code)
        if not src:
            continue
        props = {"nta": src.get("nta"), "borough": src.get("borough")}
        for k in FIELDS:
            v = src.get(k)
            props[k] = round(v, 1) if isinstance(v, float) else v
        out_features.append({
            "type": "Feature",
            "properties": props,
            "geometry": {"type": f["geometry"]["type"],
                         "coordinates": round_coords(f["geometry"]["coordinates"])},
        })

    out = {"type": "FeatureCollection", "features": out_features}
    out_path = os.path.join(HERE, "..", "docs", "nyc-ntas.geojson")
    with open(out_path, "w") as fh:
        json.dump(out, fh, separators=(",", ":"))
    sz = os.path.getsize(out_path)
    print(f"wrote {out_path}: {len(out_features)} NTAs, {sz//1024} KB")


if __name__ == "__main__":
    main()
