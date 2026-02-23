"""
Hospital Data Pipeline - HCL Hackathon

This pipeline processes hospital data through Bronze, Silver, and Gold layers:
- Bronze: Raw data storage
- Silver: Cleaned and standardized data
- Gold: Anomaly detection and analysis outputs
- Visualizations: Charts and graphs

Author: HCL Hackathon Team
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import warnings
from docx import Document
import sys
import io

# Set UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

print("=" * 80)
print("🏥 HOSPITAL DATA PIPELINE - Starting Execution")
print("=" * 80)


# ============================================================================
# TASK 1: BRONZE LAYER - Raw Data Storage
# ============================================================================
print("\n📦 TASK 1: Bronze Layer - Storing Raw Data")
print("-" * 80)

# Read ehr.csv
print("Reading ehr.csv...")
ehr_df = pd.read_csv('ehr.csv')
ehr_df.to_csv('bronze/ehr.csv', index=False)
print(f"✓ Stored {len(ehr_df)} records to bronze/ehr.csv")

# Read vitals.docx
print("Reading vitals.docx...")
try:
    doc = Document('vitals.docx')
    vitals_data = []
    
    # Check if data is in tables
    if doc.tables:
        for table in doc.tables:
            headers = [cell.text.strip() for cell in table.rows[0].cells]
            for row in table.rows[1:]:
                row_data = [cell.text.strip() for cell in row.cells]
                if any(row_data):
                    vitals_data.append(dict(zip(headers, row_data)))
    else:
        # Data is in paragraphs as JSON/JSONL format
        for para in doc.paragraphs:
            text = para.text.strip()
            if text and text.startswith('{'):
                try:
                    vitals_data.append(json.loads(text))
                except json.JSONDecodeError:
                    pass
    
    vitals_df = pd.DataFrame(vitals_data)
    vitals_df.to_csv('bronze/vitals.csv', index=False)
    print(f"✓ Stored {len(vitals_df)} records to bronze/vitals.csv")
except Exception as e:
    print(f"⚠ Warning: Could not read vitals.docx: {e}")
    print("  Trying vitals.jsonl as fallback...")
    vitals_list = []
    with open('vitals.jsonl', 'r') as f:
        for line in f:
            vitals_list.append(json.loads(line))
    vitals_df = pd.DataFrame(vitals_list)
    vitals_df.to_csv('bronze/vitals.csv', index=False)
    print(f"✓ Stored {len(vitals_df)} records to bronze/vitals.csv")

# Read labs.docx
print("Reading labs.docx...")
try:
    doc = Document('labs.docx')
    labs_data = []
    
    # Check if data is in tables
    if doc.tables:
        for table in doc.tables:
            headers = [cell.text.strip() for cell in table.rows[0].cells]
            for row in table.rows[1:]:
                row_data = [cell.text.strip() for cell in row.cells]
                if any(row_data):
                    labs_data.append(dict(zip(headers, row_data)))
    else:
        # Data is in paragraphs as JSON array format
        full_text = '\n'.join([para.text for para in doc.paragraphs])
        try:
            labs_data = json.loads(full_text)
        except json.JSONDecodeError:
            # Try parsing line by line as JSONL
            for para in doc.paragraphs:
                text = para.text.strip()
                if text and text.startswith('{'):
                    try:
                        labs_data.append(json.loads(text))
                    except json.JSONDecodeError:
                        pass
    
    labs_df = pd.DataFrame(labs_data)
    labs_df.to_csv('bronze/labs.csv', index=False)
    print(f"✓ Stored {len(labs_df)} records to bronze/labs.csv")
except Exception as e:
    print(f"⚠ Warning: Could not read labs.docx: {e}")
    print("  Trying labs.json as fallback...")
    with open('labs.json', 'r') as f:
        labs_list = json.load(f)
    labs_df = pd.DataFrame(labs_list)
    labs_df.to_csv('bronze/labs.csv', index=False)
    print(f"✓ Stored {len(labs_df)} records to bronze/labs.csv")

print("✓ Bronze Layer Complete - All raw data stored")


# ============================================================================
# TASK 2: SILVER LAYER - Data Cleaning & Standardization
# ============================================================================
print("\n🧹 TASK 2: Silver Layer - Data Cleaning & Standardization")
print("-" * 80)

# Clean EHR data
print("Cleaning ehr.csv...")
ehr_clean = ehr_df.copy()
ehr_clean['admission_time'] = pd.to_datetime(ehr_clean['admission_time'])
ehr_clean = ehr_clean.rename(columns={'admission_time': 'timestamp'})
ehr_clean['patient_id'] = ehr_clean['patient_id'].astype(int)
ehr_clean.to_csv('silver/ehr_clean.csv', index=False)
print(f"✓ Cleaned EHR data: {len(ehr_clean)} patients")
print(f"  - Converted timestamps to datetime")
print(f"  - Standardized column names")

# Clean vitals data
print("\nCleaning vitals.jsonl...")
vitals_clean = vitals_df.copy()
# Convert UNIX timestamps to datetime
vitals_clean['timestamp'] = pd.to_datetime(vitals_clean['timestamp'], unit='s')
# Rename patientId to patient_id for consistency
vitals_clean = vitals_clean.rename(columns={'patientId': 'patient_id'})
# Ensure numeric fields are numeric
vitals_clean['hr'] = pd.to_numeric(vitals_clean['hr'], errors='coerce')
vitals_clean['ox'] = pd.to_numeric(vitals_clean['ox'], errors='coerce')
vitals_clean['sys'] = pd.to_numeric(vitals_clean['sys'], errors='coerce')
vitals_clean['dia'] = pd.to_numeric(vitals_clean['dia'], errors='coerce')
vitals_clean['patient_id'] = vitals_clean['patient_id'].astype(int)
# Drop any rows with missing values
vitals_clean = vitals_clean.dropna()
vitals_clean.to_csv('silver/clean_vitals.csv', index=False)
print(f"✓ Cleaned vitals data: {len(vitals_clean)} vital readings")
print(f"  - Converted UNIX timestamps to datetime")
print(f"  - Ensured all vital signs are numeric (hr, ox, sys, dia)")
print(f"  - Standardized patient_id column")

# Clean labs data
print("\nCleaning labs.json...")
labs_clean = labs_df.copy()
# Convert timestamps to datetime
labs_clean['timestamp'] = pd.to_datetime(labs_clean['timestamp'])
# Ensure numeric fields are numeric
labs_clean['value'] = pd.to_numeric(labs_clean['value'], errors='coerce')
labs_clean['patient_id'] = labs_clean['patient_id'].astype(int)
# Rename for standardization
labs_clean = labs_clean.rename(columns={'test': 'lab_test', 'value': 'lab_value'})
# Drop any rows with missing values
labs_clean = labs_clean.dropna()
labs_clean.to_csv('silver/clean_labs.csv', index=False)
print(f"✓ Cleaned labs data: {len(labs_clean)} lab records")
print(f"  - Converted timestamps to datetime")
print(f"  - Ensured lab values are numeric")
print(f"  - Standardized column names (lab_test, lab_value)")

print("✓ Silver Layer Complete - All data cleaned and standardized")


# ============================================================================
# TASK 3: Combined Patient Master Table
# ============================================================================
print("\n🔗 TASK 3: Creating Combined Patient Master Table")
print("-" * 80)

# Get latest vitals for each patient
print("Getting latest vitals for each patient...")
vitals_latest = vitals_clean.sort_values('timestamp').groupby('patient_id').last().reset_index()
vitals_latest = vitals_latest[['patient_id', 'hr', 'ox', 'sys', 'dia']]
vitals_latest.columns = ['patient_id', 'latest_hr', 'latest_ox', 'latest_sys', 'latest_dia']
print(f"✓ Got latest vitals for {len(vitals_latest)} patients")

# Get latest labs for each patient (pivot to get one row per patient)
print("Getting latest labs for each patient...")
labs_latest = labs_clean.sort_values('timestamp').groupby(['patient_id', 'lab_test']).last().reset_index()
labs_pivot = labs_latest.pivot(index='patient_id', columns='lab_test', values='lab_value').reset_index()
# Rename columns to be more descriptive
labs_pivot.columns = ['patient_id'] + [f'latest_{col}' for col in labs_pivot.columns[1:]]
print(f"✓ Got latest labs for {len(labs_pivot)} patients")

# Join EHR + latest vitals + latest labs
print("\nJoining EHR + Vitals + Labs...")
patient_master = ehr_clean.copy()
patient_master = patient_master.merge(vitals_latest, on='patient_id', how='left')
patient_master = patient_master.merge(labs_pivot, on='patient_id', how='left')

# Save patient master
patient_master.to_csv('silver/patient_master.csv', index=False)
print(f"✓ Created patient_master.csv with {len(patient_master)} patients")
print(f"  - Columns: {len(patient_master.columns)}")
print(f"  - Includes: EHR data + Latest vitals + Latest labs")

print("✓ Patient Master Table Complete")


# ============================================================================
# TASK 4: Anomaly Detection (Rule-Based)
# ============================================================================
print("\n🚨 TASK 4: Anomaly Detection (Rule-Based)")
print("-" * 80)

anomalies = []

# Detect anomalies in vitals data
print("Detecting anomalies in vitals data...")
for _, row in vitals_clean.iterrows():
    patient_id = row['patient_id']
    timestamp = row['timestamp']
    
    # Rule 1: High Heart Rate (HR > 120)
    if row['hr'] > 120:
        anomalies.append({
            'patient_id': patient_id,
            'timestamp': timestamp,
            'anomaly': 'High Heart Rate',
            'value': row['hr']
        })
    
    # Rule 2: Low Oxygen (OX < 92)
    if row['ox'] < 92:
        anomalies.append({
            'patient_id': patient_id,
            'timestamp': timestamp,
            'anomaly': 'Low Oxygen',
            'value': row['ox']
        })
    
    # Rule 3: High Blood Pressure (sys > 160 OR dia > 100)
    if row['sys'] > 160 or row['dia'] > 100:
        anomalies.append({
            'patient_id': patient_id,
            'timestamp': timestamp,
            'anomaly': 'High Blood Pressure',
            'value': f"sys={row['sys']}, dia={row['dia']}"
        })

# Create anomalies dataframe
anomalies_df = pd.DataFrame(anomalies)
anomalies_df.to_csv('gold/anomalies.csv', index=False)

print(f"✓ Detected {len(anomalies_df)} anomalies:")
if len(anomalies_df) > 0:
    anomaly_counts = anomalies_df['anomaly'].value_counts()
    for anomaly_type, count in anomaly_counts.items():
        print(f"  - {anomaly_type}: {count}")

print("✓ Anomaly Detection Complete")


# ============================================================================
# TASK 5: Visualizations
# ============================================================================
print("\n📊 TASK 5: Creating Visualizations")
print("-" * 80)

# Visualization 1: Heart Rate Trend (Combined Multi-line Plot)
print("Creating Heart Rate Trend visualization...")
plt.figure(figsize=(12, 6))

# Get sample of 5 patients for clarity
sample_patients = vitals_clean['patient_id'].unique()[:5]
for patient_id in sample_patients:
    patient_vitals = vitals_clean[vitals_clean['patient_id'] == patient_id]
    plt.plot(patient_vitals['timestamp'], patient_vitals['hr'], 
             marker='o', label=f'Patient {patient_id}', alpha=0.7)

plt.axhline(y=120, color='r', linestyle='--', label='High HR Threshold (120)', alpha=0.5)
plt.xlabel('Timestamp', fontsize=12)
plt.ylabel('Heart Rate (bpm)', fontsize=12)
plt.title('Heart Rate Trend Over Time (Sample Patients)', fontsize=14, fontweight='bold')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('visualizations/hr_trend.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: visualizations/hr_trend.png")

# Visualization 2: Oxygen Level Distribution
print("Creating Oxygen Level Distribution visualization...")
plt.figure(figsize=(10, 6))

# Create histogram with low oxygen highlighted
ox_values = vitals_clean['ox'].values
plt.hist(ox_values, bins=30, alpha=0.7, color='skyblue', edgecolor='black')

# Add vertical line for low oxygen threshold
plt.axvline(x=92, color='red', linestyle='--', linewidth=2, 
            label='Low Oxygen Threshold (92)')

# Highlight low oxygen readings
low_ox = vitals_clean[vitals_clean['ox'] < 92]['ox']
if len(low_ox) > 0:
    plt.hist(low_ox, bins=30, alpha=0.8, color='red', edgecolor='darkred', 
             label=f'Low Oxygen Readings ({len(low_ox)})')

plt.xlabel('Oxygen Level (%)', fontsize=12)
plt.ylabel('Number of Occurrences', fontsize=12)
plt.title('Oxygen Level Distribution', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('visualizations/oxygen_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: visualizations/oxygen_distribution.png")

# Visualization 3: Bar Chart of Anomaly Counts
print("Creating Anomaly Counts Bar Chart...")
plt.figure(figsize=(10, 6))

if len(anomalies_df) > 0:
    anomaly_counts = anomalies_df['anomaly'].value_counts()
    bars = plt.bar(range(len(anomaly_counts)), anomaly_counts.values, 
                   color=['#FF6B6B', '#4ECDC4', '#FFE66D'], 
                   edgecolor='black', linewidth=1.5)
    
    plt.xticks(range(len(anomaly_counts)), anomaly_counts.index, rotation=0)
    plt.xlabel('Anomaly Type', fontsize=12)
    plt.ylabel('Number of Occurrences', fontsize=12)
    plt.title('Anomaly Detection Summary', fontsize=14, fontweight='bold')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
else:
    plt.text(0.5, 0.5, 'No anomalies detected', 
             ha='center', va='center', fontsize=14)
    plt.xlim(0, 1)
    plt.ylim(0, 1)

plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('visualizations/anomaly_counts.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: visualizations/anomaly_counts.png")

print("✓ All Visualizations Created")


# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("✅ PIPELINE EXECUTION COMPLETE!")
print("=" * 80)
print("\n📊 Summary:")
print(f"  • Bronze Layer: {len(ehr_df)} EHR records, {len(vitals_df)} vitals, {len(labs_df)} labs")
print(f"  • Silver Layer: {len(ehr_clean)} patients cleaned")
print(f"  • Patient Master: {len(patient_master)} patients with complete data")
print(f"  • Anomalies Detected: {len(anomalies_df)}")
print(f"  • Visualizations: 3 charts created")

print("\n📁 Output Files:")
print("  Bronze Layer:")
print("    - bronze/ehr.csv")
print("    - bronze/vitals.csv")
print("    - bronze/labs.csv")
print("\n  Silver Layer:")
print("    - silver/ehr_clean.csv")
print("    - silver/clean_vitals.csv")
print("    - silver/clean_labs.csv")
print("    - silver/patient_master.csv")
print("\n  Gold Layer:")
print("    - gold/anomalies.csv")
print("\n  Visualizations:")
print("    - visualizations/hr_trend.png")
print("    - visualizations/oxygen_distribution.png")
print("    - visualizations/anomaly_counts.png")

print("\n" + "=" * 80)
print("🎉 All tasks completed successfully!")
print("=" * 80)
