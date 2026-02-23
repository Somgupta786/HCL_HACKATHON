import os
import json
import pandas as pd

def bronze_layer():
    print("Running Bronze Layer...")

    os.makedirs("bronze", exist_ok=True)

    # Read from existing bronze folder files
    if os.path.exists("bronze/ehr.csv"):
        ehr_df = pd.read_csv("bronze/ehr.csv")
        print("✓ EHR data loaded successfully")
    else:
        print("⚠ No ehr.csv found in bronze folder")
        ehr_df = None

    if os.path.exists("bronze/vitals.csv"):
        vitals_df = pd.read_csv("bronze/vitals.csv")
        print("✓ Vitals data loaded successfully")
    else:
        print("⚠ No vitals.csv found in bronze folder")
        vitals_df = None

    if os.path.exists("bronze/labs.csv"):
        labs_df = pd.read_csv("bronze/labs.csv")
        print("✓ Labs data loaded successfully")
    else:
        print("⚠ No labs.csv found in bronze folder")
        labs_df = None

    print("Bronze Layer Completed")
