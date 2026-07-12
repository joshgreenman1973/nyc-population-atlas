# NYC Population Atlas

**The people of New York City, counted every which way.** A single scrollable
page that breaks down the city's ~8.5 million residents 25 different ways — by
age and borough, race and Hispanic origin, birthplace and citizenship, language,
ancestry, household, marital status, education, commute, work, income, poverty,
housing and more — plus three centuries of population history and an animated
1900–2023 bar-chart race of foreign-born New Yorkers by country of birth
(Fig. 10, ported from the nyc-immigration-horserace project).

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
scripts/immigration_timeline.json  # curated 1900-2023 country-of-birth series (Fig. 10)
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
