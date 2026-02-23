import pandas as pd
import os

def create_master_table():
    print("Creating Master Table...")
    
    os.makedirs("gold", exist_ok=True)
    
    # Load data
    ehr = pd.read_csv("bronze/ehr.csv") if os.path.exists("bronze/ehr.csv") else None
    vitals = pd.read_csv("silver/clean_vitals.csv") if os.path.exists("silver/clean_vitals.csv") else None
    labs = pd.read_csv("silver/clean_labs.csv") if os.path.exists("silver/clean_labs.csv") else None
    
    if ehr is not None and vitals is not None:
        # Get latest vitals per patient
        vitals['timestamp'] = pd.to_datetime(vitals['timestamp'])
        latest_vitals = vitals.sort_values('timestamp').groupby('patient_id').tail(1)
        
        # Merge with EHR
        master = ehr.merge(latest_vitals, on='patient_id', how='left')
        
        # Add labs if available
        if labs is not None:
            labs_pivot = labs.pivot_table(index='patient_id', columns='test', values='value', aggfunc='first')
            master = master.merge(labs_pivot, on='patient_id', how='left')
        
        # Save master table
        master.to_csv("gold/patient_master.csv", index=False)
        master.to_csv("silver/patient_master.csv", index=False)
    
    print("Master Table Created")
