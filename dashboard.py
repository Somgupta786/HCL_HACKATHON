import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Patient Health Monitoring", layout="wide")

def load_data():
    master = pd.read_csv("gold/patient_master.csv") if os.path.exists("gold/patient_master.csv") else None
    vitals = pd.read_csv("silver/clean_vitals.csv") if os.path.exists("silver/clean_vitals.csv") else None
    anomalies = pd.read_csv("gold/anomalies.csv") if os.path.exists("gold/anomalies.csv") else None
    labs = pd.read_csv("silver/clean_labs.csv") if os.path.exists("silver/clean_labs.csv") else None
    return master, vitals, anomalies, labs

master, vitals, anomalies, labs = load_data()

st.title("🏥 Patient Health Monitoring Dashboard")

if master is None:
    st.warning("⚠️ No data available. Please run the pipeline first.")
else:
    # Sidebar - Patient Selection
    st.sidebar.header("Filter Options")
    selected_patient = st.sidebar.selectbox("Select Patient", master['patient_id'].unique())
    
    # Global Statistics
    st.header("📊 Global Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", len(master))
    with col2:
        st.metric("Avg Heart Rate", f"{vitals['hr'].mean():.1f} bpm" if vitals is not None else "N/A")
    with col3:
        st.metric("Avg Oxygen Level", f"{vitals['ox'].mean():.1f}%" if vitals is not None else "N/A")
    with col4:
        if anomalies is not None:
            st.metric("Total Anomalies", len(anomalies))
        else:
            st.metric("Total Anomalies", 0)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Vitals Trends", "Anomalies", "Lab Results", "Patient Info"])
    
    with tab1:
        st.subheader(f"Patient {selected_patient} - Vital Signs Trends")
        if vitals is not None:
            patient_vitals = vitals[vitals['patient_id'] == selected_patient]
            patient_vitals['timestamp'] = pd.to_datetime(patient_vitals['timestamp'])
            patient_vitals = patient_vitals.sort_values('timestamp')
            
            if len(patient_vitals) > 0:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=patient_vitals['timestamp'], y=patient_vitals['hr'], mode='lines+markers', name='Heart Rate'))
                fig.add_hline(y=120, line_dash="dash", line_color="red", annotation_text="HR Threshold (120)")
                fig.update_layout(title="Heart Rate Over Time", xaxis_title="Time", yaxis_title="BPM")
                st.plotly_chart(fig, use_container_width=True)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=patient_vitals['timestamp'], y=patient_vitals['ox'], mode='lines+markers', name='Oxygen Level', line=dict(color='blue')))
                fig.add_hline(y=92, line_dash="dash", line_color="red", annotation_text="O2 Threshold (92%)")
                fig.update_layout(title="Oxygen Level Over Time", xaxis_title="Time", yaxis_title="O2 %")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No vitals data for selected patient")
    
    with tab2:
        st.subheader("Anomaly Detection")
        if anomalies is not None:
            patient_anomalies = anomalies[anomalies['patient_id'] == selected_patient]
            if len(patient_anomalies) > 0:
                st.dataframe(patient_anomalies, use_container_width=True)
                
                anomaly_summary = anomalies['anomaly'].value_counts()
                fig = px.bar(anomaly_summary, title="Anomaly Distribution", labels={'value': 'Count', 'index': 'Anomaly Type'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success(f"✅ No anomalies detected for patient {selected_patient}")
        else:
            st.info("No anomaly data available")
    
    with tab3:
        st.subheader("Lab Results")
        if labs is not None:
            patient_labs = labs[labs['patient_id'] == selected_patient]
            if len(patient_labs) > 0:
                st.dataframe(patient_labs, use_container_width=True)
            else:
                st.info("No lab results for selected patient")
        else:
            st.info("No lab data available")
    
    with tab4:
        st.subheader(f"Patient {selected_patient} Information")
        patient_info = master[master['patient_id'] == selected_patient]
        if len(patient_info) > 0:
            st.dataframe(patient_info, use_container_width=True)
        else:
            st.info("No patient information found")
