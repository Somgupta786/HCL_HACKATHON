# Hospital Data Pipeline

A Python batch data pipeline that processes hospital data through Bronze → Silver → Gold layers and generates visualizations.

## Pipeline Architecture

### Bronze Layer (Raw Ingestion)
- Reads source files from `/data` directory
- Stores exact raw copies as CSV files in `/bronze`
- No transformations applied
- Files: `ehr.csv`, `vitals.csv`, `labs.csv`

### Silver Layer (Cleaning & Standardization)
- **Clean Vitals**: Renames `patientId` to `patient_id`, converts UNIX timestamps to datetime, ensures numeric types for hr, ox, sys, dia
- **Clean Labs**: Renames columns (`patientId` → `patient_id`, `test` → `lab_test`, `value` → `lab_value`), converts timestamps, ensures numeric lab values
- **Patient Master Table**: Combines EHR data with latest vitals and latest lab results per test for each patient
- Files: `clean_vitals.csv`, `clean_labs.csv`, `patient_master.csv`

### Gold Layer (Anomaly Detection)
Detects anomalies based on:
- **High Heart Rate**: HR > 120 bpm
- **Low Oxygen**: OX < 92%
- **High Blood Pressure**: SYS > 160 OR DIA > 100 mmHg
- File: `anomalies.csv`

## Data Cleaning Details

### Latest Record Selection
- Vitals: Sorted by timestamp, grouped by patient_id, selected last record
- Labs: Sorted by timestamp, grouped by patient_id and lab_test, selected last record per test

### Type Conversions
- UNIX timestamps converted to pandas datetime
- All vital signs and lab values converted to numeric with error handling

## Visualizations

1. **Heart Rate Trend** (`hr_trend.png`): Multi-line plot showing heart rate over time for all patients
2. **Oxygen Distribution** (`oxygen_distribution.png`): Histogram with threshold line at 92%
3. **Anomaly Counts** (`anomaly_counts.png`): Bar chart showing count of each anomaly type

## How to Run

```bash
python main.py
```

## Re-runnable Pipeline Behavior

The pipeline is fully idempotent and re-runnable:
- Always reads fresh input files from `/data`
- Overwrites all outputs in bronze, silver, and gold layers
- Regenerates all visualizations
- No caching or state persistence

**Adding New Data**: Simply add rows to input files (`ehr.csv`, `vitals.jsonl`, `labs.json`) and re-run `python main.py`. All outputs will automatically reflect the new data.

## Tech Stack

- Python
- pandas
- numpy
- matplotlib
- json
- pathlib

## Project Structure

```
project/
├── data/              # Input files
├── bronze/            # Raw ingested data
├── silver/            # Cleaned and standardized data
├── gold/              # Anomaly detection results
├── visualizations/    # Generated plots
├── src/               # Source code modules
│   ├── bronze.py
│   ├── silver.py
│   ├── gold.py
│   ├── visualize.py
│   └── utils.py
├── main.py            # Pipeline orchestration
└── README.md
```

## Execution Flow

1. **Setup**: Create required folders
2. **Bronze**: Ingest raw data
3. **Silver**: Clean and standardize data, create patient master
4. **Gold**: Detect anomalies
5. **Visualization**: Generate plots

Each step prints a log message indicating completion.
