# MS1 submission – F1 Podium Prediction

| File | What it is |
|------|------------|
| `f1-podium-prediction.ipynb` | The one run-all notebook: audit, cleaning, EDA, data-engineering questions, features, models, experiments, XAI and the inference function. Saved with all outputs. |
| `report.pdf` | The analytical report: all 33 notebook figures, the data-engineering answers, the selected features and why each is valid before the race, the model comparison, ablation, pre-processing-order experiments, XAI and limitations. |
| `requirements.txt` | Library versions the notebook was last run with. |

## How to run

In the repo, run it from this folder: it reads `../data/raw` and saves the modeling table to `../data/processed`. Run All takes about 6 minutes on a laptop CPU.

On Kaggle, nothing needs editing. Attach a dataset that contains the 14 CSVs. The first code cell finds the folder with `results.csv` under `/kaggle/input` and writes to `/kaggle/working`.

## Before submitting (deadline 18 Oct 2026, 11:59 PM)

1. **Team info** is already in the report and the notebook (Team 28). To change it, edit `TEAM` and `MEMBERS` in `docs/report/report_content.py` and run `python docs/report/build_report.py` (needs `pip install reportlab`).
2. **Kaggle.** Upload our own `data/raw` as a Kaggle dataset, so the numbers match the public dataset even if it has been updated since. Upload the notebook, attach that dataset, Run All, Save Version, and set the notebook to **Public**.
3. **GitHub.** Push the repo (with this folder) and make sure it is accessible.
4. **Form.** Submit the Kaggle link, the GitHub link and `report.pdf`: https://forms.gle/esDxHsvfzffYHVAZ9
