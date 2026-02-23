"""Gold layer - Anomaly detection."""
import pandas as pd


def detect_anomalies():
    """Detect anomalies in vitals data."""
    df = pd.read_csv('silver/clean_vitals.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    anomalies = []
    
    for _, row in df.iterrows():
        if pd.notna(row['hr']) and row['hr'] > 120:
            anomalies.append({
                'patient_id': row['patient_id'],
                'timestamp': row['timestamp'],
                'anomaly': 'High Heart Rate',
                'value': row['hr']
            })
        
        if pd.notna(row['ox']) and row['ox'] < 92:
            anomalies.append({
                'patient_id': row['patient_id'],
                'timestamp': row['timestamp'],
                'anomaly': 'Low Oxygen',
                'value': row['ox']
            })
        
        if pd.notna(row['sys']) and pd.notna(row['dia']):
            if row['sys'] > 160 or row['dia'] > 100:
                anomalies.append({
                    'patient_id': row['patient_id'],
                    'timestamp': row['timestamp'],
                    'anomaly': 'High Blood Pressure',
                    'value': f"{row['sys']}/{row['dia']}"
                })
    
    anomalies_df = pd.DataFrame(anomalies)
    anomalies_df.to_csv('gold/anomalies.csv', index=False)


def run_gold():
    """Execute all gold layer processing."""
    detect_anomalies()
