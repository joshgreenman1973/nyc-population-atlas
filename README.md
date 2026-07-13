# NYC Population Atlas

**The people of New York City, counted every which way.** A single scrollable
page that breaks down the city's ~8.5 million residents 50 different ways — an
interactive 262-neighborhood map (with a 2010–2020 decennial growth layer), a
four-year population ledger (births/deaths/migration), commuter-adjusted
day-vs-night population, county-to-county migration flows, life expectancy by
community district, DOE school rosters vs the census survey, a modeled
undocumented-population estimate, baby names from the city's birth registry,
same-sex couples and group quarters from the 2020 census, the income ladder and
Gini index, building age, crowding, a licensed-dogs coda, and cuts by
age and borough, race and Hispanic origin, birthplace and citizenship, language,
ancestry, household, marital status, births and caregiving, education, public vs
private school, commute, work, occupation, industry and class of worker, income,
poverty, SNAP, rent burden, car ownership, housing, geographic mobility, digital
access and health-insurance type — plus three centuries of population history and
an animated 1900–2023 bar-chart race of foreign-born New Yorkers by country of
birth (Fig. 10, ported from the nyc-immigration-horserace project).

Almost every figure is Census ACS 2020–2024. Two exceptions: the timeline and
immigration race use decennial census + NYC City Planning data, and Fig. 21's
*current* unemployment rate is pulled live from the U.S. Bureau of Labor
Statistics. See [METHODOLOGY.md](METHODOLOGY.md).

Every number comes straight from the U.S. Census Bureau's American Community
Survey (2020–2024 5-year estimates) and decennial census. See
[METHODOLOGY.md](METHODOLOGY.md) for sources, universes, tables and caveats.

## Structure

```
docs/index.html   # the page (self-contained; loads data.json)
docs/data.json    # baked breakdowns the page renders
scripts/fetch_acs.py    # one-time pull of every ACS table -> data_raw.json
scripts/build_data.py   # transforms raw estimates (+ merges timeline) -> docs/data.json
scripts/labels/         # official Census variable definitions (for reproducibility)
scripts/immigration_timeline.json  # curated 1900-2023 country-of-birth series
scripts/build_map.py    # bakes docs/nyc-ntas.geojson (neighborhood map)
scripts/fetch_extras.py # PEP ledger, baby names, dog licenses, 2020 GQ/couples
docs/nyc-ntas.geojson   # 262 NTA polygons + ACS 2020-24 fields (the Fig. 03 map)
data_raw.json           # raw per-geography estimate values
```

## Build

```bash
cd scripts
python3 fetch_acs.py <CENSUS_API_KEY>
python3 build_data.py
```

## Publish

Served from `docs/` via GitHub Pages. No build step at runtime — the page is
static HTML that fetches the pre-baked `data.json`.

## Notes

- No external chart libraries; all charts (line, population pyramid, bar lists,
  split bars, stat tiles, borough cards) are hand-rendered in vanilla JS/SVG/CSS.
- Fonts: Fraunces (display + numerals) and Archivo, via Google Fonts.
- Assembled with AI assistance from public data; verify important figures against
  the source Census tables cited in the methodology.
