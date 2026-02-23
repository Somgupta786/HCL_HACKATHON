"""
Hospital Data Pipeline - Streamlit Dashboard
Interactive dashboard for viewing patient data and anomalies
"""

import streamlit as st
import pandas as pd
import os

# Page configuration
st.set_page_config(page_title='Hospital Data Pipeline', layout='wide')

st.title('🏥 Hospital Data Pipeline Dashboard')
st.markdown('---')

# Load data paths
SILVER_PATH = 'hospital_pipeline/silver/'
GOLD_PATH = 'hospital_pipeline/gold/'
VIZ_PATH = 'hospital_pipeline/visualizations/'

# Sidebar navigation
st.sidebar.title('Navigation')
page = st.sidebar.radio('Select View', ['Patient Master', 'Detected Anomalies', 'Visualizations', 'Risk Severity'])

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
