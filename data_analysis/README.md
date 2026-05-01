# Data Analysis Pipeline

This folder contains the data analysis pipeline for the VR-Based Beta Sensory Stimulation study. It processes raw data, calculates Inter-Trial Coherence (ITC) and sickness score shifts, performs statistical analysis, and generates publication plots.

## Setup

This project uses `uv` for dependency management. To set up the environment:

1. Ensure you have Python 3.13 or newer installed.
2. Install [uv](https://docs.astral.sh/uv/) if you haven't already.
3. Install the dependencies by running:
   ```bash
   uv sync
   ```

## Data Requirements

Before running the pipeline, ensure that the raw data is placed in the `data/raw/` directory.

## Execution

To execute the data analysis pipeline, run the `main.py` script:

```bash
uv run main.py
```

### What it does:

1. **Builds Dataset**: Loads raw data from `data/raw/`.
2. **Calculates ITC**: Computes baseline and run ITC (Inter-Trial Coherence) values.
3. **Calculates Score Shifts**: Computes pre/post shifts for SSQ, VRSQ, and CSQ sickness metrics.
4. **Exports Data**: Saves the combined feature set to `master.xlsx`.
5. **Statistical Analysis**: Runs paired tests, correlations, and time-series permutation tests on FMS and ITC data.
6. **Visualization**: Generates publication-ready plots.
