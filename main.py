"""Main pipeline orchestration."""
from src.utils import create_folders
from src.bronze import run_bronze
from src.silver import run_silver
from src.gold import run_gold
from src.visualize import run_visualizations


def main():
    """Execute the complete data pipeline."""
    print("[SETUP] Creating folders...")
    create_folders()
    
    print("[BRONZE] Raw data ingested")
    run_bronze()
    
    print("[SILVER] Data cleaned")
    run_silver()
    
    print("[GOLD] Anomalies generated")
    run_gold()
    
    print("[VISUALIZATION] Plots saved")
    run_visualizations()
    
    print("\n[SUCCESS] Pipeline completed successfully!")


if __name__ == "__main__":
    main()
