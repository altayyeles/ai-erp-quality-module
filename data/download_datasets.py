#!/usr/bin/env python3
"""
Dataset Downloader for AI ERP Quality Module
Downloads and generates all required datasets for the project.
"""

import os
import logging
import urllib.request
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"

# Ensure directories exist
RAW_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)


def download_ai4i_dataset():
    """Download AI4I 2020 Predictive Maintenance Dataset from UCI."""
    logger.info("Downloading AI4I 2020 Predictive Maintenance Dataset...")
    
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
    output_path = RAW_DIR / "ai4i2020.csv"
    
    try:
        urllib.request.urlretrieve(url, output_path)
        logger.info(f"✓ AI4I 2020 dataset downloaded successfully to {output_path}")
        
        # Load and inspect
        df = pd.read_csv(output_path)
        logger.info(f"  Dataset shape: {df.shape}")
        logger.info(f"  Columns: {list(df.columns)}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to download AI4I dataset: {e}")
        logger.info("  Continuing with synthetic data generation...")
        return False


def generate_synthetic_production_data(n_samples=10000):
    """Generate realistic synthetic production quality data."""
    logger.info(f"Generating synthetic production quality data ({n_samples} samples)...")
    
    np.random.seed(42)
    
    # Generate base features
    data = {
        'timestamp': pd.date_range(start='2023-01-01', periods=n_samples, freq='5min'),
        'machine_id': np.random.choice(['M001', 'M002', 'M003', 'M004', 'M005'], n_samples),
        'product_type': np.random.choice(['L', 'M', 'H'], n_samples, p=[0.5, 0.3, 0.2]),
        'air_temperature': np.random.normal(298, 2, n_samples),  # Kelvin
        'process_temperature': np.random.normal(308, 1.5, n_samples),  # Kelvin
        'rotational_speed': np.random.normal(1500, 200, n_samples),  # rpm
        'torque': np.random.normal(40, 10, n_samples),  # Nm
        'tool_wear': np.random.uniform(0, 250, n_samples),  # minutes
        'vibration': np.random.normal(0.5, 0.15, n_samples),  # mm/s
        'humidity': np.random.normal(60, 10, n_samples),  # %
        'pressure': np.random.normal(1.0, 0.1, n_samples),  # bar
    }
    
    df = pd.DataFrame(data)
    
    # Generate failure labels based on realistic conditions
    failure_conditions = (
        (df['tool_wear'] > 200) |
        (df['process_temperature'] > 310) |
        (df['torque'] > 60) |
        (df['rotational_speed'] < 1200) |
        (df['vibration'] > 0.8)
    )
    
    # Add some randomness to failures
    df['machine_failure'] = failure_conditions.astype(int)
    df.loc[np.random.choice(df.index, int(n_samples * 0.02), replace=False), 'machine_failure'] = 1
    df.loc[df['machine_failure'] == 1, 'machine_failure'] = np.where(
        np.random.random(df[df['machine_failure'] == 1].shape[0]) > 0.1,
        1, 0
    )
    
    # Add failure types
    failure_types = []
    for idx, row in df.iterrows():
        if row['machine_failure'] == 1:
            if row['tool_wear'] > 200:
                failure_types.append('Tool Wear Failure')
            elif row['process_temperature'] > 310:
                failure_types.append('Heat Dissipation Failure')
            elif row['torque'] > 60 or row['rotational_speed'] < 1200:
                failure_types.append('Power Failure')
            elif row['vibration'] > 0.8:
                failure_types.append('Overstrain Failure')
            else:
                failure_types.append('Random Failures')
        else:
            failure_types.append('No Failure')
    
    df['failure_type'] = failure_types
    
    # Save
    output_path = RAW_DIR / "synthetic_production_data.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"✓ Synthetic production data generated: {output_path}")
    logger.info(f"  Shape: {df.shape}")
    logger.info(f"  Failure rate: {df['machine_failure'].mean():.2%}")
    
    return df


def generate_synthetic_supplier_data(n_suppliers=50):
    """Generate realistic synthetic supplier performance data."""
    logger.info(f"Generating synthetic supplier data ({n_suppliers} suppliers)...")
    
    np.random.seed(42)
    
    # Generate supplier base data
    suppliers = []
    for i in range(n_suppliers):
        supplier_id = f"SUP{i+1:03d}"
        supplier_name = f"Supplier_{i+1}"
        
        # Base quality score (some suppliers are better than others)
        base_quality = np.random.beta(8, 2)  # Skewed towards high quality
        
        # Generate 12 months of data
        months_data = []
        for month in range(12):
            date = datetime(2023, 1, 1) + timedelta(days=30 * month)
            
            # Monthly metrics with some variation
            quality_score = np.clip(base_quality + np.random.normal(0, 0.05), 0, 1) * 100
            on_time_delivery = np.clip(np.random.beta(9, 1), 0, 1) * 100
            defect_rate = np.random.exponential(0.5)  # PPM
            lead_time_days = np.random.gamma(5, 2)
            price_competitiveness = np.random.beta(5, 5) * 100
            response_time_hours = np.random.gamma(2, 12)
            
            months_data.append({
                'supplier_id': supplier_id,
                'supplier_name': supplier_name,
                'date': date,
                'quality_score': quality_score,
                'on_time_delivery': on_time_delivery,
                'defect_rate_ppm': defect_rate,
                'lead_time_days': lead_time_days,
                'price_competitiveness': price_competitiveness,
                'response_time_hours': response_time_hours,
                'total_orders': np.random.randint(10, 100),
                'total_value': np.random.uniform(50000, 500000)
            })
        
        suppliers.extend(months_data)
    
    df = pd.DataFrame(suppliers)
    
    # Save
    output_path = RAW_DIR / "synthetic_supplier_data.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"✓ Synthetic supplier data generated: {output_path}")
    logger.info(f"  Shape: {df.shape}")
    logger.info(f"  Unique suppliers: {df['supplier_id'].nunique()}")
    
    return df


def generate_synthetic_steel_faults_data(n_samples=2000):
    """Generate synthetic steel plates fault data."""
    logger.info(f"Generating synthetic steel faults data ({n_samples} samples)...")
    
    np.random.seed(42)
    
    fault_types = ['Pastry', 'Z_Scratch', 'K_Scatch', 'Stains', 'Dirtiness', 'Bumps', 'Other_Faults']
    
    data = {
        'X_Minimum': np.random.uniform(0, 200, n_samples),
        'X_Maximum': np.random.uniform(200, 400, n_samples),
        'Y_Minimum': np.random.uniform(0, 150, n_samples),
        'Y_Maximum': np.random.uniform(150, 300, n_samples),
        'Pixels_Areas': np.random.randint(1000, 50000, n_samples),
        'X_Perimeter': np.random.uniform(50, 500, n_samples),
        'Y_Perimeter': np.random.uniform(50, 400, n_samples),
        'Sum_of_Luminosity': np.random.randint(50000, 500000, n_samples),
        'Minimum_of_Luminosity': np.random.randint(0, 100, n_samples),
        'Maximum_of_Luminosity': np.random.randint(150, 255, n_samples),
        'Length_of_Conveyer': np.random.uniform(1000, 2000, n_samples),
        'TypeOfSteel_A300': np.random.choice([0, 1], n_samples),
        'TypeOfSteel_A400': np.random.choice([0, 1], n_samples),
        'Steel_Plate_Thickness': np.random.uniform(40, 150, n_samples),
        'Edges_Index': np.random.uniform(0, 1, n_samples),
        'Empty_Index': np.random.uniform(0, 1, n_samples),
        'Square_Index': np.random.uniform(0, 1, n_samples),
        'Outside_X_Index': np.random.uniform(0, 1, n_samples),
        'Edges_X_Index': np.random.uniform(0, 1, n_samples),
        'Edges_Y_Index': np.random.uniform(0, 1, n_samples),
        'Outside_Global_Index': np.random.uniform(0, 1, n_samples),
        'Fault_Type': np.random.choice(fault_types, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Save
    output_path = RAW_DIR / "synthetic_steel_faults.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"✓ Synthetic steel faults data generated: {output_path}")
    logger.info(f"  Shape: {df.shape}")
    
    return df


def main():
    """Main function to download and generate all datasets."""
    logger.info("=" * 60)
    logger.info("AI ERP Quality Module - Dataset Preparation")
    logger.info("=" * 60)
    
    # 1. Try to download AI4I dataset
    ai4i_success = download_ai4i_dataset()
    
    # 2. Generate synthetic production data
    generate_synthetic_production_data(n_samples=10000)
    
    # 3. Generate synthetic supplier data
    generate_synthetic_supplier_data(n_suppliers=50)
    
    # 4. Generate synthetic steel faults data
    generate_synthetic_steel_faults_data(n_samples=2000)
    
    logger.info("=" * 60)
    logger.info("✓ All datasets prepared successfully!")
    logger.info(f"  Raw data directory: {RAW_DIR}")
    logger.info(f"  Processed data directory: {PROCESSED_DIR}")
    logger.info("=" * 60)
    
    # List all files
    logger.info("\nGenerated files:")
    for file in sorted(RAW_DIR.glob("*.csv")):
        size_mb = file.stat().st_size / (1024 * 1024)
        logger.info(f"  - {file.name} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
