import pandas as pd
import os

def anomaly_detection():
    print("Running Anomaly Detection...")
    
    os.makedirs("gold", exist_ok=True)
    
    if os.path.exists("silver/clean_vitals.csv"):
        vitals = pd.read_csv("silver/clean_vitals.csv")
        
        anomalies = []
        for idx, row in vitals.iterrows():
            if row["hr"] > 120:
                anomalies.append([row["patient_id"], row["timestamp"], "High HR", row["hr"]])
            if row["ox"] < 92:
                anomalies.append([row["patient_id"], row["timestamp"], "Low Oxygen", row["ox"]])
            if row["sys"] > 160 or row["dia"] > 100:
                anomalies.append([row["patient_id"], row["timestamp"], "High BP", f"{row['sys']}/{row['dia']}"])
        
        anomalies_df = pd.DataFrame(anomalies, columns=["patient_id", "timestamp", "anomaly", "value"])
        anomalies_df.to_csv("gold/anomalies.csv", index=False)
    
    print("Anomaly Detection Completed")
