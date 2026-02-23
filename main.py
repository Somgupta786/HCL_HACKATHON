import os
import sys
from datetime import datetime
from bronze.bronze_layer import bronze_layer
from silver.silver_layer import silver_layer
from gold.master_table import create_master_table
from gold.anomaly_detection import anomaly_detection
from visualizations.visualize import generate_visualizations

# Set encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("Starting Patient Health Data Pipeline")
print("=" * 60)

try:
    print("\n[BRONZE] Running Bronze Layer...")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    bronze_layer()
    print("   [OK] Bronze Layer Completed")
except Exception as e:
    print(f"   [ERROR] Error in Bronze Layer: {e}")

try:
    print("\n[SILVER] Running Silver Layer...")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    silver_layer()
    print("   [OK] Silver Layer Completed")
except Exception as e:
    print(f"   [ERROR] Error in Silver Layer: {e}")

try:
    print("\n[GOLD] Running Master Table Creation...")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    create_master_table()
    print("   [OK] Master Table Completed")
except Exception as e:
    print(f"   [ERROR] Error in Master Table: {e}")

try:
    print("\n[ANOMALY] Running Anomaly Detection...")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    anomaly_detection()
    print("   [OK] Anomaly Detection Completed")
except Exception as e:
    print(f"   [ERROR] Error in Anomaly Detection: {e}")

try:
    print("\n[VIZ] Generating Visualizations...")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    generate_visualizations()
    print("   [OK] Visualizations Completed")
except Exception as e:
    print(f"   [ERROR] Error in Visualizations: {e}")

print("\n" + "=" * 60)
print("[SUCCESS] Pipeline Execution Completed Successfully!")
print("=" * 60)

print("\nOutput Files Created:")
output_files = [
    "bronze/ehr.csv",
    "bronze/vitals.csv",
    "bronze/labs.csv",
    "silver/clean_vitals.csv",
    "silver/clean_labs.csv",
    "silver/patient_master.csv",
    "gold/patient_master.csv",
    "gold/anomalies.csv",
]

for file in output_files:
    if os.path.exists(file):
        print(f"   [V] {file}")

print("\nVisualizations Created:")
viz_files = [
    "visualizations/hr_trend.png",
    "visualizations/oxygen_distribution.png",
    "visualizations/blood_pressure_distribution.png",
    "visualizations/anomaly_counts.png",
    "visualizations/anomaly_timeline.png",
    "visualizations/patient_anomaly_counts.png",
    "visualizations/vital_signs_boxplot.png",
]

for file in viz_files:
    if os.path.exists(file):
        print(f"   [V] {file}")

print("\nTo view the interactive dashboard, run:")
print("   streamlit run dashboard.py")
print("\nPipeline Completed Successfully!")


