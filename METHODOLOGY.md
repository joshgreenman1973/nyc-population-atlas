# Methodology — NYC Population Atlas

A single page that breaks down New York City's population as many ways as the
census lets you. Every figure is traceable to a public U.S. Census Bureau
table. Nothing is estimated or invented by hand.

## Sources

| Data | Source |
|------|--------|
| All demographic, social, economic and housing breakdowns | U.S. Census Bureau, **American Community Survey (ACS) 2020–2024 5-year estimates**, via `api.census.gov` |
| Population timeline, 1790–2020 | U.S. Census Bureau **decennial census** counts (modern five-borough area); NYC Department of City Planning historical population tables |
| Borough land areas (for density) | U.S. Census Bureau / NYC Department of City Planning land-area figures (square miles) |
| Current unemployment rate | **U.S. Bureau of Labor Statistics**, Local Area Unemployment Statistics (LAUS), New York city, not seasonally adjusted — pulled live from the BLS public API. Used in Fig. 21 alongside the ACS figures because the ACS five-year *average* unemployment rate is inflated by the pandemic window; the BLS number is the latest month available. |
| Person-level car ownership | **Hunter College, Dept. of Urban Policy & Planning**, *"Car Ownership in NYC: By the Numbers"* (2024, from its *Shifting Gears* studio), analyzing ACS 2018–2022. Used in the car figure for the person-level statistic (54% of New Yorkers live in a vehicle-owning household even though only ~45% of households own a car, because car-owning households are larger), vehicles per household, and the citywide vehicle total. Household and borough car-ownership rates in that figure are the atlas's own ACS 2020–2024 tabulation, which matches Hunter's within a point. The "vehicles per household by household size" bars and the 50-year growth figures (vehicles +45% / population +11% / multi-car households +127%) are quoted from the same Hunter report. |
| Undocumented estimate | **NYC Mayor's Office of Immigrant Affairs** (ACS-based modeling): ~412,000 undocumented residents (2022), down from ~611,000 (2012). A modeled estimate, not a census count. See the note below. |

Five-year ACS estimates are used (rather than 1-year) because they are the most
reliable for small subgroups — specific countries of birth, languages spoken at
home, ancestry, and so on.

## Geography

- **Citywide** figures use the Census "place" geography for New York city
  (state 36, place 51000). This is used for all citywide totals **and** for every
  median (age, household income, per-capita income, gross rent, home value,
  household size) because medians cannot be summed or averaged across boroughs.
- **Borough** figures use the five county equivalents: Bronx (36005),
  Kings/Brooklyn (36047), New York/Manhattan (36061), Queens (36081),
  Richmond/Staten Island (36085).

## The immigration bar-chart race (Fig. 10)

Figure 10 animates foreign-born New Yorkers by country of birth, **1900–2023**,
using a curated historical series (`scripts/immigration_timeline.json`, ported
from the standalone *nyc-immigration-horserace* project). Sources by period:

- **1900, 1910** — 1910 U.S. Census, Vol. 1, Table 29 (New York city).
- **1920, 1930** — 1930 U.S. Census, Vol. II, Table 9 (New York, N.Y.).
- **1970–2000, 2011** — NYC Dept. of City Planning, *The Newest New Yorkers 2013*, Table 2-3.
- **2020** — Census ACS 2022 5-year, table B05006 (China = mainland + Hong Kong + Taiwan, to match City Planning's definition).
- **2023** — NYC Dept. of City Planning, *The Newest New Yorkers 2026*, Ch. 2; groups outside that report's top 20 from the 2023 ACS 1-year B05006 summed across the five boroughs.
- **1940, 1950, 1960** — not filled from primary sources; those cells are blank and the bars interpolate across them (shown as declining, not flat).

**The "fade."** Once a group's wave peaks and stops being replenished, its bar
both shrinks and dims. The dimming is a **visual device**, not a measured
statistic: the census counts immigrants by country of birth but cannot count
their U.S.-born children and grandchildren, who become simply "American" in the
birthplace tables. The fade marks a wave receding into later generations; it is
not a generation count.

## The neighborhood map (Fig. 03)

The distribution map shades New York's **262 Neighborhood Tabulation Areas
(NTAs, 2020 vintage)** by American Community Survey 2020–2024 estimates —
population density, median income, foreign-born share, race/ethnicity shares,
rent and car-ownership. Colors use **six equal-count (quantile) bins**, so each
shade holds a similar number of neighborhoods; adjacent shades can differ by
less than the survey's margin of error, so read the map for pattern, not
precision. Geometry is a simplified NTA boundary file; the per-NTA ACS values
are a prior NYC-data build in this workspace, joined by NTA code. Non-residential
NTAs (parks, airports, cemeteries) with little or no population appear grey.

## Undocumented residents (Fig. 09) — a modeled estimate, not a count

**The Census Bureau does not ask legal status, so no figure on this page counts
undocumented residents.** The ACS "not a U.S. citizen" category (Fig. 08) is
much larger and includes lawful permanent residents, students and visa holders —
it is not an undocumented count. Figure 09 instead reports a **modeled
estimate** from the **NYC Mayor's Office of Immigrant Affairs** (ACS-based
modeling): roughly **412,000 undocumented residents as of 2022, down from about
611,000 in 2012**. Such estimates vary widely by method and year; figures above
~600,000 in circulation generally describe **New York State**, not the city
(e.g., Migration Policy Institute). Treat the number as an order-of-magnitude
estimate with real uncertainty, not a precise total.

## Universes (denominators)

Percentages are taken against the correct base for each table, noted on each
section of the page:

- **Total population** — age & sex, race, Hispanic origin, nativity,
  citizenship, ancestry.
- **Foreign-born population** — region of birth, country of birth.
- **Population 5 and older** — language spoken at home, English proficiency.
- **Population 25 and older** — educational attainment.
- **Population 15 and older** — marital status.
- **Population 16 and older** — employment status.
- **Workers 16 and older** — means of transportation to work; travel time.
- **Population enrolled in K–12** — public vs private/parochial school (Fig. 18; "public" includes charter schools).
- **Employed civilians 16 and older** — occupation, industry, class of worker.
- **Population 1 year and older** — geographic mobility (who moved in the past year, and from where; "same county" = same borough in NYC).
- **Women 15–50** — births in the past 12 months.
- **Total civilian noninstitutionalized population** — health-insurance type (Fig. 35; "(only)" categories plus a "two or more types" group partition the whole population).
- **Households** — household type, household income, SNAP receipt, internet subscription and computer presence.
- **Occupied housing units** — tenure (owner/renter), vehicles available (car-free).
- **Renter-occupied units paying cash rent** — rent as a percentage of income (rent burden).
- **All housing units** — units in structure.
- **Civilian population 18+** — veteran status.
- **Civilian noninstitutionalized population** — disability, health-insurance coverage.

## Census tables used

`B01001` sex by age · `B01002` median age · `B02001` race · `B03002` Hispanic
origin by race · `B05001` citizenship · `B05002` nativity & region of birth ·
`B05006` place of birth for the foreign-born · `B04006` ancestry · `C16001`
language spoken at home · `B11001` household type · `B12001` marital status ·
`B14007` school enrollment · `B15003` educational attainment · `B08301` means of
transportation to work · `B08303` travel time to work · `B23025` employment
status · `B25003` tenure · `B25024` units in structure · `B19001` household
income · `B19013` median household income · `B19301` per-capita income ·
`B25064` median gross rent · `B25077` median home value · `B25010` average
household size · `B17001` poverty status · `B21001` veteran status · `B18101`
disability status · `B27010` health-insurance coverage · `B14002` school
enrollment by public/private type · `C24010` occupation · `C24030` industry ·
`B25044` vehicles available · `B25070` rent as a percentage of income ·
`B22010` receipt of SNAP/food stamps · `B24080` class of worker · `B07001`
geographic mobility in the past year · `B28002`/`B28003` internet and computer
access · `B13002` women 15–50 who gave birth · `B10051` grandparents raising
grandchildren.

## Derived measures

- **Density** = borough population ÷ borough land area (people per square mile).
- **Foreign-born %** = B05002 foreign-born ÷ (native + foreign-born).
- **Limited English** = sum of every "speak English less than 'very well'" line
  in C16001, ÷ population 5+.
- **Bachelor's or higher** = B15003 bachelor's + master's + professional +
  doctorate, ÷ population 25+.
- **Unemployment rate** = unemployed ÷ civilian labor force (B23025). Because this
  is a 2020–2024 average, it runs higher than the current single-year rate.
- **Poverty / child poverty** = B17001 below-poverty totals ÷ the matching
  population base.
- **Disability / uninsured rates** = summed "with a disability" / "no coverage"
  lines ÷ the table total.

## Caveats

- ACS figures are **survey estimates with margins of error**, not exact counts.
  Treat small differences between categories as noise.
- **Race and Hispanic origin overlap by design.** The census asks Hispanic/Latino
  origin separately from race, so Hispanic New Yorkers appear within every race
  group. The two sections are shown the way the census collects them.
- **Ancestry is optional and self-reported**, so its totals are smaller than the
  city's population; the page shows the top 20 and the two catch-all census
  categories ("Other groups", "Unclassified") are omitted from that ranking.
- The **1890 → 1900 jump** in the timeline reflects the 1898 consolidation of
  Greater New York (Brooklyn, Queens, the Bronx and Staten Island joining
  Manhattan), an administrative merger — not a real doubling in one decade.

## Reproducing the data

```bash
cd scripts
python3 fetch_acs.py <CENSUS_API_KEY>   # pulls every table -> data_raw.json + labels/
python3 build_data.py                   # transforms -> docs/data.json
```

A free Census API key is available at
<https://api.census.gov/data/key_signup.html>. The key is used only for the
one-time local pull and is never written into any output file or the published
page. `labels/` holds the official Census variable definitions used to map codes
to labels, kept in the repo for full reproducibility.
