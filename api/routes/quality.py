"""
Quality Module API Routes
Endpoints for predictive quality analysis and SPC monitoring
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
async def predict_quality(sensors: SensorReadings):
    """Predict defect probability based on sensor readings."""
    try:
        from modules.quality.predictive_model import QualityPredictiveModel
        from pathlib import Path
        
        model_path = Path("models/quality_model.pkl")
        model = QualityPredictiveModel(model_path if model_path.exists() else None)
        
        # If model not loaded, create demo model
        if model.model is None:
            from modules.quality.predictive_model import create_demo_model
            model = create_demo_model()
        
        result = model.predict_defect_probability(sensors.dict())
        
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


@router.get("/spc-status")
async def get_spc_status():
    """Get Statistical Process Control status."""
    try:
        from modules.quality.spc_analysis import SPCAnalyzer
        
        analyzer = SPCAnalyzer()
        # Generate demo data for SPC
        import numpy as np
        demo_data = np.random.normal(100, 5, 30).tolist()
        
        result = analyzer.analyze(demo_data)
        
        return {
            "status": "success",
            "data": {
                "in_control": result.in_control,
                "violations": result.violations,
                "control_limits": {
                    "ucl": result.ucl,
                    "lcl": result.lcl,
                    "center_line": result.center_line
                },
                "statistics": result.statistics
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
