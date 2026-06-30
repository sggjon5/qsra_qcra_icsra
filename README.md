# Quantitative Project Risk - QSRA, QCRA and ICSRA

This Python package provides a Monte Carlo–based engine for Quantitative Schedule Risk Analysis (QSRA), Quantitative Cost Risk Analysis (QCRA) and integrated cost and schedule risk analysis (ICSRA), including both standalone (via commandline interface (CLI)) and interactive (Dashboard) modes. You can run static analyses to produce summary statistics, histograms, CDFs, tornado plots, JCL scatterplots and heatmaps, or launch a live dashboard to explore the same results with adaptable parameters.

* currently the only interactivity is the ability to zoom and move around the plots and to change the target duration and cost for the project.

---

<img width="906" height="450" alt="1746528258706" src="https://github.com/user-attachments/assets/df26bfba-0b8d-437f-91bf-4f29b79a9f4b" />
<img width="1889" height="450" alt="1746528258638" src="https://github.com/user-attachments/assets/2a9f6f2c-f198-4801-b2b6-e6cf8d1b55b7" />
<img width="1836" height="871" alt="1746528258724" src="https://github.com/user-attachments/assets/f0327dc7-efcf-452b-badd-8fccaef0413c" />

---

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Input File Format](#input-file-format)
5. [Distributions Supported](#distributions-supported)
6. [Command‑Line Interface (CLI)](#command-line-interface-cli)
   - [Static Run](#static-run)
   - [Dashboard](#dashboard)
7. [Outputs](#outputs)
8. [Interactive Dashboard](#interactive-dashboard)
9. [Project Structure](#project-structure)
10. [Contributing](#contributing)
11. [License](#license)

---

## Features

- **Monte Carlo simulation** of a user defined project and iteration count
- **Joint confidence level** for cost/time targets
- **Multiple distributions**: point, normal, uniform, beta (PERT), triangular
- **Static mode**: CLI entry point to generate PNGs & CSV
- **Interactive mode**: Dash-based dashboard with sliders for targets and live plots
- **Comprehensive visualisations**: histograms, CDFs, scatterplots, heatmaps, tornado


---

## Requirements

- Python 3.8 or newer
- Packages (see `setup.py`):
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `click`
  - `openpyxl>=3.1.0` (for Excel support)
  - `dash`
  - `plotly`

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/qsra_qcra.git
   cd qsra_qcra
   ```
2. (Recommended) Create and activate a Conda environment:
   ```bash
   conda create -n qsra_qcra python=3.11
   conda activate qsra_qcra
   ```
3. Install in editable mode:
   ```bash
   pip install --upgrade pip
   pip install -e .
   ```
4. Ensure `openpyxl` is up to date:
   ```bash
   pip install --upgrade openpyxl
   ```

---

## Input File Format

The tool accepts CSV or Excel (`.xlsx`) with these columns:

| Column     | Type     | Description                                  |
|------------|----------|----------------------------------------------|
| `task_id`  | integer  | Unique task identifier                       |
| `name`     | string   | Task name or description                     |
| `a_dur`    | float    | Optimistic duration (days)                   |
| `m_dur`    | float    | Most likely duration                         |
| `b_dur`    | float    | Pessimistic duration                         |
| `a_cost`   | float    | Optimistic cost                              |
| `m_cost`   | float    | Most likely cost                             |
| `b_cost`   | float    | Pessimistic cost                             |
| `dist_type`| string   | Distribution type: `point`, `normal`, `uniform`, `beta`, `triangular` |
| `is_critical` | int   | `1` if on critical path, else `0`           |

A sample file is provided in `sample_inputs/sample_tasks.csv`.

---

## Distributions Supported

| Type         | Parameters                                             | Best Use Case                                                 |
|--------------|--------------------------------------------------------|---------------------------------------------------------------|
| **point**    | fixed value                                           | Deterministic tasks                                          |
| **normal**   | mean = `(a + 4m + b)/6`, σ = `(b - a)/6`               | Symmetric uncertainty (beware unbounded tails)                |
| **uniform**  | `min=a`, `max=b`                                       | Only bounds known, flat likelihood                             |
| **beta**     | PERT: `α=1+4*(m–a)/(b–a)`, `β=1+4*(b–m)/(b–a)`         | Standard PERT smooth curve, down‑weights extremes             |
| **triangular**| `(a, m, b)`                                            | Simpler piecewise-linear peak, heavier tails                  |

---

## Command‑Line Interface (CLI)

### Static Run
Numbers used as parameters here are somewhat suited to example file provided but should be changed to suit each project being assessed.

```bash
qsra_qcra run \
  --input path/to/tasks.csv \
  --iters 10000 \
  --seed 42 \
  --outdir results/ \
  --cost-target 35000 \
  --time-target 40 \
```

- `--input`: path to CSV or Excel file
- `--iters`: number of Monte Carlo iterations
- `--seed`: random seed for reproducibility
- `--outdir`: directory for PNG + CSV outputs
- `--cost-target`, `--time-target`: thresholds for Joint Confidence Level (JCL)


After completion, you’ll see console P50/P90  and files in `results/`:

- `duration_hist.png`, `duration_cdf.png`
- `cost_hist.png`, `cost_cdf.png`
- `joint_scatter.png`, `joint_heatmap.png`
- `tornado_duration.png`, `tornado_cost.png`
- `percentiles_table.csv` (decile percentiles)

### Dashboard

```bash
qsra_qcra dashboard \
  --input path/to/tasks.xlsx(or .csv) \
  --iters 10000 \
  --seed 42 \
  --host 127.0.0.1 \
  --port 8050 \
```

Open your browser to `http://127.0.0.1:8050` to interact with:

- **Sliders** for cost/time targets
- **Histograms** & **CDFs** for duration & cost
- **Joint scatter** & **heatmap** with P50/P90 & targets
- **Tornado plots** for sensitivity analysis
- **Decile percentile table**

---

## Outputs Explained

- **Histograms**: raw counts of simulated outcomes with P50/P90 and target lines
- **CDFs**: cumulative distributions with P50/P90/targets
- **Joint Scatter**: each Monte Carlo point, P50/P90 lines, and cost/time targets
- **Heatmap**: density of (duration, cost) points
- **Tornado**: rank‐ordered Pearson correlations of each task’s contribution to overall risk
- **Percentiles Table**: shows values at every 10th percentile (10%–90%) for both duration & cost

---

## Project Structure

```
qsra_qcra/
├── cli.py            # click CLI entry points
├── data.py           # input loading (CSV/Excel)
├── project.py        # core simulation & analysis
├── viz.py            # Matplotlib static plotting (for CLI)
├── dashboard.py      # Dash app
├── setup.py          # package metadata & dependencies
├── sample_inputs/    # sample CSV/Excel files
└── README.md         # this document
```

---

## Contributing

1. Fork the repo and create a branch: `git checkout -b feature/xyz`
2. Make your changes and add tests if needed
3. Submit a pull request with a clear description

---

