"""
Hospital Data Pipeline - Streamlit Dashboard
Interactive dashboard for viewing patient data and anomalies
"""

import streamlit as st
import pandas as pd
import os
import subprocess
import sys
from pathlib import Path

# Page configuration
st.set_page_config(page_title='Hospital Data Pipeline', layout='wide')

# Function to run the pipeline
@st.cache_data
def run_pipeline():
    """Execute the main.py pipeline script"""
    try:
        # Set environment to handle Unicode on Windows
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            [sys.executable, 'main.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=os.path.dirname(__file__) or '.',
            env=env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

# Check if output data exists, if not run pipeline automatically
def check_data_exists():
    """Check if the pipeline has been run and data exists"""
    required_files = [
        'silver/patient_master.csv',
        'gold/anomalies.csv',
        'visualizations/hr_trend.png'
    ]
    return all(os.path.exists(f) for f in required_files)

# Auto-run pipeline on first load if data doesn't exist
if not check_data_exists():
    with st.spinner('🔄 Running pipeline for the first time... This may take a moment.'):
        success, stdout, stderr = run_pipeline()
        if not success:
            st.error(f'Pipeline failed: {stderr}')
        else:
            st.success('✅ Pipeline completed successfully!')

st.title('🏥 Hospital Data Pipeline Dashboard')
st.markdown('---')

# Load data paths
SILVER_PATH = 'silver/'
GOLD_PATH = 'gold/'
VIZ_PATH = 'visualizations/'

# Sidebar navigation
st.sidebar.title('Navigation')
page = st.sidebar.radio('Select View', ['Patient Master', 'Detected Anomalies', 'Visualizations', 'Risk Severity'])

st.sidebar.markdown('---')

# Add buttons to manage pipeline
st.sidebar.markdown('### 🔧 Pipeline Controls')

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button('▶️ Run Pipeline'):
        with st.spinner('🔄 Running pipeline...'):
            st.cache_data.clear()
            success, stdout, stderr = run_pipeline()
            if success:
                st.success('✅ Pipeline completed!')
                st.rerun()
            else:
                st.error(f'❌ Pipeline failed: {stderr}')

with col2:
    if st.button('🔄 Refresh'):
        st.cache_data.clear()
        st.rerun()

st.sidebar.markdown('---')
st.sidebar.markdown('### 📝 Instructions')
st.sidebar.info(
    """
    1. **Edit Data**: Modify the CSV files (e.g., `ehr.csv`)
    2. **Run Pipeline**: Click "▶️ Run Pipeline" button
    3. **View Dashboard**: Results auto-load
    4. **Refresh**: Click "🔄 Refresh" if needed
    """
)

# ============ 1. Patient Master Table ============
if page == 'Patient Master':
    st.header('📋 Patient Master Table')
    
    patient_master_path = f'{SILVER_PATH}patient_master.csv'
    if os.path.exists(patient_master_path):
        df = pd.read_csv(patient_master_path)
        
        st.markdown(f'**Total Patients:** {len(df)}')
        st.dataframe(df, use_container_width=True)
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label='Download Patient Master CSV',
            data=csv,
            file_name='patient_master.csv',
            mime='text/csv'
        )
    else:
        st.warning('Patient master data not found. Please run the pipeline first.')

# ============ 2. Detected Anomalies ============
elif page == 'Detected Anomalies':
    st.header('⚠️ Detected Anomalies')
    
    anomalies_path = f'{GOLD_PATH}anomalies.csv'
    if os.path.exists(anomalies_path):
        df = pd.read_csv(anomalies_path)
        
        st.markdown(f'**Total Anomalies Detected:** {len(df)}')
        
        # Filter by patient
        patients = df['patient_id'].unique()
        selected_patient = st.selectbox('Filter by Patient:', ['All'] + list(patients))
        
        if selected_patient != 'All':
            df = df[df['patient_id'] == selected_patient]
        
        st.dataframe(df, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Total Anomalies', len(df))
        with col2:
            st.metric('Unique Patients', df['patient_id'].nunique())
        with col3:
            st.metric('Anomaly Types', df['anomaly'].nunique())
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label='Download Anomalies CSV',
            data=csv,
            file_name='anomalies.csv',
            mime='text/csv'
        )
    else:
        st.warning('Anomaly data not found. Please run the pipeline first.')

# ============ 3. Visualizations ============
elif page == 'Visualizations':
    st.header('📊 Data Visualizations')
    
    viz_files = [f for f in os.listdir(VIZ_PATH) if f.endswith('.png')] if os.path.exists(VIZ_PATH) else []
    
    if viz_files:
        # Create tabs for each visualization
        tabs = st.tabs([f.replace('.png', '').replace('_', ' ').title() for f in viz_files])
        
        for tab, viz_file in zip(tabs, viz_files):
            with tab:
                st.image(f'{VIZ_PATH}{viz_file}', use_column_width=True)
    else:
        st.warning('Visualizations not found. Please run the pipeline first.')

# ============ 4. Risk Severity ============
elif page == 'Risk Severity':
    st.header('⚕️ Risk Severity Analysis')
    
    patient_master_path = f'{SILVER_PATH}patient_master.csv'
    if os.path.exists(patient_master_path):
        df = pd.read_csv(patient_master_path)
        
        if 'severity' in df.columns:
            # Severity summary
            severity_counts = df['severity'].value_counts()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('High Risk Patients', severity_counts.get('High', 0), delta=None)
            with col2:
                st.metric('Medium Risk Patients', severity_counts.get('Medium', 0), delta=None)
            with col3:
                st.metric('Normal Risk Patients', severity_counts.get('Normal', 0), delta=None)
            
            st.markdown('---')
            
            # Detailed patient severity table
            st.subheader('Patient Risk Severity Details')
            severity_df = df[['patient_id', 'name', 'age', 'severity', 'risk_score']].copy()
            severity_df = severity_df.sort_values('risk_score', ascending=False)
            
            st.dataframe(severity_df, use_container_width=True)
            
            # Filter by severity
            selected_severity = st.selectbox('Filter by Severity:', ['All', 'High', 'Medium', 'Normal'])
            if selected_severity != 'All':
                filtered_df = severity_df[severity_df['severity'] == selected_severity]
                st.write(f"**Patients with {selected_severity} Risk:**")
                st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info('Risk severity data not available. Please run the full pipeline.')
    else:
        st.warning('Patient data not found. Please run the pipeline first.')

st.markdown('---')
st.markdown('**Hospital Data Pipeline Dashboard** © 2024 | Powered by Streamlit')
