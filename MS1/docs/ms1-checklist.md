# MS1 checklist

Every requirement from `docs/resources/MS1.pdf` and the F1 guide, checked against what is in `submission/`.

**Deadline: 18 October 2026, 11:59 PM.** Submit on the form: https://forms.gle/esDxHsvfzffYHVAZ9

Legend: ✅ done · ⬜ still to do

## What is in `submission/`

| File | What it is |
|------|------------|
| `f1-podium-prediction.ipynb` | The one run-all notebook: **Part 1** audit, cleaning and modeling table, **Part 2** data-engineering questions, **Part 3** modeling, experiments, XAI and inference, then a summary. Saved with all outputs. |
| `report.pdf` | 18 pages with all 33 notebook figures. Source: `docs/report/` (rebuild with `python docs/report/build_report.py`). |
| `README.md` | How to run it, and the steps before submitting. |
| `requirements.txt` | Library versions of the last run. |

References below: **P1 §7.3** = notebook Part 1, section 7.3. **R4** = report section 4.

**Verified on 16 Oct 2026:**
- Run All passes with no errors, under pandas 3.0 and again under pandas 2.2 (similar to Kaggle). Both runs give the same results.
- The saved modeling table is byte-identical to the committed one.
- Every number in the markdown matches the outputs.

## Still to do

- [x] ✅ **Team info** (Team 28, 4 members with ID and tutorial) is on the report cover and in the notebook title cell. To change it, edit `TEAM` and `MEMBERS` in `docs/report/report_content.py`, then run `python docs/report/build_report.py`.
- [ ] ⬜ **Kaggle dataset:** upload our own `data/raw` as a Kaggle dataset, so the numbers stay the same if the public dataset has been updated.
- [ ] ⬜ **Kaggle notebook:**
  - [ ] Upload `f1-podium-prediction.ipynb` and attach the dataset. No path editing is needed: the first cell finds the folder with `results.csv`.
  - [ ] Run All passes on Kaggle (`shap` and `lime` import), then **Save Version** with outputs.
  - [ ] The numbers match the local run.
  - [ ] Set the notebook to **Public**, and open the link in a private window to check it.
- [ ] ⬜ **GitHub:** commit and push `submission/`, `docs/report/` and this checklist. Make sure the repo is accessible (public, or shared with the TAs).
- [ ] ⬜ **Form:** Kaggle link, GitHub link and `report.pdf`, before 18 Oct 2026, 11:59 PM.
- [ ] ⬜ Optional: `docs/cleaning-and-modeling-table.md` still points to `notebooks/01-...`. Point it to `submission/f1-podium-prediction.ipynb`.

## 1. Notebook requirements

- [x] ✅ **One** run-all notebook, no manual cells. Paths are set in the first code cell and found automatically on Kaggle.
- [x] ✅ Sectioned: a title cell with the contents, Parts 1–3 with numbered sections, and a summary at the end
- [x] ✅ Logical order, with a markdown cell before each step
- [x] ✅ Raw CSVs only read, never written. Cleaning happens on copies.
- [x] ✅ Every conclusion backed by a plot, a statistic or an experiment

## 2. Data cleaning and auditing

- [x] ✅ EDA **before** cleaning, with plots: sentinels, rows and podium rate per season, `positionText` codes, grid histogram, qualifying coverage, Indianapolis 500 (P1 §2–3, R2.1, R2.5)
- [x] ✅ EDA **after** cleaning, compared with before: rows after each step, before/after lines, grid histogram (P1 §5, R2.5)
- [x] ✅ Sentinels: `\N` counted in all 14 tables, plotted, replaced and recounted. Empty qualifying cells checked too. (P1 §2.2, §4.1, R2.1)
- [x] ✅ Semantic typing: numbers, dates, and qualifying lap times converted to seconds. The 16:42 outlier is set to missing. The post-race duration text columns are explained (they already have numeric `milliseconds`). (P1 §4.2–4.3, R2.2)
- [x] ✅ Whitespace in column names, text and nationality (P1 §2.1, §4.4)
- [x] ✅ Primary keys of all 14 tables are unique and non-null. 23 foreign keys, 0 orphans. (P1 §2.3–2.4, R2.1)
- [x] ✅ Grain is one row per (`raceId`, `driverId`): 91 duplicates, plotted, with the "lowest `positionOrder`" rule and its reason. Two drivers in one car are kept. (P1 §4.5, R2.3)
- [x] ✅ Non-starters removed: Indianapolis 500, F/W, grid 0 with 0 laps. Pit-lane starts set to last place + 1. (P1 §4.6–4.7, R2.4)

## 3. Data-engineering questions

Each needs multi-hop joins, an answer, a plot, and a justification of grain, missingness and pre-race cutoff.

- [x] ✅ Q1 front row → podium per circuit, before/after 2014, qualifying vs grid (P2 Q1, R3 Q1)
- [x] ✅ Q2 home podium rate, controlled for grid: grid groups, single positions, and a logit (P2 Q2, R3 Q2)
- [x] ✅ Q3 mechanical-retirement rate per constructor, 2014–2021 vs 2022–2024, with the status mapping and team lineages (P2 Q3, R3 Q3)
- [x] ✅ Answers in markdown in the notebook **and** in the report, with figures

## 4. Feature selection and engineering

- [x] ✅ Every feature known before the race, with a table of why each one is valid (P1 §7, R4)
- [x] ✅ Leakage-safe form: `shift()`, and one row per team per race before shifting (P1 §7.3–7.4)
- [x] ✅ Standings from the previous round, points divided by the leader's points (P1 §7.5)
- [x] ✅ Leakage checks: row count, no post-race columns, a value recomputed by hand, correlation with the target (P1 §8, R4)
- [x] ✅ Evidence for the choices: podium rate by grid, the penalty test, correlation plots, feature-feature heatmap (P1 §7, P3 §2, R4)
- [x] ✅ Why there are no sprint features (P1 §7, R4)
- [x] ✅ The `season_progress` 2020 caveat (P1 §7.6, R10)

## 5. Split and pre-processing

- [x] ✅ Split by season (train ≤ 2019, val 2020–21, test 2022–24), with the reason (P3 §1, R5)
- [x] ✅ Missing values filled with the train median, with the effect shown (P3 §3.1, R5)
- [x] ✅ Scaling with the train mean and std, with the effect described (P3 §3.2, R5)
- [x] ✅ 3 pre-processing-order experiments (2 required): split vs pre-process first, fill vs scale first, missing flags (P3 §8.4, R5)

## 6. Models

- [x] ✅ Baseline: the grid rule, plus logistic regression as the baseline model (P3 §4.1, §5.1)
- [x] ✅ 3 statistical models (2 required): logistic regression, random forest, gradient boosting (P3 §5)
- [x] ✅ Shallow NN in Keras: 1 layer (16), and 2 layers (32-16) with dropout (P3 §6)
- [x] ✅ More than 3 modeling attempts: C, depth, number of trees and seeds tuned, each in its own cell
- [x] ✅ How each model works and its limits (P3 §5–6, R6)
- [x] ✅ Thresholds and hyperparameters chosen on validation only. Test scored once.
- [x] ✅ ROC-AUC, PR-AUC, F1, precision and recall for every model, on train, val and test (P3 §7, R6)
- [x] ✅ Primary metric (PR-AUC) and secondary metrics (ROC-AUC, F1) justified (P3 §4, R6)
- [x] ✅ Plots: NN loss, PR-AUC per split, ROC and PR curves, confusion matrix (P3 §6–7, R6)
- [x] ✅ Same rows and the same features for every model

## 7. Experiments

- [x] ✅ Feature-group ablation for LR and RF, plus "one group alone" (P3 §8.1, R7)
- [x] ✅ Extra: absolute vs relative grid, and the training-year window (P3 §8.2–8.3, R7)

## 8. Explainability

- [x] ✅ Global: permutation importance, SHAP bar and beeswarm (P3 §9.1–9.2, R8.1)
- [x] ✅ Local: SHAP waterfall and LIME for one prediction (P3 §9.3, R8.2)
- [x] ✅ Plotted and interpreted in the notebook and the report
- [x] ✅ "Importance is not causation" stated in both (P3 §9, R8)

## 9. Inference function

- [x] ✅ `predict_podium(record)` on a complete record and a partially-missing record (P3 §10, R9)

## 10. Report

- [x] ✅ Task, unit of analysis, target and cutoff (R1)
- [x] ✅ Cleaning, with the before/after EDA (R2)
- [x] ✅ DE answers with figures (R3)
- [x] ✅ Selected features and why each is valid at the pre-race cutoff (R4)
- [x] ✅ Split, pre-processing and the order experiments (R5)
- [x] ✅ Model comparison table (val and test), and the metric choice (R6)
- [x] ✅ Ablation (R7), XAI (R8), inference (R9)
- [x] ✅ Limitations: qualifying-coverage drift, era sensitivity, small validation set, team renames, shared-drive grid, `season_progress` 2020, association not cause (R10)
- [x] ✅ All 33 notebook plots included
- [x] ✅ Team info on the cover

## 11. Evaluation prep (whole team)

- [ ] ⬜ Every member can explain every cell: cleaning, features, models, metrics and the metric choice
- [ ] ⬜ Each choice has a reason tied to F1 and to evidence. "An AI tool suggested it" is not a reason.
- [ ] ⬜ Be ready for:
  - why PR-AUC
  - why a season split
  - why `shift()`
  - why the previous-round standings
  - why logistic regression won
  - why `has_qualifying_data` is high in SHAP but 0 in permutation importance
  - why validation scores are above train
