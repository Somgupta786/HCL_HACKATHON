# 🏥 Hospital Data Pipeline - HCL Hackathon Solution

## 📋 Project Overview

This is a **complete end-to-end hospital data pipeline** solution that processes Electronic Health Records (EHR), vital signs, and laboratory results through a medallion architecture (Bronze → Silver → Gold). The pipeline implements data cleaning, standardization, table joins, rule-based anomaly detection, and comprehensive visualizations.

---

## 📁 Project Folder Structure

```
hospital_pipeline/
├── bronze/                      # Raw data storage (Task 1)
│   ├── ehr.csv
│   ├── vitals.csv
│   └── labs.csv
├── silver/                      # Cleaned and standardized data (Task 2 & 3)
│   ├── ehr_clean.csv
│   ├── clean_vitals.csv
│   ├── clean_labs.csv
│   └── patient_master.csv       # Master table with joined data
├── gold/                        # Anomaly detection outputs (Task 4)
│   └── anomalies.csv
├── visualizations/              # Generated charts (Task 5)
│   ├── hr_trend.png
│   ├── oxygen_distribution.png
│   └── anomaly_counts.png
├── main.py                      # Main pipeline implementation
├── generate_sample_data.py      # Sample data generator
├── ehr.csv                      # Input: Electronic Health Records (300 patients)
├── vitals.jsonl                 # Input: Vital signs (1500 readings, JSONL format)
├── labs.json                    # Input: Lab results (900 records, JSON format)
└── README.md                    # This file
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Install Required Packages
```bash
pip install pandas matplotlib seaborn streamlit plotly python-docx
```

### Step 2: Generate Sample Data (Optional)
If you need sample data files, run:
```bash
cd hospital_pipeline
python generate_sample_data.py
```

This creates:
- `ehr.csv` - 300 patient records
- `vitals.jsonl` - 1500 vital sign readings (5 per patient)
- `labs.json` - 900 lab test results (3 per patient)

---

## 🚀 How to Run

### Option 1: Run the Data Pipeline
```bash
cd hospital_pipeline
python main.py
```

**Expected Output:**
```
================================================================================
🏥 HOSPITAL DATA PIPELINE - Starting Execution
================================================================================

📦 TASK 1: Bronze Layer - Storing Raw Data
✓ Stored 300 records to bronze/ehr.csv
✓ Stored 1500 records to bronze/vitals.csv
✓ Stored 900 records to bronze/labs.csv

🧹 TASK 2: Silver Layer - Data Cleaning & Standardization
✓ Cleaned EHR data: 300 patients
✓ Cleaned vitals data: 1500 vital readings
✓ Cleaned labs data: 900 lab records

🔗 TASK 3: Creating Combined Patient Master Table
✓ Created patient_master.csv with 300 patients

🚨 TASK 4: Anomaly Detection (Rule-Based)
✓ Detected 212 anomalies

📊 TASK 5: Creating Visualizations
✓ Saved: visualizations/hr_trend.png
✓ Saved: visualizations/oxygen_distribution.png
✓ Saved: visualizations/anomaly_counts.png

✅ PIPELINE EXECUTION COMPLETE!
```

### Option 2: Launch Interactive Dashboard 🎨
```bash
cd hospital_pipeline
streamlit run app.py
```

Then open your browser to **http://localhost:8501**

**Dashboard Features:**
- 📊 **Dashboard Overview**: Real-time metrics, anomaly distribution, vital signs charts
- 👥 **Patient Records**: Complete patient data with filters and search
- 🚨 **Anomaly Detection**: Timeline and detailed anomaly reports
- 📈 **Vital Signs Analysis**: Interactive trend charts for patient monitoring
- 🧪 **Lab Results**: Comprehensive lab test analysis and visualization
- 📉 **Visualizations**: Advanced charts including heatmaps and correlation matrices

---

## 📖 Task Implementation Details

### Task 1: Bronze Layer (Raw Storage)

**Purpose:** Store all input files exactly as received for backup and auditing.

**Implementation:**
- Read `ehr.csv` (CSV format) → Store as `bronze/ehr.csv`
- Read `vitals.jsonl` (JSON Lines) → Store as `bronze/vitals.csv`
- Read `labs.json` (JSON list) → Store as `bronze/labs.csv`

**Key Points:**
- No transformations applied
- Data stored row-by-row exactly as received
- Maintains data immutability for compliance

---

### Task 2: Silver Layer (Cleaning & Standardization)

**Purpose:** Clean and standardize data for analysis.

#### How We Cleaned EHR Data (`ehr.csv`):
```
✓ Converted admission_time from string to datetime objects
✓ Renamed 'admission_time' → 'timestamp' for consistency
✓ Ensured patient_id is integer type
✓ All demographic fields validated (name, age, gender)
```

**Output:** `silver/ehr_clean.csv`

#### How We Cleaned Vitals Data (`vitals.jsonl`):
```
✓ Converted UNIX timestamps to readable datetime format
✓ Renamed 'patientId' → 'patient_id' for consistency
✓ Ensured all vital signs are numeric:
  - hr (heart rate)
  - ox (oxygen level)
  - sys (systolic blood pressure)
  - dia (diastolic blood pressure)
✓ Removed rows with missing/invalid values
✓ Standardized patient_id column naming
```

**Output:** `silver/clean_vitals.csv`

#### How We Cleaned Labs Data (`labs.json`):
```
✓ Converted timestamp strings to datetime objects
✓ Ensured lab values are numeric (float type)
✓ Renamed 'test' → 'lab_test' for clarity
✓ Renamed 'value' → 'lab_value' for clarity
✓ Ensured patient_id is integer type
✓ Removed rows with missing/invalid values
```

**Output:** `silver/clean_labs.csv`

---

### Task 3: Combined Patient Master Table

**Purpose:** Create a unified view of each patient with their latest vitals and lab results.

#### How We Merged/Joined the Tables:

**Step 1:** Get Latest Vitals per Patient
```
- Sort vitals by timestamp
- Group by patient_id
- Take the last (most recent) record for each patient
- Select: hr, ox, sys, dia
```

**Step 2:** Get Latest Labs per Patient
```
- Sort labs by timestamp
- Group by patient_id and lab_test
- Take the last (most recent) record
- Pivot table so each lab test becomes a column
```

**Step 3:** Join Everything Together
```
EHR (base table with patient demographics)
  ⬇ LEFT JOIN
Latest Vitals (on patient_id)
  ⬇ LEFT JOIN
Latest Labs (on patient_id)
  ⬇
Patient Master Table
```

**Join Type:** LEFT JOIN (keeps all patients even if vitals/labs missing)

**Final Columns:**
- Patient info: patient_id, name, age, gender, timestamp
- Latest vitals: latest_hr, latest_ox, latest_sys, latest_dia
- Latest labs: latest_[test_name] for each lab test type

**Output:** `silver/patient_master.csv` (300 patients with ~21 columns)

---

### Task 4: Anomaly Detection (Rule-Based)

**Purpose:** Identify health anomalies that require attention.

#### Anomaly Detection Rules Used:

| Rule | Condition | Classification |
|------|-----------|----------------|
| **High Heart Rate** | HR > 120 bpm | Anomaly |
| **Low Oxygen** | OX < 92% | Anomaly |
| **High Blood Pressure** | sys > 160 OR dia > 100 | Anomaly |

**Implementation:**
```python
# Iterate through all vital sign readings
for each vital record:
    if hr > 120:
        flag as "High Heart Rate"
    
    if ox < 92:
        flag as "Low Oxygen"
    
    if sys > 160 or dia > 100:
        flag as "High Blood Pressure"
```

**Output Format:** `gold/anomalies.csv`
```csv
patient_id,timestamp,anomaly,value
101,2024-01-10 16:00:00,High Heart Rate,125
205,2024-01-10 12:00:00,Low Oxygen,89
176,2024-01-10 20:00:00,High Blood Pressure,sys=165, dia=102
```

**Typical Results:**
- ~200+ anomalies detected from 1500 vital readings
- ~14% anomaly rate (reflects natural variation + medical issues)

---

### Task 5: Visualizations

**Purpose:** Create visual insights for data analysis and reporting.

#### Visualization 1: Heart Rate Trend (per patient)
**File:** `visualizations/hr_trend.png`

**Description:**
- Line chart showing heart rate over time
- Shows 5 sample patients (for clarity)
- Red dashed line at HR=120 (anomaly threshold)
- X-axis: Timestamp
- Y-axis: Heart Rate (bpm)

**Use Case:** Monitor patient recovery trends and identify abnormal patterns

---

#### Visualization 2: Oxygen Level Distribution
**File:** `visualizations/oxygen_distribution.png`

**Description:**
- Histogram showing distribution of all oxygen readings
- Blue bars: Normal oxygen readings
- Red bars: Low oxygen readings (< 92%)
- Red dashed line: Low oxygen threshold (92%)
- X-axis: Oxygen Level (%)
- Y-axis: Number of Occurrences

**Use Case:** Identify systemic oxygen issues affecting patient population

---

#### Visualization 3: Bar Chart of Anomaly Counts
**File:** `visualizations/anomaly_counts.png`

**Description:**
- Bar chart showing count of each anomaly type
- X-axis: Anomaly Type (High Heart Rate, Low Oxygen, High Blood Pressure)
- Y-axis: Number of Occurrences
- Value labels displayed on top of each bar
- Color-coded bars for visual distinction

**Use Case:** Quickly identify which health issues are most prevalent

---

## 📊 Judging Criteria Alignment

| Category | Weight | Implementation |
|----------|--------|----------------|
| **Data Cleaning & Transformations** | 30% | ✓ Complete timestamp conversion, numeric validation, null handling, column standardization |
| **Pipeline Logic & Joins** | 25% | ✓ Medallion architecture (Bronze→Silver→Gold), efficient LEFT JOINs, latest record selection |
| **Visualizations** | 20% | ✓ 3 publication-quality charts (heart rate trend, oxygen distribution, anomaly counts) |
| **Anomaly Detection** | 15% | ✓ Rule-based detection with 3 clinical thresholds, structured output |
| **Code Quality & README** | 10% | ✓ Clean modular code, comprehensive documentation, clear execution logs |

---

## 📈 Execution Summary

When you run `python main.py`, the pipeline:

1. **Reads 3 input files** (ehr.csv, vitals.jsonl, labs.json)
2. **Stores raw data** in bronze/ folder (Task 1)
3. **Cleans all datasets** with timestamp/numeric conversions (Task 2)
4. **Creates patient master table** by joining EHR + latest vitals + latest labs (Task 3)
5. **Detects anomalies** using clinical rules (Task 4)
6. **Generates 3 visualizations** (Task 5)
7. **Displays summary** with statistics and file locations

**Total Execution Time:** ~5-10 seconds

---

## 📁 Output Files Summary

After running the pipeline, you'll have:

**Bronze Layer (Raw Backups):**
- `bronze/ehr.csv` - 300 rows
- `bronze/vitals.csv` - 1500 rows
- `bronze/labs.csv` - 900 rows

**Silver Layer (Cleaned Data):**
- `silver/ehr_clean.csv` - 300 patients
- `silver/clean_vitals.csv` - 1500 vital readings
- `silver/clean_labs.csv` - 900 lab results
- `silver/patient_master.csv` - 300 patients with complete data

**Gold Layer (Analytics):**
- `gold/anomalies.csv` - ~200+ anomaly records

**Visualizations:**
- `visualizations/hr_trend.png` - Heart rate trends
- `visualizations/oxygen_distribution.png` - Oxygen level histogram
- `visualizations/anomaly_counts.png` - Anomaly summary bar chart

---

## 🔧 Troubleshooting

**Issue:** `FileNotFoundError: ehr.csv not found`  
**Solution:** Ensure you're in the `hospital_pipeline/` directory and input files exist

**Issue:** `ModuleNotFoundError: No module named 'pandas'`  
**Solution:** Install dependencies: `pip install pandas matplotlib seaborn`

**Issue:** Visualizations not generating  
**Solution:** Check if `visualizations/` folder exists and you have write permissions

---

## 🎯 Key Features

✅ Medallion Architecture (Bronze → Silver → Gold)  
✅ Multi-format data ingestion (CSV, JSONL, JSON)  
✅ Comprehensive data cleaning pipeline  
✅ Efficient table joins using pandas  
✅ Latest record selection per patient  
✅ Rule-based clinical anomaly detection  
✅ High-quality visualizations (300 DPI)  
✅ Clear execution logging  
✅ Modular, maintainable code  

---

## 📝 Code Quality Highlights

- **Clean structure:** Separation of concerns with clear task boundaries
- **Readable code:** Descriptive variable names, clear logic flow
- **Error handling:** Proper data type conversions with validation
- **Performance:** Efficient pandas operations for large datasets
- **Documentation:** Inline comments and comprehensive README
- **Output validation:** Confirmation messages and statistics at each step

---

**Project Status:** ✅ Complete & Ready for Submission  
**Hackathon:** HCL Healthcare Data Challenge  
**Date:** February 2026