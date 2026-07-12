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
- **Households** — household type, household income.
- **Occupied housing units** — tenure (owner/renter).
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
disability status · `B27010` health-insurance coverage.

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
