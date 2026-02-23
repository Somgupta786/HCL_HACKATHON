"""Visualization generation."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100


def plot_hr_trend():
    """Generate heart rate trend - combined multi-line plot (Time vs HR per patient)."""
    df = pd.read_csv('silver/clean_vitals.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Get top 10 patients with most readings for better visualization
    top_patients = df['patient_id'].value_counts().head(10).index
    df_filtered = df[df['patient_id'].isin(top_patients)]
    
    plt.figure(figsize=(14, 7))
    for patient_id in top_patients:
        patient_data = df_filtered[df_filtered['patient_id'] == patient_id].sort_values('timestamp')
        plt.plot(patient_data['timestamp'], patient_data['hr'], marker='o', markersize=4, 
                linewidth=1.5, label=f'Patient {patient_id}', alpha=0.7)
    
    plt.xlabel('Timestamp', fontsize=12)
    plt.ylabel('Heart Rate (bpm)', fontsize=12)
    plt.title('Heart Rate Trends (Per Patient)', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('visualizations/hr_trend.png', bbox_inches='tight', dpi=150)
    plt.close()


def plot_oxygen_distribution():
    """Generate oxygen level distribution - histogram and boxplot with low oxygen highlight."""
    df = pd.read_csv('silver/clean_vitals.csv')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Histogram
    ax1.hist(df['ox'].dropna(), bins=30, edgecolor='black', alpha=0.7, color='skyblue')
    ax1.axvline(x=92, color='red', linestyle='--', linewidth=2.5, label='Low Oxygen Threshold (92%)')
    
    # Highlight low oxygen readings
    low_ox = df[df['ox'] < 92]['ox']
    if len(low_ox) > 0:
        ax1.hist(low_ox, bins=30, edgecolor='black', alpha=0.9, color='red', label=f'Low Oxygen (n={len(low_ox)})')
    
    ax1.set_xlabel('Oxygen Level (%)', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('Oxygen Level Distribution (Histogram)', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Boxplot
    bp = ax2.boxplot(df['ox'].dropna(), patch_artist=True, widths=0.5)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][0].set_edgecolor('black')
    bp['medians'][0].set_color('red')
    bp['medians'][0].set_linewidth(2)
    
    # Add horizontal line at 92
    ax2.axhline(y=92, color='red', linestyle='--', linewidth=2, label='Low Oxygen Threshold (92%)')
    
    ax2.set_ylabel('Oxygen Level (%)', fontsize=12)
    ax2.set_title('Oxygen Level Distribution (Boxplot)', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('visualizations/oxygen_distribution.png', bbox_inches='tight', dpi=150)
    plt.close()


def plot_anomaly_counts():
    """Generate anomaly counts bar chart - Anomaly Type vs Number of Occurrences."""
    df = pd.read_csv('gold/anomalies.csv')
    
    anomaly_counts = df['anomaly'].value_counts()
    
    plt.figure(figsize=(10, 6))
    colors = ['#ff6b6b', '#feca57', '#48dbfb']
    bars = plt.bar(range(len(anomaly_counts)), anomaly_counts.values, 
                   color=colors[:len(anomaly_counts)], edgecolor='black', linewidth=1.5)
    
    plt.xticks(range(len(anomaly_counts)), anomaly_counts.index, rotation=15, ha='right')
    plt.xlabel('Anomaly Type', fontsize=12)
    plt.ylabel('Number of Occurrences', fontsize=12)
    plt.title('Anomaly Counts', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('visualizations/anomaly_counts.png', bbox_inches='tight', dpi=150)
    plt.close()


def run_visualizations():
    """Generate all visualizations."""
    plot_hr_trend()
    plot_oxygen_distribution()
    plot_anomaly_counts()
