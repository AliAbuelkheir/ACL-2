# AGENTS.md

F1 podium prediction, a university milestone. Every team member must be able to explain every cell out loud, so write as a **junior developer** would.

## Where code goes

All code goes in Jupyter notebook cells (`.ipynb`). The notebook must run top to bottom with Run All.

Read from `data/raw`, which stays read-only. Save cleaned copies elsewhere.

## Junior developer style

- **Inspect, then fix.** Look at a problem in one cell, fix it in the next, then look again to confirm. `df.isna().sum()` comes before `fillna` or `dropna`. `df.duplicated().sum()` comes before `drop_duplicates`. `df.dtypes` comes before a cast.
- **One small step per cell.** Leave the output visible (`head()`, `shape`, `value_counts()`, a plot).
- **Plain pandas, top-level code.** Use the basic calls a first course teaches: `read_csv`, `merge`, `groupby`, `apply`, boolean masks. Reach for a function only when the same lines appear a third time.
- **Short, obvious names**: `df`, `results`, `races`, `merged`.
- **A markdown cell before each step** saying in one or two plain sentences what we saw and why we do the next thing.
- **Comments are short and casual**, only where a line is not obvious.

## Simplicity

Follow YAGNI principles, and prefer one-liner solutions.

The shortest code that a classmate understands on first read wins. If a one-liner needs explaining, split it into two plain lines.

Build only what the current step needs: the direct call, with the default arguments, on the data we have.

## Project context

- Requirements: `docs/resources/MS1.pdf`
- What each table is and how they link: `docs/dataset-tables.md`
- Cleaning musts and the modeling table: `docs/cleaning-and-modeling-table.md`
- Features must be known before the race starts. Read the leakage rules in the modeling-table doc before any feature work.
