import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_visualizations():
    print("Generating Visualizations...")
    
    os.makedirs("visualizations", exist_ok=True)
    
    if not os.path.exists("silver/clean_vitals.csv"):
        print("No vitals data found")
        return
    
    vitals = pd.read_csv("silver/clean_vitals.csv")
    
    # 1. Heart Rate Trend
    print("Creating Heart Rate Trend visualization...")
    plt.figure(figsize=(12, 6))
    for patient in vitals['patient_id'].unique():
        patient_data = vitals[vitals['patient_id'] == patient].sort_values('timestamp')
        plt.plot(range(len(patient_data)), patient_data['hr'], marker='o', label=patient)
    plt.axhline(y=120, color='r', linestyle='--', label='Threshold (120)')
    plt.xlabel('Time')
    plt.ylabel('Heart Rate (bpm)')
    plt.title('Heart Rate Trends')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('visualizations/hr_trend.png', dpi=300)
    plt.close()
    
    # 2. Oxygen Distribution
    print("Creating Oxygen Level Distribution visualization...")
    plt.figure(figsize=(10, 6))
    plt.hist(vitals['ox'], bins=20, color='blue', edgecolor='black')
    plt.axvline(x=92, color='r', linestyle='--', label='Threshold (92)')
    plt.xlabel('Oxygen Level (%)')
    plt.ylabel('Frequency')
    plt.title('Oxygen Level Distribution')
    plt.legend()
    plt.tight_layout()
    plt.savefig('visualizations/oxygen_distribution.png', dpi=300)
    plt.close()
    
    # 3. Blood Pressure Distribution
    print("Creating Blood Pressure visualization...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.hist(vitals['sys'], bins=20, color='green', edgecolor='black')
    ax1.axvline(x=160, color='r', linestyle='--', label='Threshold (160)')
    ax1.set_xlabel('Systolic BP')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Systolic Blood Pressure Distribution')
    ax1.legend()
    
    ax2.hist(vitals['dia'], bins=20, color='orange', edgecolor='black')
    ax2.axvline(x=100, color='r', linestyle='--', label='Threshold (100)')
    ax2.set_xlabel('Diastolic BP')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Diastolic Blood Pressure Distribution')
    ax2.legend()
    plt.tight_layout()
    plt.savefig('visualizations/blood_pressure_distribution.png', dpi=300)
    plt.close()
    
    # 4. Anomaly Counts
    if os.path.exists("gold/anomalies.csv"):
        print("Creating Anomaly Count visualization...")
        anomalies = pd.read_csv("gold/anomalies.csv")
        anomaly_counts = anomalies['anomaly'].value_counts()
        plt.figure(figsize=(10, 6))
        anomaly_counts.plot(kind='bar', color=['red', 'orange', 'yellow'])
        plt.xlabel('Anomaly Type')
        plt.ylabel('Count')
        plt.title('Anomaly Distribution')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('visualizations/anomaly_counts.png', dpi=300)
        plt.close()
        
        # 5. Anomaly Timeline
        print("Creating Anomaly Timeline visualization...")
        anomalies['timestamp'] = pd.to_datetime(anomalies['timestamp'])
        plt.figure(figsize=(12, 6))
        for anomaly_type in anomalies['anomaly'].unique():
            data = anomalies[anomalies['anomaly'] == anomaly_type]
            plt.scatter(data['timestamp'], [anomaly_type]*len(data), label=anomaly_type, s=100)
        plt.xlabel('Time')
        plt.ylabel('Anomaly Type')
        plt.title('Anomaly Timeline')
        plt.legend()
        plt.tight_layout()
        plt.savefig('visualizations/anomaly_timeline.png', dpi=300)
        plt.close()
        
        # 6. Patient Anomaly Summary
        print("Creating Patient Anomaly Summary visualization...")
        patient_anomalies = anomalies['patient_id'].value_counts()
        plt.figure(figsize=(12, 6))
        patient_anomalies.plot(kind='bar', color='red')
        plt.xlabel('Patient ID')
        plt.ylabel('Number of Anomalies')
        plt.title('Anomalies per Patient')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('visualizations/patient_anomaly_counts.png', dpi=300)
        plt.close()
    
    # 7. Vital Signs Box Plot
    print("Creating Box Plot visualization...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    sns.boxplot(data=vitals, y='hr', ax=axes[0, 0])
    axes[0, 0].set_title('Heart Rate Distribution')
    axes[0, 0].axhline(y=120, color='r', linestyle='--', alpha=0.5)
    
    sns.boxplot(data=vitals, y='ox', ax=axes[0, 1])
    axes[0, 1].set_title('Oxygen Level Distribution')
    axes[0, 1].axhline(y=92, color='r', linestyle='--', alpha=0.5)
    
    sns.boxplot(data=vitals, y='sys', ax=axes[1, 0])
    axes[1, 0].set_title('Systolic BP Distribution')
    axes[1, 0].axhline(y=160, color='r', linestyle='--', alpha=0.5)
    
    sns.boxplot(data=vitals, y='dia', ax=axes[1, 1])
    axes[1, 1].set_title('Diastolic BP Distribution')
    axes[1, 1].axhline(y=100, color='r', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('visualizations/vital_signs_boxplot.png', dpi=300)
    plt.close()
    
    print("✅ All Visualizations Completed Successfully!")
    print("Saved visualizations to: visualizations/")
