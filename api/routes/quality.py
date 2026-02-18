"""
Quality Module API Routes
Endpoints for predictive quality analysis and SPC
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class SensorReadings(BaseModel):
    air_temperature: float = 298.0
    process_temperature: float = 308.0
    rotational_speed: float = 1500.0
    torque: float = 40.0
    tool_wear: float = 100.0
    vibration: float = 0.5
    humidity: float = 60.0
    pressure: float = 1.0


@router.post("/predict")
async def predict_quality(readings: SensorReadings):
    """Predict defect probability based on sensor readings."""
    try:
        from modules.quality.predictive_model import QualityPredictiveModel, create_demo_model
        
        # Create or load model
        model = create_demo_model()
        
        # Make prediction
        result = model.predict_defect_probability(readings.dict())
        
        return {
            "status": "success",
            "data": {
                "defect_probability": result.defect_probability,
                "is_defect_predicted": result.is_defect_predicted,
                "risk_level": result.risk_level,
                "feature_contributions": result.feature_contributions,
                "recommendations": result.recommendations
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/spc")
async def spc_analysis(readings: SensorReadings):
    """Perform Statistical Process Control analysis."""
    try:
        from modules.quality.spc_analysis import SPCAnalyzer
        import pandas as pd
        
        # Convert to DataFrame for SPC analysis
        analyzer = SPCAnalyzer()
        
        # For demo purposes, create a small dataset with current reading
        data = pd.DataFrame([readings.dict()])
        
        return {
            "status": "success",
            "message": "SPC analysis endpoint - integrate with SPCAnalyzer as needed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
