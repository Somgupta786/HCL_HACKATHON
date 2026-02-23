"""Streamlit UI for Hospital Data Pipeline."""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from src.utils import create_folders
from src.bronze import run_bronze
from src.silver import run_silver
from src.gold import run_gold
from src.visualize import run_visualizations

st.set_page_config(page_title="Hospital Data Pipeline", layout="wide")

st.title("🏥 Hospital Data Pipeline")
st.markdown("---")

# Sidebar for pipeline control
with st.sidebar:
    st.header("⚙️ Pipeline Control")
    if st.button("🚀 Run Pipeline", type="primary", use_container_width=True):
        with st.spinner("Running pipeline..."):
            st.info("📁 Creating folders...")
            create_folders()
            
            st.info("🥉 BRONZE: Ingesting raw data...")
            run_bronze()
            st.success("✅ Bronze layer completed")
            
            st.info("🥈 SILVER: Cleaning data with EDA...")
            run_silver()
            st.success("✅ Silver layer completed")
            
            st.info("🥇 GOLD: Detecting anomalies...")
            run_gold()
            st.success("✅ Gold layer completed")
            
            st.info("📊 Generating visualizations...")
            run_visualizations()
            st.success("✅ Visualizations generated")
            
            st.balloons()
            st.success("🎉 Pipeline completed successfully!")
    
    st.markdown("---")
    st.header("📊 Quick Stats")
    if Path("silver/patient_master.csv").exists():
        df = pd.read_csv("silver/patient_master.csv")
        st.metric("Total Patients", len(df))
        st.metric("Avg Age", f"{df['age'].mean():.1f}")
        
        if Path("gold/anomalies.csv").exists():
            anom = pd.read_csv("gold/anomalies.csv")
            st.metric("Total Anomalies", len(anom))

st.markdown("---")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visualizations", "🔍 Patient Search", "📋 Data Tables", "📈 EDA"])

with tab1:
    st.header("📊 Pipeline Visualizations")
    
    viz_path = Path("visualizations")
    if viz_path.exists():
        st.subheader("1. Heart Rate Trends (Per Patient)")
        hr_trend = viz_path / "hr_trend.png"
        if hr_trend.exists():
            st.image(str(hr_trend), use_container_width=True, caption="Combined Multi-Line Plot: Timestamp vs Heart Rate")
        
        st.subheader("2. Oxygen Level Distribution")
        ox_dist = viz_path / "oxygen_distribution.png"
        if ox_dist.exists():
            st.image(str(ox_dist), use_container_width=True, caption="Histogram & Boxplot with Low Oxygen Readings Highlighted (OX < 92)")
        
        st.subheader("3. Anomaly Counts")
        anomaly_counts = viz_path / "anomaly_counts.png"
        if anomaly_counts.exists():
            st.image(str(anomaly_counts), use_container_width=True, caption="Bar Chart: Anomaly Type vs Number of Occurrences")
    else:
        st.info("Run the pipeline to generate visualizations")

with tab2:
    st.header("🔍 Patient Search & Filter")
    
    if Path("silver/patient_master.csv").exists():
        df = pd.read_csv("silver/patient_master.csv")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Patient ID filter
            patient_ids = ['All'] + sorted(df['patient_id'].unique().tolist())
            selected_patient = st.selectbox("Filter by Patient ID", patient_ids)
        
        with col2:
            # Gender filter
            genders = ['All'] + sorted(df['gender'].dropna().unique().tolist())
            selected_gender = st.selectbox("Filter by Gender", genders)
        
        with col3:
            # Age range filter
            min_age, max_age = int(df['age'].min()), int(df['age'].max())
            age_range = st.slider("Filter by Age Range", min_age, max_age, (min_age, max_age))
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_patient != 'All':
            filtered_df = filtered_df[filtered_df['patient_id'] == selected_patient]
        
        if selected_gender != 'All':
            filtered_df = filtered_df[filtered_df['gender'] == selected_gender]
        
        filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]
        
        st.markdown(f"### Showing {len(filtered_df)} of {len(df)} patients")
        
        # Search by name
        search_name = st.text_input("🔎 Search by Patient Name", "")
        if search_name:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_name, case=False, na=False)]
        
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Download filtered data
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name='filtered_patients.csv',
            mime='text/csv',
        )
        
        # Show anomalies for filtered patients
        if Path("gold/anomalies.csv").exists() and len(filtered_df) > 0:
            st.markdown("### 🚨 Anomalies for Filtered Patients")
            anom_df = pd.read_csv("gold/anomalies.csv")
            filtered_anom = anom_df[anom_df['patient_id'].isin(filtered_df['patient_id'])]
            
            if len(filtered_anom) > 0:
                st.dataframe(filtered_anom, use_container_width=True)
                st.metric("Anomalies Found", len(filtered_anom))
            else:
                st.success("No anomalies found for selected patients")
    else:
        st.info("Run the pipeline to enable patient search")

with tab3:
    st.header("📋 Data Tables")
    
    subtab1, subtab2, subtab3 = st.tabs(["Patient Master", "Anomalies", "Clean Vitals"])
    
    with subtab1:
        patient_master = Path("silver/patient_master.csv")
        if patient_master.exists():
            df = pd.read_csv(patient_master)
            
            # Column selector
            all_cols = df.columns.tolist()
            selected_cols = st.multiselect("Select columns to display", all_cols, default=all_cols[:7])
            
            if selected_cols:
                st.dataframe(df[selected_cols], use_container_width=True, height=400)
            else:
                st.dataframe(df, use_container_width=True, height=400)
            
            st.metric("Total Patients", len(df))
        else:
            st.info("Run the pipeline to generate patient master data")
    
    with subtab2:
        anomalies = Path("gold/anomalies.csv")
        if anomalies.exists():
            df = pd.read_csv(anomalies)
            
            # Anomaly type filter
            anomaly_types = ['All'] + df['anomaly'].unique().tolist()
            selected_anomaly = st.selectbox("Filter by Anomaly Type", anomaly_types)
            
            if selected_anomaly != 'All':
                df = df[df['anomaly'] == selected_anomaly]
            
            st.dataframe(df, use_container_width=True, height=400)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Anomalies", len(df))
            with col2:
                if len(df) > 0:
                    st.metric("Unique Patients", df['patient_id'].nunique())
        else:
            st.info("Run the pipeline to detect anomalies")
    
    with subtab3:
        clean_vitals = Path("silver/clean_vitals.csv")
        if clean_vitals.exists():
            df = pd.read_csv(clean_vitals)
            
            # Patient filter
            patient_ids = ['All'] + sorted(df['patient_id'].unique().tolist())
            selected_patient = st.selectbox("Filter by Patient ID ", patient_ids, key="vitals_patient")
            
            if selected_patient != 'All':
                df = df[df['patient_id'] == selected_patient]
            
            st.dataframe(df, use_container_width=True, height=400)
            st.metric("Total Records", len(df))
        else:
            st.info("Run the pipeline to generate clean vitals data")

with tab4:
    st.header("📈 Exploratory Data Analysis")
    
    if Path("bronze/ehr.csv").exists():
        subtab1, subtab2, subtab3 = st.tabs(["EHR Analysis", "Vitals Analysis", "Labs Analysis"])
        
        with subtab1:
            st.subheader("EHR Dataset Statistics")
            ehr = pd.read_csv('bronze/ehr.csv')
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Patients", len(ehr))
            with col2:
                st.metric("Avg Age", f"{ehr['age'].mean():.1f}")
            with col3:
                st.metric("Age Range", f"{ehr['age'].min()}-{ehr['age'].max()}")
            with col4:
                st.metric("Missing Values", ehr.isnull().sum().sum())
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Gender Distribution**")
                st.bar_chart(ehr['gender'].value_counts())
            with col2:
                st.write("**Age Distribution**")
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.hist(ehr['age'], bins=20, edgecolor='black')
                ax.set_xlabel('Age')
                ax.set_ylabel('Frequency')
                st.pyplot(fig)
        
        with subtab2:
            st.subheader("Vitals Dataset Statistics")
            vitals = pd.read_csv('bronze/vitals.csv')
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", len(vitals))
            with col2:
                st.metric("Unique Patients", vitals['patientId'].nunique())
            with col3:
                st.metric("Avg HR", f"{vitals['hr'].mean():.1f}")
            with col4:
                st.metric("Avg Oxygen", f"{vitals['ox'].mean():.1f}%")
            
            st.write("**Vitals Statistics**")
            st.dataframe(vitals[['hr', 'ox', 'sys', 'dia']].describe())
            
            st.write("**Outlier Detection (IQR Method)**")
            outlier_data = []
            for col in ['hr', 'ox', 'sys', 'dia']:
                Q1 = vitals[col].quantile(0.25)
                Q3 = vitals[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((vitals[col] < (Q1 - 1.5 * IQR)) | (vitals[col] > (Q3 + 1.5 * IQR))).sum()
                outlier_data.append({"Vital": col.upper(), "Outliers": outliers, "Percentage": f"{(outliers/len(vitals)*100):.2f}%"})
            st.table(pd.DataFrame(outlier_data))
        
        with subtab3:
            st.subheader("Labs Dataset Statistics")
            labs = pd.read_csv('bronze/labs.csv')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(labs))
            with col2:
                st.metric("Unique Patients", labs['patient_id'].nunique())
            with col3:
                st.metric("Test Types", labs['test'].nunique())
            
            st.write("**Lab Test Distribution**")
            st.bar_chart(labs['test'].value_counts())
            
            st.write("**Records per Patient**")
            records_per_patient = labs['patient_id'].value_counts().describe()
            st.write(f"Mean: {records_per_patient['mean']:.1f}, Min: {records_per_patient['min']:.0f}, Max: {records_per_patient['max']:.0f}")
    else:
        st.info("Run the pipeline to view EDA")
