# Configuration for Patient Health Monitoring System

# Anomaly Detection Thresholds
HR_THRESHOLD_HIGH = 120
OX_THRESHOLD_LOW = 92
BP_SYS_THRESHOLD_HIGH = 160
BP_DIA_THRESHOLD_HIGH = 100

# File Paths
BRONZE_DIR = "bronze"
SILVER_DIR = "silver"
GOLD_DIR = "gold"
VISUALIZATIONS_DIR = "visualizations"

# Visualization Settings
VISUALIZATION_DPI = 300
VISUALIZATION_WIDTH = 12
VISUALIZATION_HEIGHT = 6

# Helper Functions
def get_anomaly_color(anomaly_type):
    colors = {
        "High HR": "red",
        "Low Oxygen": "orange",
        "High BP": "darkred"
    }
    return colors.get(anomaly_type, "gray")

def get_risk_level(anomaly_count):
    if anomaly_count == 0:
        return "Low Risk"
    elif anomaly_count <= 2:
        return "Medium Risk"
    else:
        return "High Risk"

def validate_vitals_range(value, vital_type):
    ranges = {
        "hr": (40, 150),
        "ox": (70, 100),
        "sys": (80, 200),
        "dia": (40, 130)
    }
    min_val, max_val = ranges.get(vital_type, (0, 1000))
    return min_val <= value <= max_val
