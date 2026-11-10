# Report text. Executed by build_report.py, which provides h1, h2, p, bullets, table, fig, story, ...

# ---- fill in before submitting ----
TEAM = 'Team 28'
MEMBERS = ('Ali Abuelkheir - 58-3693 - T17<br/>'
           'Maria Awad - 58-5927 - T28<br/>'
           'Rodaina Elsawy - 58-16542 - T24<br/>'
           'Monica Samaan - 58-4467 - T18')
# -----------------------------------

W = PAGE_W

story.append(Spacer(1, 1.5 * cm))
story.append(Paragraph('F1 Podium Prediction', TITLE))
story.append(Paragraph('Milestone 1 Report', ParagraphStyle('Sub', parent=TITLE, fontSize=14, textColor=colors.grey)))
story.append(Spacer(1, 0.6 * cm))
table([['Team', TEAM], ['Members<br/>(name - ID - tutorial)', MEMBERS],
       ['Notebook', 'f1-podium-prediction.ipynb (Kaggle link and GitHub link on the submission form)'],
       ['Dataset', 'Formula 1 World Championship (1950-2024), Kaggle / Ergast, 14 linked CSV tables']],
      widths=[3 * cm, W - 3 * cm], header=False)
story.append(Spacer(1, 0.4 * cm))

h1('1. Task')
p('For every driver entering a race we predict whether the driver finishes on the podium (<b>positionOrder &lt;= 3</b>). '
  'One row is one driver in one race, so the key (raceId, driverId) must be unique. The prediction is made '
  '<b>after qualifying and before the race starts</b>. Everything the race itself produces (finishing position, points, '
  'laps, status, pit stops, lap times, and the standings after the race) is <b>leakage</b> and is never used as a feature.')
p('Podiums are rare: 13.7% of the final rows (about 3 of 20 drivers in a modern race, far fewer in eras with 30+ entrants). '
  'This class imbalance drives the choice of metric in section 6.')

h1('2. Audit and cleaning')
h2('2.1 Audit')
bullets([
    '<b>Formatting:</b> in our copy, constructor_results and constructor_standings have spaces and quotes around column '
    'names and text (" raceId"). Merges would fail, so they are stripped first.',
    '<b>Sentinels:</b> missing values are written as the text \\N in 6 tables (for example results.position, '
    'qualifying.q2/q3, drivers.number). Pandas reads them as text, so they are counted per column (Figure 1), replaced '
    'by NaN, and counted again (0 left). qualifying also has 68 truly empty cells, which pandas already reads as NaN.',
    '<b>Primary keys:</b> all 14 tables have a unique, non-null primary key.',
    '<b>Foreign keys:</b> 23 links checked (for example results.raceId -> races, qualifying.driverId -> drivers): 0 orphans.',
    '<b>Modeling key:</b> (raceId, driverId) is not unique in results.csv: 85 pairs, 91 extra rows (section 2.3).',
])
fig("plt.barh(sentinels['column']", 'Share of \\N sentinel values per column, before cleaning.', 0.62)

h2('2.2 Semantic typing')
bullets([
    'Six results columns (number, position, milliseconds, fastestLap, rank, fastestLapSpeed) to numbers. races.date and '
    'drivers.dob to dates.',
    'Qualifying lap times ("1:26.572") to seconds. One lap of 16:42.640 (1002.6 s) is far from every other value (the '
    'next is 153.9 s), so it is set to missing. The other slow laps fit a wet session and are kept.',
    'The other duration columns are post-race and never used (results.time, results.fastestLapTime, lap_times.time, '
    'pit_stops.duration). Race, lap and pit-stop times already have a numeric milliseconds column next to the text, '
    'so the text copies are left as they are.',
    'One driver nationality had a stray space. circuits.country uses both "USA" and "United States", so they are merged.',
])

h2('2.3 Grain: one row per (raceId, driverId)')
p('Almost all duplicates come from 1950-1964 <b>shared drives</b>: a driver could take over a teammate\'s car during the '
  'race, which gives one row per car. <b>Rule: keep the row with the lowest positionOrder.</b> The row answers "did this '
  'driver finish on the podium?", and a podium in the shared car is an official podium for that driver. Limitation: the '
  'kept row can carry the grid slot of the car the driver took over, because the data does not say which car the '
  'driver started in. The opposite case, <b>two drivers sharing one car</b>, is kept: both have one row and both were '
  'officially on the podium (18 races have 4 or 5 podium rows).')
fig("Duplicate driver-race rows per season", 'Duplicate (raceId, driverId) rows per season: almost all in the 1950s.', 0.6)

h2('2.4 Rows that are not prediction cases')
table([
    ['Step', 'Rows left', 'Reason'],
    ['Raw results.csv', '26,759', ''],
    ['Duplicate rule', '26,668', 'One row per driver per race (section 2.3).'],
    ['Drop the Indianapolis 500 (1950-1960)', '26,287', '107 drivers, only 3 of whom raced anywhere else: a separate population on an oval.'],
    ['Drop positionText F and W', '24,586', 'Failed to qualify or withdrew: they never started, which is known after qualifying.'],
    ['Drop grid = 0 with 0 laps', '24,571', 'Excluded, disqualified or broken before the start: they did not start either.'],
    ['grid = 0 with laps (72 rows, 2015+)', '24,571', 'Pit-lane starts. Left as 0 they look better than pole, so grid = last grid place of the race + 1.'],
], widths=[5.2 * cm, 1.8 * cm, W - 7 * cm])
p('raceId is not in time order (raceId 1 is a 2009 race), so the rows are sorted by date before any "previous races" feature is built.')

h2('2.5 EDA before and after cleaning')
p('Before cleaning, the rows per season spike in the late 1980s and early 1990s and the podium rate drops in the same '
  'years, because every race still has about three podiums. Most of those extra rows were cars that never started, so '
  'after cleaning the bump is much smaller, the lowest podium rates move up, and the spike at grid 0 is gone (Figures 3-6). '
  'Qualifying data starts in 1994, is patchy in 1996-2002, and is complete from 2003 (Figure 7): this is the '
  'qualifying-coverage drift that the qualifying features must handle.')
fig("rows_before.plot(ax=ax[0]", 'Before cleaning: result rows and podium rate per season.')
fig("title='grid (before cleaning)'", 'Before cleaning: grid has a spike at 0, which is not a real starting slot.', 0.6)
fig("Rows after each cleaning step", 'Rows left after each cleaning step.', 0.55)
fig("ax[0].plot(rows_before, label='before')", 'Before vs after cleaning: rows per season, podium rate per season, and the grid distribution after cleaning.')
fig("Share of races with qualifying data", 'Share of races with any qualifying data, per season.', 0.7)

h1('3. Data-engineering questions')
p('All three answers need multi-hop joins: results.csv alone has neither the year, the circuit, the nationality nor the status text.')

h2('Q1. Which circuits convert a front-row start into a podium most often, and does that change after 2014?')
p('<b>Joins:</b> results -> races (raceId) -> circuits (circuitId), and results -> qualifying (raceId, driverId). '
  '<b>Grain:</b> one front-row starter in one race. <b>Two definitions:</b> front row by <b>grid</b> (grid 1 or 2, where the car '
  'actually started) and by <b>qualifying</b> (qualifying position 1 or 2, before penalties). <b>Years:</b> 2003-2024, because qualifying '
  'is only complete from 2003. That gives two eras of 11 seasons: 2003-2013 and 2014-2024 (hybrid era and later). Circuits need at '
  'least 5 races in an era, because with fewer races one result moves the rate by more than 10 points.')
p('<b>Answer.</b> A front-row start became a podium in <b>68.3%</b> of cases in 2003-2013 (272/398) and <b>76.2%</b> in 2014-2024 (345/453). '
  'The top circuits were Magny-Cours (91.7%), Istanbul Park (78.6%), Monza and Monaco (77.3%) before 2014, and Monaco (89.5%), Suzuka (88.9%) '
  'and Yas Marina (86.4%) from 2014. <b>The ranking changed a lot:</b> for the 14 circuits with enough races in both eras the Spearman rank '
  'correlation is only 0.36. Yas Marina climbed from 11th to 3rd, and Monza fell from 1st to 10th. 11 of the 14 circuits have a higher rate in the later era.')
p('<b>Grid vs qualifying.</b> Qualifying position and grid differ on 27.7% of driver rows, but the front row is stable: of 852 top-2 '
  'qualifiers, 37 (4.3%) did not start from the front row, mostly because of penalties. Rates by qualifying are a little lower (67.6% and 74.0%), '
  'and the circuit ranking is nearly the same with both definitions (rank correlation 0.89 and 0.88).')
fig("Share of result rows that have a qualifying row", 'Q1: share of result rows with a qualifying row, per season (red line: 2003).', 0.65)
fig("sns.barplot(data=both", 'Q1: front-row (grid) to podium conversion rate per circuit and era (circuits with at least 5 races in both eras).', 0.78)
fig("Rank of each circuit by front-row conversion rate", 'Q1: rank of each circuit in 2003-2013 vs 2014-2024. Crossing lines mean the ranking changed.', 0.6)
fig("Each dot is one circuit", 'Q1: conversion rate per circuit, grid definition vs qualifying definition (dashed line = equal).', 0.75)
p('<b>Missingness:</b> 21 starters from 2003 have no qualifying row (kept by a left join, so they cannot be "front row by qualifying"). '
  'grid = 0 never counts as front row. Drivers who did not start are dropped, so the 2005 US Grand Prix (grid 1-4 withdrew) has no front-row starter. '
  '<b>Pre-race cutoff:</b> both front-row flags are known before the start, and the podium is the outcome. Each circuit rate rests on only '
  '10-22 starts, so the order of neighbouring circuits is noisy. The overall rise from 68% to 76% is the solid result.', SMALL)

h2('Q2. Do drivers podium more often at a home circuit, after controlling for starting position?')
p('<b>Joins:</b> results -> races -> circuits (circuit country) and results -> drivers (nationality). <b>Home</b> means the circuit country is '
  'the country of the driver\'s nationality, through a documented mapping ("British" -> "UK", "Monegasque" -> "Monaco", "East German" -> "Germany", '
  'dual nationalities -> the first one). <b>Removed:</b> the Indianapolis 500 (99.7% "home" entries, a separate population), drivers who did not start, '
  'grid = 0 starts (no grid group), and 43 drivers whose country never hosted a race (they can never be at home). That leaves 22,175 starts: 1,927 at home and 20,248 away.')
table([
    ['Grid group', 'Home', 'Away', 'Difference'],
    ['1-3', '57.5% (131/228)', '56.4% (1,548/2,747)', '+1.1 points'],
    ['4-6', '27.2% (61/224)', '26.1% (704/2,701)', '+1.2 points'],
    ['7-10', '7.5% (25/335)', '9.1% (333/3,669)', '-1.6 points'],
    ['11+', '1.1% (13/1,140)', '1.6% (181/11,131)', '-0.5 points'],
], widths=[2.5 * cm, 4 * cm, 4.5 * cm, W - 11 * cm])
p('<b>Answer: no home advantage once starting position is controlled.</b> Before any control, home drivers reach the podium <i>less</i> often '
  '(11.9% vs 13.7%), but they also start further back on average (mean grid 12.7 vs 11.8). Inside grid groups the differences go both ways. '
  'Their weighted average is -0.3 points (-0.2 points with every grid position as its own group). A logistic regression '
  '<i>podium ~ grid group + home</i> gives a home odds ratio of <b>0.96 (95% CI 0.81-1.14, p = 0.65)</b>. The sign is not stable over time '
  '(+0.2 points in 1950-1989, -1.8 in 1990-2024). This controls for the grid only, not for the car or the driver, so it is an association, not a causal statement.')
fig("Podium rate by grid position (question 2 table)", 'Q2: podium rate by grid position, used to choose the grid groups 1-3, 4-6, 7-10, 11+.', 0.65)
fig("Podium rate at home vs away", 'Q2: podium rate at home vs away inside each grid group.', 0.55)

h2('Q3. Which constructors have the highest mechanical-retirement rate in 2014-2021 vs 2022-2024?')
p('<b>Joins:</b> results -> races (year), results -> status (reason the race ended), results -> constructors (team). <b>Grain:</b> one car that '
  'started one race. <b>Rate</b> = mechanical retirements / race starts. Entries that never started (W) are excluded from both the numerator and the denominator, '
  'even when the reason was mechanical, because the brief defines the rate over race starts. <b>Status mapping:</b> all 66 statuses seen in 2014-2024 are classified by hand '
  'as mechanical (a named part or system failed: Engine, Power Unit, Gearbox, Hydraulics, Brakes, ...), accident (Collision, Accident, Collision damage, Debris), '
  'driver (Spun off, Illness), regulation (Disqualified, Excluded), unclear (Retired, Withdrew, Puncture, Tyre) or finished (Finished, +n Laps). '
  '<b>Team lineages:</b> renamed teams are grouped (Toro Rosso / AlphaTauri / RB, Force India / Racing Point / Aston Martin, Lotus F1 / Renault / Alpine, '
  'Sauber / Alfa Romeo, Marussia / Manor), otherwise the two periods cannot be compared for those teams. Minimum: 50 starts in the period (this removes Caterham, 33 starts).')
table([
    ['Rank', '2014-2021', 'Rate', '2022-2024', 'Rate'],
    ['1', 'Lotus F1 / Renault / Alpine', '14.8% (47/318)', 'Lotus F1 / Renault / Alpine', '10.4% (14/135)'],
    ['2', 'Toro Rosso / AlphaTauri / RB', '14.4% (46/319)', 'Sauber / Alfa Romeo', '8.8% (12/136)'],
    ['3', 'McLaren', '13.6% (43/316)', 'Toro Rosso / AlphaTauri / RB', '6.6% (9/136)'],
    ['4', 'Red Bull', '10.7% (34/318)', 'Williams', '6.0% (8/134)'],
    ['5', 'Haas', '9.5% (23/241)', 'Aston Martin lineage, Ferrari, Haas', '5.2% (7 each)'],
    ['last', 'Mercedes', '4.1% (13/320)', 'McLaren, Red Bull', '3.7% (5/136 each)'],
], widths=[1.1 * cm, 4.6 * cm, 2.6 * cm, W - 10.9 * cm, 2.6 * cm])
p('<b>Answer.</b> Overall, mechanical retirements fell from 9.5% of starts (308/3,246) to 5.9% (80/1,352). <b>The Enstone team (Lotus F1 / Renault / Alpine) '
  'has the highest rate in both periods.</b> McLaren and Red Bull moved from 3rd and 4th worst to the two most reliable teams. Sauber / Alfa Romeo is the only midfield '
  'team that got slightly worse (8.2% -> 8.8%). Counting the unclear statuses as mechanical raises every rate a little but keeps the same team on top in both periods. '
  'In 2022-2024 each team has only about 135 starts, so teams one or two retirements apart are not really different. '
  '<b>Pre-race cutoff:</b> status is post-race, so it is only used to describe past races. As a model feature it is turned into a rate over earlier races only (section 4).')
fig("Mechanical-retirement rate per team", 'Q3: mechanical-retirement rate per team lineage, sorted by the 2014-2021 rate.', 0.72)
fig("Share of race starts that did not finish", 'Q3: share of race starts that did not finish, by reason, per period.', 0.55)

h1('4. Features and why each is valid at the pre-race cutoff')
p('Each feature uses only the starting grid, qualifying, or results of <b>earlier</b> races. The key tool is <b>shift()</b>: the value of a race '
  'is moved one row down before any rolling or cumulative step, so a row never sees its own result. Constructor form is computed on <b>one row per team per race</b> '
  'first, otherwise one car could see its teammate\'s result from the same race. The standings tables are post-race, so each row takes the standings of the '
  '<b>previous round of the same season</b>. Points are divided by the leader\'s points because a win was worth 8, 9, 10 or 25 points depending on the era.')
table([
    ['Group', 'Features', 'Why it is known before the race'],
    ['Grid', 'grid_position, grid_position_relative (grid / field size), front_row_start', 'The starting grid is fixed before the start.'],
    ['Qualifying', 'grid_penalty_places (grid - qualifying position), qualifying_gap_to_pole_percent, has_qualifying_data',
     'Qualifying is finished before the race. Grid and qualifying position correlate at 0.97, so only their difference is kept.'],
    ['Driver form', 'driver_races_before, podium rate last 5, average finish last 5, retirement rate last 10, career podium rate, podium rate at this circuit',
     'Earlier races only (shift). Checked by hand on one driver.'],
    ['Constructor form', 'podium rate last 5, average finish last 5, mechanical-retirement rate last 10', 'Earlier races only, one row per team per race before shifting.'],
    ['Standings', 'driver points share, standing position, season wins; constructor points share, standing position', 'Previous round. No row means 0 points and 0 wins.'],
    ['Context', 'driver_age, home_race, season_progress, circuit_podium_rate_for_grid_group',
     'Birth date, nationality and calendar are known in advance. The circuit rate uses earlier races at the circuit only.'],
], widths=[2.4 * cm, 7.2 * cm, W - 9.6 * cm])
p('<b>Evidence for the choices.</b> The podium rate falls fast and non-linearly with grid position (Figures 16-17), so grid is the core signal, and '
  'front_row_start and the circuit-by-grid-group rate help a linear model follow the curve. Among drivers starting 7th-10th, those moved back 3+ places by a '
  'penalty reached the podium 21.7% of the time against 5.7% for the others: fast cars out of position, which grid alone cannot see. No feature correlates near '
  '+-1 with the target (Figure 18), which would be the sign of a leak. <b>No sprint features:</b> sprints only exist from 2021, so the column would be empty for every '
  'training row, and the format changed almost every year.')
p('<b>Leakage checks in the notebook:</b> the row count is unchanged after all merges, there are no duplicate keys, no post-race column is in the feature list, '
  'and one form value recomputed by hand matches the table.')
fig("title='Podium rate by grid position')", 'Podium rate by grid position (all rows of the modeling table).', 0.62)
fig("Podium rate by grid position (train)", 'The same on the training rows only, as checked before modeling.', 0.62)
fig("title='Correlation of each feature with podium')", 'Leakage check: correlation of each feature with the target on all rows. None is close to +-1.', 0.55)
fig("Correlation of each feature with podium (train)", 'Correlation of each feature with the target (training rows).', 0.55)
p('The features overlap: four pairs correlate above 0.8 (grid_position and grid_position_relative 0.96, grid_position_relative and the '
  'circuit rate -0.81, driver and constructor podium rate 0.81, driver and constructor points share 0.81). This is why removing a '
  'single group costs little in the ablation (section 7).')
fig("Correlation between features (train)", 'Correlation between the 24 features (training rows).', 0.75)

h1('5. Split and pre-processing')
p('<b>Split by season:</b> train 1950-2019 (22,444 rows, 13.5% podium), validation 2020-2021 (775 rows, 15.1%), test 2022-2024 (1,352 rows, 15.1%). '
  'The split is not random because at prediction time only the past is known, and form and standings features link neighbouring races. A random split would '
  'leak in both directions. year is used for the split only, never as a feature.')
p('<b>Missing values</b> are filled with the <b>training median</b> (several features are skewed). The biggest case is the qualifying gap, missing in 14,284 '
  'training rows (no lap times before 2003) but almost complete in validation and test. has_qualifying_data tells the model which races were filled. '
  '<b>Scaling:</b> standardisation with the training mean and std, for logistic regression and the neural network. Trees get the filled, unscaled table. '
  'Every model uses the same rows, the same 24 features and the same filled values. <b>Effect of scaling:</b> the ranges were very '
  'different (driver_races_before goes up to a few hundred, the rates stay between 0 and 1). After scaling every feature has mean 0 '
  'and std 1 on train, and the shape of each distribution is unchanged: only the axis moves.')
fig("Share of missing values in the modeling table", 'Share of missing values left in the saved modeling table, before filling.', 0.65)
fig("after filling with the train median", 'Effect of median filling on the qualifying gap: the filled rows form a spike at the median.', 0.75)
p('<b>Pre-processing-order experiments</b> (logistic regression, PR-AUC):')
table([
    ['Experiment', 'Our pipeline (val / test)', 'Alternative (val / test)', 'Finding'],
    ['A. Split first vs fill and scale the whole table first', '0.7459 / 0.7233', '0.7459 / 0.7235',
     'Same score: the medians barely move because val + test are 9% of rows. We still split first, the only leak-free order.'],
    ['B. Fill then scale vs scale then fill', '0.7459 / 0.7233', '0.7461 / 0.7236',
     'The std of the qualifying gap changes (1.57 vs 2.57), but a linear model absorbs the scale in its weight.'],
    ['C. Missing flags before vs after filling', '0.7459 / 0.7233', '0.7446 / 0.7213',
     'Flags after filling flag 0 cells, before filling 24,120. The flags do not help, so they are not used.'],
], widths=[4.2 * cm, 2.6 * cm, 2.6 * cm, W - 9.4 * cm])

h1('6. Models and metrics')
p('<b>Metrics:</b> ROC-AUC, PR-AUC, F1, precision and recall, for every model. <b>Primary metric: PR-AUC.</b> Only about 14% of rows are podiums, and ROC-AUC '
  'also rewards the many easy "no podium" rows at the back of the grid, so it is high for every model. PR-AUC only improves when podium rows are ranked better. '
  '<b>Secondary metrics:</b> ROC-AUC (comparability) and F1 (the final yes/no decision). The F1 threshold of each model is the one with the best F1 on '
  '<b>validation</b>. All hyperparameters were also chosen on validation. The test set was scored once, at the end.')
bullets([
    '<b>Baseline without a model, the grid rule:</b> score = 1 / grid_position. The best threshold is "grid 1-3 is the podium". <i>Limits:</i> it sees one feature only.',
    '<b>Logistic regression (baseline model):</b> a weighted sum of the features squeezed into a probability. Each feature pushes the probability in one direction only, '
    'and there are no interactions unless they are built by hand. Changing C (0.01-10) moved validation PR-AUC by less than 0.002, so the default C = 1 is kept. '
    '<i>Limits:</i> it keeps adding or subtracting for every extra unit, so outliers (a huge gap to pole) get extreme values.',
    '<b>Random forest:</b> averages many decorrelated trees and handles curves and interactions. The default (fully grown trees) overfits (train PR-AUC 1.000, validation 0.685), so '
    'max_depth = 5 (validation 0.732). <i>Limits:</i> deep trees memorise the training rows, and a forest cannot predict outside what it has seen.',
    '<b>Gradient boosting:</b> trees built one after another, each correcting the last. The default (100 trees, depth 3) beat larger variants on validation. <i>Limits:</i> more settings to tune, and with too many trees it fits noise.',
    '<b>Shallow neural networks (Keras):</b> 1 hidden layer of 16, and 2 hidden layers (32-16) with dropout 0.2. ReLU, sigmoid output, binary cross-entropy, Adam, '
    'early stopping on validation loss (patience 10). Retraining with three other seeds moves validation PR-AUC between 0.744 and 0.751, so <b>differences under about 0.01 are noise</b>. <i>Limits:</i> the result depends on the random start, it needs scaled inputs, '
    'and it is harder to explain than a list of weights.',
])
table([
    ['', 'Validation', '', '', 'Test (unseen)', '', '', '', '', ''],
    ['Model', 'ROC<br/>AUC', 'PR<br/>AUC', 'F1', 'ROC<br/>AUC', 'PR<br/>AUC', 'F1', 'Precision', 'Recall', 'Threshold'],
    ['Grid rule (baseline)', '0.910', '0.648', '0.695', '0.913', '0.647', '0.649', '0.650', '0.647', '0.333'],
    ['<b>Logistic regression</b>', '0.931', '0.746', '0.713', '0.936', '<b>0.723</b>', '0.676', '0.551', '0.873', '0.233'],
    ['Random forest', '0.932', '0.732', '0.716', '0.941', '0.719', '0.669', '0.566', '0.819', '0.272'],
    ['Gradient boosting', '0.928', '0.724', '0.725', '0.939', '0.695', '0.691', '0.625', '0.775', '0.309'],
    ['NN 1 layer (16)', '0.930', '0.727', '0.723', '0.934', '0.717', '0.662', '0.579', '0.775', '0.266'],
    ['NN 2 layers (32-16)', '0.931', '0.751', '0.713', '0.937', '0.715', '0.676', '0.592', '0.789', '0.319'],
], widths=[3.3 * cm] + [(W - 3.3 * cm) / 9] * 9, spans=[((1, 0), (3, 0)), ((4, 0), (8, 0))])
p('Train PR-AUC: grid rule 0.500, logistic regression 0.578, random forest 0.612, gradient boosting 0.657, NN 0.601 / 0.600. Validation and test scores are above train '
  'for every model. This is not a bug: the training rows go back to 1950, when races were far less predictable, and the validation and test races are modern.', SMALL)
p('<b>Result.</b> Every model beats the grid rule (test PR-AUC 0.647 -> 0.70-0.72), so the non-grid features add real information. The models are within the noise '
  'of each other. <b>Final model: logistic regression</b>, chosen on validation: it is tied with the best network (0.746 vs 0.751, inside the seed noise), and among tied models '
  'we take the simplest. It is deterministic, trains in a second, and its weights can be read. The test column (PR-AUC 0.723, ROC-AUC 0.936) confirms the choice but did not make it. '
  'The complex models did not earn their complexity because the hand-built features (form, standings, circuit rate) already capture the non-linear structure. At the '
  'validation threshold of 0.23 the model finds 178 of the 204 test podiums (recall 0.87) with 145 false alarms (precision 0.55), about 5 candidates per race for 3 places.')
fig("title='1 hidden layer (16)'", 'Training and validation loss per epoch of the two networks (early stopping keeps the best epoch).', 0.8)
fig("PR-AUC per model and split", 'PR-AUC per model on train, validation and test.', 0.72)
fig("ROC curve (test)", 'ROC and precision-recall curves on the unseen test set.', 0.95)
fig("Logistic regression on the test set", 'Confusion matrix of the final model on the test set (threshold 0.23 from validation).', 0.45)

h1('7. Experiments: feature-group ablation')
p('One feature group is removed at a time and the model is retrained (logistic regression, and the random forest as a second opinion). '
  'Then the view is turned around: one group alone.')
table([
    ['Group removed', 'LR val drop', 'LR test drop', 'RF val drop', 'Group alone: val / test PR-AUC'],
    ['grid', '-0.011', '+0.022', '+0.008', '0.655 / 0.658'],
    ['qualifying', '+0.004', '+0.001', '+0.009', '0.639 / 0.607'],
    ['driver form', '+0.008', '-0.002', '+0.006', '0.653 / 0.519'],
    ['constructor form', '-0.009', '+0.007', '-0.004', '0.534 / 0.509'],
    ['standings', '+0.007', '+0.009', '+0.012', '0.661 / 0.562'],
    ['context', '+0.013', '+0.000', '+0.008', '0.635 / 0.574'],
    ['(all features)', '', '', '', '0.746 / 0.723'],
], widths=[3.4 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm, W - 10.6 * cm])
p('<b>No single group is essential:</b> every drop is at most about 0.02, and several are negative, all near the noise level of 0.01. The groups overlap '
  '(driver and constructor form correlate at 0.81, and the circuit rate is built from the grid), so when one group is removed the others fill in. '
  '<b>Every group alone is far below the full model</b>, so the gain comes from combining groups. Grid alone is the strongest and most stable group. '
  'Standings and driver form alone look good on validation but fall on test. Further experiments: absolute vs relative grid makes no difference (within 0.003), '
  'and training from 1994 (10,091 rows) scores the same as training from 1950 (validation 0.752 vs 0.746), so the old seasons do not help.')
fig("Drop in PR-AUC when one feature group is removed", 'Drop in PR-AUC when one feature group is removed (right = the group helped).', 0.7)
fig("PR-AUC with one feature group alone", 'PR-AUC with one feature group alone, against all features.', 0.7)

h1('8. Explainability')
p('<b>Important: these explanations show what the model relies on. They are not causal effects.</b> A feature being important does not prove that it causes '
  'podium finishes. For example, the model leans on grid position, but a slow car moved to pole by hand would not become a podium car.')
h2('8.1 Global: permutation importance and SHAP')
p('<b>Permutation importance</b> (validation, PR-AUC, 10 shuffles): grid_position stands far above everything else (shuffling it costs about 0.17 PR-AUC). Then come '
  'driver_career_podium_rate, circuit_podium_rate_for_grid_group and qualifying_gap_to_pole_percent at about 0.02 each. Most other features are near zero. '
  'A zero does not mean useless: when two features carry the same information, shuffling one leaves the other to do the job.')
fig("perm_table['drop in PR-AUC'].plot", 'Permutation importance of the final model on the validation set.', 0.55)
p('<b>SHAP</b> (LinearExplainer, in log-odds) agrees on the top features. In the beeswarm, a high grid number (red) pushes the prediction down and a front start (blue) pushes it up. '
  'A few drivers with a huge gap to pole get extreme negative values, because a linear model keeps subtracting for every extra percent: this is a limit of the model. '
  'A positive grid_penalty_places pushes up: a driver who starts further back than qualified is faster than the grid slot suggests. '
  'has_qualifying_data ranks high in SHAP but is zero in permutation importance. Every validation race has qualifying data, so it shifts every row by the same amount and '
  'cannot change the order. SHAP measures the distance from the training average, while permutation importance measures what the ranking needs.')
fig("shap.plots.bar(shap_values", 'Mean |SHAP| per feature (validation rows).', 0.6)
fig("shap.plots.beeswarm(shap_values", 'SHAP beeswarm: each dot is one validation row (red = high feature value).', 0.7)
h2('8.2 Local: one prediction (SHAP waterfall and LIME)')
p('The row is the pole sitter of the last race of 2021 (round 22). The model gives 0.85, and the driver did finish on the podium. The SHAP waterfall starts at the model\'s '
  'average output (-2.96 log-odds, about 5%) and ends at +1.75 (about 85%). Pole position adds the most (+1.69). The circuit\'s podium rate for the front of the grid, '
  'the zero gap to pole, 9 wins this season, the career podium rate and the team\'s recent results all push up. LIME, a different method that fits a local linear model on '
  'perturbed copies of the row, gives the same picture (its conditions are in scaled units). The two methods agree on why the model said 0.85. Neither says these features caused the podium.')
fig("shap.plots.waterfall(shap_values[i]", 'Local SHAP waterfall for one prediction.', 0.62)
fig("lime_exp.as_pyplot_figure()", 'LIME explanation of the same prediction (green pushes towards podium).', 0.6)

h1('9. Inference function')
p('predict_podium(record) takes the pre-race features of one driver in one race as a dict. It repeats the training pipeline with values learned on training rows only: '
  'it fills missing features with the training medians, scales with the training mean and std, predicts with the logistic regression, and compares with the validation '
  'threshold. A feature absent from the record is treated as missing. On a complete test record it returns (0.358, podium). With three values removed (qualifying gap, '
  'podium rate at the circuit, standing position) it returns (0.276, podium). The prediction still works, but it is less reliable, because a typical value replaced '
  'the driver\'s real circuit podium rate of 1.0.')

h1('10. Known limitations')
bullets([
    '<b>Qualifying-coverage drift:</b> qualifying lap times are missing for most races before 2003 (58% of all rows for the gap feature). The qualifying features '
    'are mostly filled values in training but complete in validation and test.',
    '<b>Era sensitivity:</b> most training rows come from a different kind of F1 (bigger fields, lower reliability, other points systems). Training from 1994 scores the same with less than half the rows.',
    '<b>Small validation set:</b> 775 rows and 117 podiums, so differences under about 0.01 PR-AUC (the seed noise of the network) cannot be separated.',
    '<b>Team renames reset history:</b> constructor form follows constructorId, so a renamed team starts with no history.',
    '<b>Shared drives:</b> the kept duplicate row can carry the grid slot of the car the driver took over.',
    '<b>season_progress in 2020:</b> the COVID calendar was built during the season, so the number of rounds was not fully known in advance.',
    '<b>Associations, not causes:</b> the data-engineering answers and the explanations describe patterns in the data and in the model, not causal effects.',
])
