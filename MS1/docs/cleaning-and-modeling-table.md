# Cleaning and modeling table

What we decided and what the notebook fixes. Code: `notebooks/01-cleaning-and-modeling-table.ipynb`. Output: `data/processed/modeling_table.csv`.

- **One row** = one driver in one race. Key: (`raceId`, `driverId`).
- **Target**: `podium` = 1 if `positionOrder <= 3`.
- **Cutoff**: every feature is known after qualifying and before the race starts.
- **Result**: 24,571 rows, 24 features, 13.7% podiums.

## 1. Decisions

**Rows**

- Train on all years. Later, compare against training from 1994 and from 2003 as an experiment.
- Same driver with several rows in a race (shared drives): keep the row with the lowest `positionOrder`.
- Two drivers sharing one car: keep both. Both count as podium finishers.
- Drop the Indianapolis 500 (1950–1960).
- Drop drivers who never started: `positionText` `F` (failed to qualify) or `W` (withdrew).
- Drop rows with `grid = 0` and 0 laps. They did not start either.
- `grid = 0` with laps is a pit-lane start: set `grid` to the last grid place in that race plus one. No separate flag.

**Split**

- By season: train up to 2019, validation 2020–2021, test 2022–2024.
- `year` is used for the split only. It is not a feature.

**Features**

- Constructors: use past performance, not identity. History follows `constructorId`, so a renamed team starts empty.
- Start position: keep both `grid_position` and `grid_position_relative`. Compare them by ablation later.
- Qualifying: `has_qualifying_data` is set per race, and is 0 only when the race has no qualifying data at all.
- Qualifying: use `grid_penalty_places` (grid minus qualifying position) instead of the qualifying position. It is 0 when there is no qualifying position.
- Circuits: keep `circuitId`, and add `circuit_podium_rate_for_grid_group`.
- Form windows: last 5 races for podium rate and average finish, last 10 for retirement rates. Starting values, to compare later.
- Standings: use the previous round of the same season. Points are divided by the leader's points.
- Standings: no row means 0 points and 0 wins. The position stays missing. At round 1 everyone has 0.
- Home race and mechanical retirements: use the same mappings as the data-engineering questions notebook.
- No sprint features.

**Other**

- Missing values stay empty in the saved table. They are filled in the modeling notebook, and any median, mean or mode is learned from training rows only.
- Sentinel and key checks run on all 14 tables, before the EDA. Type conversion only on the tables we use.
- Raw files are not changed. One `DATA_DIR` variable at the top for Kaggle.

## 2. Problems and fixes in the notebook

| # | Problem | Size | Fix |
|---|---------|------|-----|
| 1 | Spaces around column names and text in `constructor_results` and `constructor_standings` (our local copy) | 2 files | Strip spaces and quotes. |
| 2 | Missing values written as the text `\N` | 6 tables; 122,887 cells in `results` | Replace with `NaN`. |
| 3 | Empty cells in `qualifying` | `q2` 22, `q3` 46 | Already read as `NaN`. |
| 4 | Numbers and dates stored as text | 6 columns in `results`, `races.date`, `drivers.dob` | `to_numeric`, `to_datetime`. |
| 5 | Lap times stored as text (`1:26.572`) | `q1`, `q2`, `q3` | Convert to seconds. |
| 6 | One qualifying lap of 16:42.640 | 1 row | Set to missing. |
| 7 | Space around a nationality | 1 row | Strip. |
| 8 | Same driver twice in a race | 85 pairs, 91 rows dropped | Keep lowest `positionOrder`. 26,759 → 26,668 rows. |
| 9 | Two drivers in one car, both with the car's position | 18 races with 4 or 5 podium rows | Kept. |
| 10 | Indianapolis 500 has almost separate drivers | 381 rows | Dropped. → 26,287 rows. |
| 11 | Drivers who never started | 1,701 rows | Dropped. → 24,586 rows. |
| 12 | `grid = 0` and 0 laps | 15 rows | Dropped. → 24,571 rows. |
| 13 | `grid = 0` for pit-lane starts looks better than pole | 72 rows | Last grid place plus one. |
| 14 | `raceId` is not in time order (`raceId` 1 is a 2009 race) | all rows | Sort by `date`. |
| 15 | A row could see its own result in a form feature | all form features | `shift()` before every rolling or cumulative step. |
| 16 | Two cars per team: one car could see its teammate's result of the same race | constructor form | One row per team per race first, then look back. |
| 17 | Standings are post-race | all standings features | Join the previous round's row. |
| 18 | Points differ by season (a win is worth 8, 9, 10 or 25) | all seasons | Divide by the leader's points. |
| 19 | No standings row | 2,889 driver rows, 1,593 of them round 1 | 0 points and 0 wins. Position stays missing. |
| 20 | No constructors' championship before 1958 | 77% of 1950s rows | Constructor standings stay missing. |
| 21 | Nationality (`British`) and country (`UK`) do not match; `USA` and `United States` both used | 43 nationalities | Mapping dict; merge the two USA names. |
| 22 | No qualifying data for many races | 620 of 1,114 races | `has_qualifying_data` = 0. |
| 23 | Race has qualifying data but a driver has no row | 21 rows | `grid_penalty_places` = 0. |
| 24 | Grid and qualifying position are almost the same number | correlation 0.97 | Keep the difference (`grid_penalty_places`). |
| 25 | Drivers of the same race share a grid group | `circuit_podium_rate_for_grid_group` | Count per race first, then add up earlier races only. |
| 26 | Circuit with few past races gives a noisy rate | under 5 earlier races | Use the rate over all circuits. |

Primary keys (14 tables) and foreign keys (23 links) had no problems.

## 3. The saved table

**Keys (not features):** `raceId`, `driverId`, `constructorId`, `circuitId`, `year`, `round`, `date`, `split`.

| Group | Features |
|-------|----------|
| Grid | `grid_position`, `grid_position_relative`, `front_row_start` |
| Qualifying | `grid_penalty_places`, `qualifying_gap_to_pole_percent`, `has_qualifying_data` |
| Driver form | `driver_races_before`, `driver_podium_rate_last_5_races`, `driver_average_finish_last_5_races`, `driver_retirement_rate_last_10_races`, `driver_career_podium_rate`, `driver_podium_rate_at_circuit` |
| Constructor form | `constructor_podium_rate_last_5_races`, `constructor_average_finish_last_5_races`, `constructor_mechanical_retirement_rate_last_10_races` |
| Standings before the race | `driver_points_share_before_race`, `driver_standing_position_before_race`, `driver_season_wins_before_race`, `constructor_points_share_before_race`, `constructor_standing_position_before_race` |
| Context | `driver_age`, `home_race`, `season_progress`, `circuit_podium_rate_for_grid_group` |

`circuit_podium_rate_for_grid_group` = in earlier races at this circuit, the share of drivers from this grid group (1–3, 4–6, 7–10, 11+) who reached the podium.

| Split | Rows | Podium rate |
|-------|------|-------------|
| Train | 22,444 | 13.5% |
| Validation | 775 | 15.1% |
| Test | 1,352 | 15.1% |

**Missing values left to fill in the modeling notebook**

| Feature | Missing | Why |
|---------|---------|-----|
| `qualifying_gap_to_pole_percent` | 58.2% | No qualifying lap times for most races before 2003. |
| `driver_podium_rate_at_circuit` | 30.3% | Driver's first race at this circuit. |
| `driver_standing_position_before_race`, `constructor_standing_position_before_race` | 11.8% | Round 1, or no points yet. |
| `constructor_points_share_before_race` | 4.7% | Before 1958. |
| Other `driver_` form columns | 2.8% | Driver's first race. |
| `constructor_` form columns | 1.1% | Team's first race. |
| `circuit_podium_rate_for_grid_group` | 0.1% | The very first race. |

## 4. Limitations to report

- After a shared drive, the kept row can carry the grid of the car the driver took over, not the car he started in.
- A renamed team loses its history.
- Qualifying features are empty for most training rows but complete in validation and test.
- Validation is small: 775 rows, 117 podiums.
