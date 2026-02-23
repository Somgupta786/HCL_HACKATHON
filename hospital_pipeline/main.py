"""
Hospital Data Pipeline - Main Module
Handles ETL, anomaly detection, risk scoring, and visualizations
"""

import pandas as pd
import json
import os
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import time

# Configure logging
log_file = 'pipeline.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Folder paths
BRONZE_PATH = 'hospital_pipeline/bronze/'
SILVER_PATH = 'hospital_pipeline/silver/'
GOLD_PATH = 'hospital_pipeline/gold/'
VIZ_PATH = 'hospital_pipeline/visualizations/'


class HospitalPipeline:
    """Hospital data pipeline processor"""
    
    def __init__(self):
        self.ehr_df = None
        self.vitals_df = None
        self.labs_df = None
        self.patient_master = None
        self.anomalies = None
        
    # ============ STEP 1 & 2: Read Input Files and Store in Bronze ============
    def read_and_store_bronze(self):
        """Read input files and store raw data in bronze folder"""
        logger.info("STEP 1 & 2: Reading input files and storing in bronze folder...")
        
        # Read EHR data
        try:
            self.ehr_df = pd.read_csv('hospital_pipeline/ehr.csv')
            # Store in bronze
            self.ehr_df.to_csv(f'{BRONZE_PATH}ehr_raw.csv', index=False)
            logger.info(f"[OK] EHR data read: {len(self.ehr_df)} patients")
        except Exception as e:
            logger.error(f"[ERR] Error reading EHR: {e}")
        
        # Read Vitals data from JSONL
        try:
            vitals_list = []
            with open('hospital_pipeline/vitals.jsonl', 'r') as f:
                for line in f:
                    vitals_list.append(json.loads(line))
            self.vitals_df = pd.DataFrame(vitals_list)
            # Store in bronze
            self.vitals_df.to_csv(f'{BRONZE_PATH}vitals_raw.csv', index=False)
            logger.info(f"[OK] Vitals data read: {len(self.vitals_df)} records")
        except Exception as e:
            logger.error(f"[ERR] Error reading Vitals: {e}")
        
        # Read Labs data from JSON
        try:
            with open('hospital_pipeline/labs.json', 'r') as f:
                labs_list = json.load(f)
            self.labs_df = pd.DataFrame(labs_list)
            # Store in bronze
            self.labs_df.to_csv(f'{BRONZE_PATH}labs_raw.csv', index=False)
            logger.info(f"[OK] Labs data read: {len(self.labs_df)} records")
        except Exception as e:
            logger.error(f"[ERR] Error reading Labs: {e}")
    
    # ============ STEP 3 & 4: Clean Data and Store in Silver ============
    def clean_data(self):
        """Clean data - convert timestamps, ensure numeric, remove nulls, standardize columns"""
        logger.info("STEP 3 & 4: Cleaning data...")
        
        # Clean EHR data
        self.ehr_df['admission_date'] = pd.to_datetime(self.ehr_df['admission_date'])
        self.ehr_df['discharge_date'] = pd.to_datetime(self.ehr_df['discharge_date'])
        self.ehr_df['age'] = pd.to_numeric(self.ehr_df['age'], errors='coerce')
        self.ehr_df.dropna(subset=['patient_id'], inplace=True)
        logger.info(f"[OK] EHR data cleaned: {len(self.ehr_df)} records")
        
        # Clean Vitals data
        if self.vitals_df is not None:
            self.vitals_df['timestamp'] = pd.to_datetime(self.vitals_df['timestamp'])
            self.vitals_df['heart_rate'] = pd.to_numeric(self.vitals_df['heart_rate'], errors='coerce')
            self.vitals_df['oxygen'] = pd.to_numeric(self.vitals_df['oxygen'], errors='coerce')
            self.vitals_df['sys_bp'] = pd.to_numeric(self.vitals_df['sys_bp'], errors='coerce')
            self.vitals_df['dia_bp'] = pd.to_numeric(self.vitals_df['dia_bp'], errors='coerce')
            self.vitals_df.dropna(inplace=True)
            logger.info(f"[OK] Vitals data cleaned: {len(self.vitals_df)} records")
        
        # Clean Labs data
        if self.labs_df is not None:
            self.labs_df['test_date'] = pd.to_datetime(self.labs_df['test_date'])
            self.labs_df['glucose'] = pd.to_numeric(self.labs_df['glucose'], errors='coerce')
            self.labs_df['hemoglobin'] = pd.to_numeric(self.labs_df['hemoglobin'], errors='coerce')
            self.labs_df['creatinine'] = pd.to_numeric(self.labs_df['creatinine'], errors='coerce')
            self.labs_df.dropna(inplace=True)
            logger.info(f"[OK] Labs data cleaned: {len(self.labs_df)} records")
        
        # Save cleaned data to silver
        self.ehr_df.to_csv(f'{SILVER_PATH}ehr_clean.csv', index=False)
        if self.vitals_df is not None:
            self.vitals_df.to_csv(f'{SILVER_PATH}vitals_clean.csv', index=False)
        if self.labs_df is not None:
            self.labs_df.to_csv(f'{SILVER_PATH}labs_clean.csv', index=False)
    
    # ============ STEP 5 & 6: Create Patient Master Table with Joins ============
    def create_patient_master(self):
        """Join EHR + latest vitals + latest labs"""
        logger.info("STEP 5 & 6: Creating patient master table...")
        
        # Get latest vitals per patient
        latest_vitals = self.vitals_df.sort_values('timestamp').groupby('patient_id').tail(1)[
            ['patient_id', 'heart_rate', 'oxygen', 'sys_bp', 'dia_bp', 'timestamp']
        ].rename(columns={'timestamp': 'vitals_timestamp'})
        
        # Get latest labs per patient
        latest_labs = self.labs_df.sort_values('test_date').groupby('patient_id').tail(1)[
            ['patient_id', 'glucose', 'hemoglobin', 'creatinine', 'test_date']
        ].rename(columns={'test_date': 'labs_date'})
        
        # Merge all tables
        self.patient_master = self.ehr_df.merge(latest_vitals, on='patient_id', how='left')
        self.patient_master = self.patient_master.merge(latest_labs, on='patient_id', how='left')
        
        logger.info(f"[OK] Patient master table created: {len(self.patient_master)} patients")
        
        # Save patient master
        self.patient_master.to_csv(f'{SILVER_PATH}patient_master.csv', index=False)
    
    # ============ STEP 7: Anomaly Detection ============
    def detect_anomalies(self):
        """Apply rule-based anomaly detection"""
        logger.info("STEP 7: Detecting anomalies...")
        
        anomalies_list = []
        
        for _, row in self.vitals_df.iterrows():
            anomaly_found = False
            anomaly_type = []
            max_value = None
            
            # Check Heart Rate >120
            if row['heart_rate'] > 120:
                anomaly_found = True
                anomaly_type.append('High HR')
                max_value = row['heart_rate']
            
            # Check Oxygen <92
            if row['oxygen'] < 92:
                anomaly_found = True
                anomaly_type.append('Low Oxygen')
                max_value = row['oxygen']
            
            # Check SYS>160 or DIA>100
            if row['sys_bp'] > 160 or row['dia_bp'] > 100:
                anomaly_found = True
                anomaly_type.append('High BP')
                max_value = max(row['sys_bp'], row['dia_bp'])
            
            if anomaly_found:
                anomalies_list.append({
                    'patient_id': row['patient_id'],
                    'timestamp': row['timestamp'],
                    'anomaly': ' | '.join(anomaly_type),
                    'value': max_value
                })
        
        self.anomalies = pd.DataFrame(anomalies_list)
        logger.info(f"[OK] Anomalies detected: {len(self.anomalies)} records")
        
        # Save anomalies
        self.anomalies.to_csv(f'{GOLD_PATH}anomalies.csv', index=False)
    
    # ============ ADVANCED FEATURE 1: Risk Severity Score ============
    def calculate_risk_severity(self):
        """Calculate health risk score based on anomalies"""
        logger.info("Feature 1: Calculating risk severity scores...")
        
        def calculate_score(row):
            score = 0
            
            # High HR (+2)
            if pd.notna(row['heart_rate']) and row['heart_rate'] > 120:
                score += 2
            
            # Low Oxygen (+3)
            if pd.notna(row['oxygen']) and row['oxygen'] < 92:
                score += 3
            
            # High BP (+2)
            if (pd.notna(row['sys_bp']) and row['sys_bp'] > 160) or \
               (pd.notna(row['dia_bp']) and row['dia_bp'] > 100):
                score += 2
            
            # Determine severity
            if score >= 5:
                return 'High', score
            elif score >= 2:
                return 'Medium', score
            else:
                return 'Normal', score
        
        self.patient_master[['severity', 'risk_score']] = self.patient_master.apply(
            lambda row: pd.Series(calculate_score(row)), axis=1
        )
        
        logger.info("[OK] Risk severity scores calculated")
        self.patient_master.to_csv(f'{SILVER_PATH}patient_master.csv', index=False)
    
    # ============ ADVANCED FEATURE 2: Real-Time Simulation ============
    def simulate_realtime_processing(self):
        """Simulate streaming vitals processing"""
        logger.info("Feature 2: Simulating real-time vitals processing...")
        
        realtime_anomalies = []
        
        for idx, row in self.vitals_df.iterrows():
            time.sleep(0.5)  # Simulate processing delay
            
            anomalies = []
            if row['heart_rate'] > 120:
                anomalies.append('High HR')
            if row['oxygen'] < 92:
                anomalies.append('Low Oxygen')
            if row['sys_bp'] > 160 or row['dia_bp'] > 100:
                anomalies.append('High BP')
            
            if anomalies:
                logger.info(f"[STREAM] {row['patient_id']} @ {row['timestamp']}: {', '.join(anomalies)}")
                realtime_anomalies.append({
                    'patient_id': row['patient_id'],
                    'timestamp': row['timestamp'],
                    'anomalies': ', '.join(anomalies)
                })
        
        logger.info(f"[OK] Real-time simulation complete: {len(realtime_anomalies)} anomalies detected")
    
    # ============ ADVANCED FEATURE 3: Comprehensive Logging ============
    # Logging is integrated throughout the pipeline (see logger calls)
    
    # ============ STEP 8: Create Visualizations ============
    def create_visualizations(self):
        """Generate and save charts"""
        logger.info("STEP 8: Creating visualizations...")
        
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 1. Oxygen distribution histogram
        plt.figure(figsize=(10, 6))
        plt.hist(self.vitals_df['oxygen'], bins=15, color='skyblue', edgecolor='black', alpha=0.7)
        plt.xlabel('Oxygen Level (%)')
        plt.ylabel('Frequency')
        plt.title('Oxygen Level Distribution')
        plt.axvline(x=92, color='red', linestyle='--', linewidth=2, label='Low Oxygen Threshold (92)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{VIZ_PATH}oxygen_distribution.png', dpi=300)
        plt.close()
        logger.info("[OK] Oxygen distribution chart created")
        
        # 2. Anomaly count bar chart
        if len(self.anomalies) > 0:
            anomaly_counts = self.anomalies['patient_id'].value_counts()
            plt.figure(figsize=(10, 6))
            anomaly_counts.plot(kind='bar', color='coral', edgecolor='black', alpha=0.7)
            plt.xlabel('Patient ID')
            plt.ylabel('Anomaly Count')
            plt.title('Anomaly Count by Patient')
            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.savefig(f'{VIZ_PATH}anomaly_count.png', dpi=300)
            plt.close()
            logger.info("[OK] Anomaly count chart created")
        
        # 3. Heart rate trend per patient
        plt.figure(figsize=(12, 6))
        for patient_id in self.vitals_df['patient_id'].unique():
            patient_data = self.vitals_df[self.vitals_df['patient_id'] == patient_id]
            plt.plot(patient_data['timestamp'], patient_data['heart_rate'], marker='o', label=patient_id)
        plt.xlabel('Timestamp')
        plt.ylabel('Heart Rate (bpm)')
        plt.title('Heart Rate Trend by Patient')
        plt.axhline(y=120, color='red', linestyle='--', linewidth=2, label='High HR Threshold (120)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{VIZ_PATH}heart_rate_trend.png', dpi=300)
        plt.close()
        logger.info("[OK] Heart rate trend chart created")
    
    # ============ STEP 9: Generate Severity Distribution Chart ============
    def create_severity_chart(self):
        """Create visualization for risk severity distribution"""
        logger.info("Creating severity distribution chart...")
        
        if 'severity' in self.patient_master.columns:
            severity_counts = self.patient_master['severity'].value_counts()
            plt.figure(figsize=(8, 6))
            colors = {'High': 'red', 'Medium': 'orange', 'Normal': 'green'}
            severity_counts.plot(kind='bar', color=[colors.get(x, 'gray') for x in severity_counts.index],
                                edgecolor='black', alpha=0.7)
            plt.xlabel('Severity Level')
            plt.ylabel('Patient Count')
            plt.title('Patient Risk Severity Distribution')
            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.savefig(f'{VIZ_PATH}severity_distribution.png', dpi=300)
            plt.close()
            logger.info("[OK] Severity distribution chart created")
    
    def run_pipeline(self):
        """Execute complete pipeline"""
        logger.info("=" * 70)
        logger.info("HOSPITAL DATA PIPELINE EXECUTION STARTED")
        logger.info("=" * 70)
        
        try:
            # Step 1 & 2: Read and Bronze
            self.read_and_store_bronze()
            
            # Step 3 & 4: Clean and Silver
            self.clean_data()
            
            # Step 5 & 6: Create Master
            self.create_patient_master()
            
            # Step 7: Anomalies
            self.detect_anomalies()
            
            # Feature 1: Risk Scoring
            self.calculate_risk_severity()
            
            # Feature 2: Real-time Simulation
            self.simulate_realtime_processing()
            
            # Step 8: Visualizations
            self.create_visualizations()
            self.create_severity_chart()
            
            logger.info("=" * 70)
            logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
            logger.info(f"Bronze Layer: {len(os.listdir(BRONZE_PATH))} files")
            logger.info(f"Silver Layer: {len(os.listdir(SILVER_PATH))} files")
            logger.info(f"Gold Layer: {len(os.listdir(GOLD_PATH))} files")
            logger.info(f"Visualizations: {len(os.listdir(VIZ_PATH))} files")
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)


if __name__ == '__main__':
    pipeline = HospitalPipeline()
    pipeline.run_pipeline()
