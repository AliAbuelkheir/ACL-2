# Dataset Tables

The dataset has 14 CSV files in `data/raw`. Each file is one table.
The dataset has data for the seasons from 1950 to 2024.

Do not change the files in `data/raw`. Make all changes on copies.

## Keys

A primary key identifies one row in a table.
A foreign key refers to a primary key in a different table.
The text `\N` in a cell shows that the value is missing.

Four keys connect most of the tables:

| Key             | Table of origin    | Meaning                 |
|-----------------|--------------------|-------------------------|
| `raceId`        | `races.csv`        | One race in one season  |
| `driverId`      | `drivers.csv`      | One driver              |
| `constructorId` | `constructors.csv` | One constructor (team)  |
| `circuitId`     | `circuits.csv`     | One circuit             |

## Relations

```
seasons ──< races >── circuits
              │
              ├──< results >── drivers, constructors, status
              ├──< qualifying >── drivers, constructors
              ├──< sprint_results >── drivers, constructors, status
              ├──< lap_times >── drivers
              ├──< pit_stops >── drivers
              ├──< driver_standings >── drivers
              ├──< constructor_standings >── constructors
              └──< constructor_results >── constructors
```

The symbol `──<` shows that one row on the left has many rows on the right.

## Reference tables

These tables give the names and the properties of items. The data in these tables does not change after a race.

### `seasons.csv` (75 rows)

- One row is one season.
- Primary key: `year`.
- `races.year` refers to this table.

### `circuits.csv` (77 rows)

- One row is one circuit.
- Primary key: `circuitId`.
- The table gives the name, the country, and the position of each circuit.
- `races.circuitId` refers to this table.

### `drivers.csv` (861 rows)

- One row is one driver.
- Primary key: `driverId`.
- The table gives the name, the date of birth, and the nationality of each driver.
- All the tables that have a `driverId` column refer to this table.

### `constructors.csv` (212 rows)

- One row is one constructor.
- Primary key: `constructorId`.
- The table gives the name and the nationality of each constructor.
- All the tables that have a `constructorId` column refer to this table.

### `status.csv` (139 rows)

- One row is one result status. Examples: `Finished`, `Engine`, `Collision`.
- Primary key: `statusId`.
- `results.statusId` and `sprint_results.statusId` refer to this table.

## Race table

### `races.csv` (1,125 rows)

- One row is one race in one season.
- Primary key: `raceId`.
- `circuitId` refers to `circuits.csv`. `year` refers to `seasons.csv`.
- The table gives the date and the round number of each race.
- The round number gives the sequence of the races in a season.
- All the tables below refer to this table.

## Tables with data before the race

You can use the data in these tables to make a prediction for the same race.

### `qualifying.csv` (10,494 rows)

- One row is the qualifying result of one driver in one race.
- Primary key: `qualifyId`. The pair (`raceId`, `driverId`) is also unique.
- The table gives the qualifying position and the lap times `q1`, `q2`, and `q3`.
- The table has data from 1994 only. The data for 1996 to 2002 is not complete.
- The qualifying position can be different from `results.grid`, because a driver can get a penalty.

### `sprint_results.csv` (360 rows)

- One row is the result of one driver in one sprint.
- Primary key: `resultId`.
- A sprint is a short race that occurs before the main race.
- The table has data from 2021 only, for 18 races.
- The columns are almost the same as the columns of `results.csv`.

## Tables with data after the race

The data in these tables is available only after the race.
For the prediction of a race, use only the rows of the races that occurred before.

### `results.csv` (26,759 rows)

- One row is the result of one driver in one car in one race.
- Primary key: `resultId`.
- `raceId`, `driverId`, `constructorId`, and `statusId` refer to their tables.
- `positionOrder` gives the final position. This column gives the prediction target.
- `grid` gives the start position. The grid is known before the race.
- All the other result columns are known only after the race.
- The pair (`raceId`, `driverId`) is not unique. In 85 pairs, one driver has two or more rows.

### `lap_times.csv` (589,081 rows)

- One row is one lap of one driver in one race.
- Primary key: (`raceId`, `driverId`, `lap`).
- The table gives the lap time and the position of the driver at the end of the lap.
- The table has data from 1996 only.

### `pit_stops.csv` (11,371 rows)

- One row is one pit stop of one driver in one race.
- Primary key: (`raceId`, `driverId`, `stop`).
- The table gives the lap, the time of day, and the duration of the pit stop.
- The table has data from 2011 only.

### `driver_standings.csv` (34,863 rows)

- One row is the championship position of one driver after one race.
- Primary key: `driverStandingsId`. The pair (`raceId`, `driverId`) is also unique.
- The table gives the total points, the position, and the number of wins in the season.
- The values include the points of the race in `raceId`.

### `constructor_standings.csv` (13,391 rows)

- One row is the championship position of one constructor after one race.
- Primary key: `constructorStandingsId`. The pair (`raceId`, `constructorId`) is also unique.
- The columns are the same as the columns of `driver_standings.csv`.
- The table has data from 1958 only.

### `constructor_results.csv` (12,625 rows)

- One row is the points of one constructor in one race.
- Primary key: `constructorResultsId`. The pair (`raceId`, `constructorId`) is also unique.
- The points are the sum of the points of the cars of the constructor in that race.
- The table has data from 1958 only.
