"""
Hospital Health Monitoring Dashboard
Streamlit UI to display visualizations and insights
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="Hospital Health Monitoring",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Title and header
st.title("🏥 Hospital Health Monitoring Dashboard")
st.markdown("---")
st.markdown("### Real-time Patient Monitoring and Anomaly Detection System")
st.markdown("*Powered by Bronze → Silver → Gold Data Pipeline*")
st.markdown("---")


# Check if pipeline has been run
def check_pipeline_status():
    """Check if visualizations exist"""
    viz_dir = Path("visualizations")
    required_files = ['hr_trend.png', 'oxygen_distribution.png', 'anomaly_counts.png']
    
    if not viz_dir.exists():
        return False, "Visualizations folder not found"
    
    missing_files = [f for f in required_files if not (viz_dir / f).exists()]
    
    if missing_files:
        return False, f"Missing visualizations: {', '.join(missing_files)}"
    
    return True, "All visualizations ready"


# Check status
status_ok, status_msg = check_pipeline_status()

if not status_ok:
    st.warning("⚠️ Pipeline not yet executed!")
    st.info(f"**Issue:** {status_msg}")
    st.markdown("### 📝 To get started:")
    st.code("python main.py", language="bash")
    st.markdown("This will process all data and generate visualizations.")
    st.stop()


# Sidebar
with st.sidebar:
    st.header("📊 Navigation")
    st.markdown("---")
    
    page = st.radio(
        "Select View",
        ["🏠 Overview", "📈 Heart Rate Trends", "🫁 Oxygen Analysis", 
         "🚨 Anomalies", "📋 Data Summary"]
    )
    
    st.markdown("---")
    st.markdown("### 🔄 Pipeline Layers")
    st.markdown("""
    - **🟤 Bronze**: Raw storage  
    - **⚪ Silver**: Cleaned data  
    - **🟡 Gold**: Analytics  
    """)
    
    st.markdown("---")
    st.info("**Tech Stack:**  \nPython • Pandas • Matplotlib • Streamlit")
    
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Data refreshed!")
        st.rerun()
    
    # Show last update time
    if Path("gold/anomalies.csv").exists():
        last_modified = datetime.fromtimestamp(Path("gold/anomalies.csv").stat().st_mtime)
        st.caption(f"📅 Last updated: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")


# Load data for statistics
@st.cache_data
def load_data():
    """Load processed data"""
    data = {}
    
    if Path("silver/patient_master.csv").exists():
        data['patient_master'] = pd.read_csv("silver/patient_master.csv")
    
    if Path("gold/anomalies.csv").exists():
        data['anomalies'] = pd.read_csv("gold/anomalies.csv")
    
    if Path("silver/clean_vitals.csv").exists():
        data['vitals'] = pd.read_csv("silver/clean_vitals.csv")
    
    return data


data = load_data()


# ==================== PAGE: OVERVIEW ====================

if page == "🏠 Overview":
    st.header("🏠 Dashboard Overview")
    
    # Data refresh instructions
    with st.expander("ℹ️ How to update data", expanded=False):
        st.markdown("""
        **To reflect changes from the data folder:**
        1. Add/modify files in the `data/` folder (Excel, Word, CSV, JSON)
        2. Run: `python main.py` to process the data
        3. Click the **🔄 Refresh Data** button in the sidebar
        4. Dashboard will automatically show updated results
        """)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'patient_master' in data:
            st.metric("Total Patients", len(data['patient_master']))
        else:
            st.metric("Total Patients", "N/A")
    
    with col2:
        if 'anomalies' in data:
            st.metric("Active Anomalies", len(data['anomalies']), 
                     delta=None, delta_color="inverse")
        else:
            st.metric("Active Anomalies", 0)
    
    with col3:
        if 'vitals' in data:
            st.metric("Vitals Records", len(data['vitals']))
        else:
            st.metric("Vitals Records", "N/A")
    
    with col4:
        if 'patient_master' in data and 'age' in data['patient_master'].columns:
            avg_age = data['patient_master']['age'].mean()
            st.metric("Avg Patient Age", f"{avg_age:.1f} yrs")
        else:
            st.metric("Avg Patient Age", "N/A")
    
    st.markdown("---")
    
    # All visualizations in overview
    st.subheader("📊 Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💓 Heart Rate Trends")
        img = Image.open("visualizations/hr_trend.png")
        st.image(img, use_container_width=True)
        st.caption("Multi-patient heart rate monitoring over time with danger threshold (>120 bpm)")
    
    with col2:
        st.markdown("#### 🚨 Anomaly Distribution")
        img = Image.open("visualizations/anomaly_counts.png")
        st.image(img, use_container_width=True)
        st.caption("Count of detected anomalies by type across all patients")
    
    st.markdown("---")
    
    st.markdown("#### 🫁 Oxygen Saturation Analysis")
    img = Image.open("visualizations/oxygen_distribution.png")
    st.image(img, use_container_width=True)
    st.caption("Distribution of oxygen levels with danger threshold marked at 92%")


# ==================== PAGE: HEART RATE TRENDS ====================

elif page == "📈 Heart Rate Trends":
    st.header("📈 Heart Rate Trend Analysis")
    
    st.markdown("""
    This visualization shows heart rate (HR) trends for all patients over time.
    
    **Anomaly Rule:**  
    - 🔴 **High Heart Rate**: HR > 120 bpm  
    
    **Normal Range:**  
    - Resting heart rate typically ranges from 60-100 bpm  
    - Values above 120 bpm may indicate tachycardia and require medical attention
    """)
    
    st.markdown("---")
    
    # Display chart
    img = Image.open("visualizations/hr_trend.png")
    st.image(img, use_container_width=True)
    
    # Show patients with high HR anomalies
    if 'anomalies' in data:
        hr_anomalies = data['anomalies'][data['anomalies']['anomaly'] == 'High Heart Rate']
        if len(hr_anomalies) > 0:
            st.markdown("---")
            st.subheader("🚨 Patients with High Heart Rate")
            
            affected_patients = hr_anomalies['patient_id'].unique()
            st.warning(f"**{len(affected_patients)} patient(s)** with elevated heart rate detected")
            
            with st.expander("View Details"):
                st.dataframe(hr_anomalies, use_container_width=True)


# ==================== PAGE: OXYGEN ANALYSIS ====================

elif page == "🫁 Oxygen Analysis":
    st.header("🫁 Oxygen Saturation Analysis")
    
    st.markdown("""
    Oxygen saturation (SpO₂) measures the percentage of hemoglobin binding sites occupied by oxygen.
    
    **Anomaly Rule:**  
    - 🔴 **Low Oxygen**: SpO₂ < 92%  
    
    **Clinical Significance:**  
    - Normal range: 95-100%  
    - 92-94%: May indicate hypoxemia  
    - < 92%: Requires immediate medical attention
    """)
    
    st.markdown("---")
    
    # Display chart
    img = Image.open("visualizations/oxygen_distribution.png")
    st.image(img, use_container_width=True)
    
    # Statistics
    if 'vitals' in data:
        st.markdown("---")
        st.subheader("📊 Oxygen Level Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mean_ox = data['vitals']['ox'].mean()
            st.metric("Mean Oxygen Level", f"{mean_ox:.1f}%")
        
        with col2:
            min_ox = data['vitals']['ox'].min()
            st.metric("Minimum Recorded", f"{min_ox:.1f}%", 
                     delta=f"{min_ox - 92:.1f}%" if min_ox < 92 else None,
                     delta_color="inverse")
        
        with col3:
            low_ox_count = len(data['vitals'][data['vitals']['ox'] < 92])
            st.metric("Low Oxygen Records", low_ox_count)
    
    # Show patients with low oxygen
    if 'anomalies' in data:
        ox_anomalies = data['anomalies'][data['anomalies']['anomaly'] == 'Low Oxygen']
        if len(ox_anomalies) > 0:
            st.markdown("---")
            st.subheader("🚨 Patients with Low Oxygen")
            
            affected_patients = ox_anomalies['patient_id'].unique()
            st.warning(f"**{len(affected_patients)} patient(s)** with low oxygen detected")
            
            with st.expander("View Details"):
                st.dataframe(ox_anomalies, use_container_width=True)


# ==================== PAGE: ANOMALIES ====================

elif page == "🚨 Anomalies":
    st.header("🚨 Anomaly Detection Results")
    
    st.markdown("""
    Rule-based anomaly detection identifies critical health events requiring attention.
    
    **Detection Rules:**
    - 🔴 **High Heart Rate**: HR > 120 bpm
    - 🔴 **Low Oxygen**: SpO₂ < 92%
    - 🔴 **High Blood Pressure**: Systolic > 160 OR Diastolic > 100 mmHg
    """)
    
    st.markdown("---")
    
    # Display anomaly chart
    img = Image.open("visualizations/anomaly_counts.png")
    st.image(img, use_container_width=True)
    
    if 'anomalies' in data and len(data['anomalies']) > 0:
        st.markdown("---")
        st.subheader("📋 Detailed Anomaly Records")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Anomalies", len(data['anomalies']))
        
        with col2:
            affected = data['anomalies']['patient_id'].nunique()
            st.metric("Affected Patients", affected)
        
        with col3:
            types = data['anomalies']['anomaly'].nunique()
            st.metric("Anomaly Types", types)
        
        st.markdown("---")
        
        # Filter options
        anomaly_types = data['anomalies']['anomaly'].unique()
        selected_types = st.multiselect(
            "Filter by Anomaly Type",
            options=anomaly_types,
            default=anomaly_types
        )
        
        filtered_anomalies = data['anomalies'][
            data['anomalies']['anomaly'].isin(selected_types)
        ]
        
        st.dataframe(filtered_anomalies, use_container_width=True, hide_index=True)
        
        # Download option
        csv = filtered_anomalies.to_csv(index=False)
        st.download_button(
            label="📥 Download Anomalies CSV",
            data=csv,
            file_name="anomalies_export.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ No anomalies detected! All patient vitals are within normal ranges.")


# ==================== PAGE: DATA SUMMARY ====================

elif page == "📋 Data Summary":
    st.header("📋 Data Pipeline Summary")
    
    st.markdown("### 🔄 Pipeline Status")
    
    # Check all files
    layers = {
        "🟤 Bronze Layer": ["bronze/ehr.csv", "bronze/vitals.csv", "bronze/labs.csv"],
        "⚪ Silver Layer": ["silver/clean_vitals.csv", "silver/clean_labs.csv", "silver/patient_master.csv"],
        "🟡 Gold Layer": ["gold/anomalies.csv"]
    }
    
    for layer_name, files in layers.items():
        st.markdown(f"#### {layer_name}")
        
        for file_path in files:
            path = Path(file_path)
            if path.exists():
                df = pd.read_csv(path)
                st.success(f"✅ **{path.name}**: {len(df)} records, {len(df.columns)} columns")
            else:
                st.error(f"❌ **{path.name}**: Not found")
        
        st.markdown("")
    
    st.markdown("---")
    
    # Sample patient record
    if 'patient_master' in data:
        st.markdown("### 👤 Sample Patient Record")
        
        patient_ids = data['patient_master']['patient_id'].tolist()
        selected_patient = st.selectbox("Select Patient ID", patient_ids)
        
        patient_record = data['patient_master'][
            data['patient_master']['patient_id'] == selected_patient
        ].iloc[0]
        
        st.markdown("#### Patient Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Demographics:**")
            for col in ['patient_id', 'name', 'age', 'gender']:
                if col in patient_record.index:
                    st.text(f"{col.replace('_', ' ').title()}: {patient_record[col]}")
        
        with col2:
            st.markdown("**Latest Vitals:**")
            vital_cols = [col for col in patient_record.index if 'latest_vitals' in col]
            for col in vital_cols:
                if pd.notna(patient_record[col]):
                    display_name = col.replace('latest_vitals_', '').upper()
                    st.text(f"{display_name}: {patient_record[col]}")


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>🏥 Hospital Health Monitoring System | Built with Python, Pandas, Matplotlib & Streamlit</p>
    <p>Data Pipeline: Bronze → Silver → Gold Architecture</p>
</div>
""", unsafe_allow_html=True)
