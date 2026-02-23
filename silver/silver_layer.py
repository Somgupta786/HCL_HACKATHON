import pandas as pd
import os

def silver_layer():
    print("Running Silver Layer...")
    
    os.makedirs("silver", exist_ok=True)
    
    # Clean Vitals
    if os.path.exists("bronze/vitals.csv"):
        vitals_df = pd.read_csv("bronze/vitals.csv")
        vitals_df.to_csv("silver/clean_vitals.csv", index=False)
    
    # Clean Labs
    if os.path.exists("bronze/labs.csv"):
        labs_df = pd.read_csv("bronze/labs.csv")
        labs_df.to_csv("silver/clean_labs.csv", index=False)
    
    print("Silver Layer Completed")
