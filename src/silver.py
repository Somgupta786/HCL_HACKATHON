"""Silver layer - Data cleaning and standardization with EDA."""
import pandas as pd
import numpy as np


def clean_vitals():
    """Clean vitals data - keep original values for anomaly detection."""
    df = pd.read_csv('bronze/vitals.csv')
    
    # Rename columns
    df = df.rename(columns={'patientId': 'patient_id'})
    
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    # Convert to numeric - keep original values, no capping
    df['hr'] = pd.to_numeric(df['hr'], errors='coerce')
    df['ox'] = pd.to_numeric(df['ox'], errors='coerce')
    df['sys'] = pd.to_numeric(df['sys'], errors='coerce')
    df['dia'] = pd.to_numeric(df['dia'], errors='coerce')
    
    # Remove duplicates only
    df = df.drop_duplicates()
    
    # Fill only missing values with median - DO NOT cap outliers
    df['hr'] = df['hr'].fillna(df['hr'].median())
    df['ox'] = df['ox'].fillna(df['ox'].median())
    df['sys'] = df['sys'].fillna(df['sys'].median())
    df['dia'] = df['dia'].fillna(df['dia'].median())
    
    df.to_csv('silver/clean_vitals.csv', index=False)


def clean_labs():
    """Clean labs data with EDA-based preprocessing."""
    df = pd.read_csv('bronze/labs.csv')
    
    # Rename columns
    df = df.rename(columns={
        'test': 'lab_test',
        'value': 'lab_value'
    })
    
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Convert to numeric
    df['lab_value'] = pd.to_numeric(df['lab_value'], errors='coerce')
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Fill missing values with median per test type
    df['lab_value'] = df.groupby('lab_test')['lab_value'].transform(
        lambda x: x.fillna(x.median())
    )
    
    df.to_csv('silver/clean_labs.csv', index=False)


def clean_ehr():
    """Clean EHR data with EDA-based preprocessing."""
    df = pd.read_csv('bronze/ehr.csv')
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Convert admission_time to datetime
    df['admission_time'] = pd.to_datetime(df['admission_time'])
    
    # Handle missing values
    df['age'] = df['age'].fillna(df['age'].median())
    df['gender'] = df['gender'].fillna(df['gender'].mode()[0])
    df['name'] = df['name'].fillna('Unknown')
    
    # Standardize gender values
    df['gender'] = df['gender'].str.upper()
    
    return df


def create_patient_master():
    """Create patient master table with latest vitals and labs."""
    ehr = clean_ehr()
    vitals = pd.read_csv('silver/clean_vitals.csv')
    vitals['timestamp'] = pd.to_datetime(vitals['timestamp'])
    labs = pd.read_csv('silver/clean_labs.csv')
    labs['timestamp'] = pd.to_datetime(labs['timestamp'])
    
    # Get latest vitals per patient
    vitals_sorted = vitals.sort_values('timestamp')
    latest_vitals = vitals_sorted.groupby('patient_id').tail(1)
    latest_vitals = latest_vitals.drop('timestamp', axis=1)
    
    # Get latest lab per patient per test
    labs_sorted = labs.sort_values('timestamp')
    latest_labs = labs_sorted.groupby(['patient_id', 'lab_test']).tail(1)
    latest_labs = latest_labs.drop('timestamp', axis=1)
    latest_labs_pivot = latest_labs.pivot(index='patient_id', columns='lab_test', values='lab_value').reset_index()
    
    # Merge all - keep None/NULL for missing data
    master = ehr.merge(latest_vitals, on='patient_id', how='left')
    master = master.merge(latest_labs_pivot, on='patient_id', how='left')
    
    # Do NOT fill nulls - keep them as None to indicate missing tests/vitals
    master.to_csv('silver/patient_master.csv', index=False)


def run_silver():
    """Execute all silver layer processing."""
    clean_vitals()
    clean_labs()
    create_patient_master()
