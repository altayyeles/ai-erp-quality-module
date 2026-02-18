"""
Quality Module API Routes
Endpoints for predictive quality analysis and SPC control charts
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class SensorData(BaseModel):
    air_temperature: float = 298.0
    process_temperature: float = 308.0
    rotational_speed: float = 1500.0
    torque: float = 40.0
    tool_wear: float = 100.0
    vibration: float = 0.5
    humidity: float = 60.0
    pressure: float = 1.0


@router.post("/predict")
async def predict_quality(sensor_data: SensorData):
    """Predict defect probability based on sensor readings."""
    try:
        from modules.quality.predictive_model import QualityPredictiveModel, create_demo_model
        from pathlib import Path
        
        model_path = Path("models/quality_model.pkl")
        
        # Try to load existing model or create demo model
        try:
            if model_path.exists():
                model = QualityPredictiveModel(model_path=model_path)
            else:
                model = create_demo_model()
                model_path.parent.mkdir(parents=True, exist_ok=True)
                model.save_model(model_path)
        except Exception as e:
            # Fallback to demo model if loading fails
            model = create_demo_model()
        
        result = model.predict_defect_probability(sensor_data.dict())
        
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


@router.get("/feature-importance")
async def get_feature_importance():
    """Get feature importance from the trained model."""
    try:
        from modules.quality.predictive_model import QualityPredictiveModel, create_demo_model
        from pathlib import Path
        
        model_path = Path("models/quality_model.pkl")
        
        try:
            if model_path.exists():
                model = QualityPredictiveModel(model_path=model_path)
            else:
                model = create_demo_model()
        except Exception:
            model = create_demo_model()
        
        importance = model.get_feature_importance()
        
        return {"status": "success", "data": importance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spc-analysis")
async def spc_analysis():
    """Get SPC control chart analysis with demo data."""
    try:
        from modules.quality.spc_analysis import SPCAnalyzer
        import pandas as pd
        import numpy as np
        
        # Generate demo data for SPC analysis
        np.random.seed(42)
        data = pd.Series(np.random.normal(100, 5, 100))
        
        analyzer = SPCAnalyzer()
        result = analyzer.analyze_xbar(data, subgroup_size=5, usl=115, lsl=85)
        
        return {
            "status": "success",
            "data": {
                "chart_type": result.chart_type,
                "center_line": result.center_line,
                "ucl": result.ucl,
                "lcl": result.lcl,
                "usl": result.usl,
                "lsl": result.lsl,
                "out_of_control_points": result.out_of_control_points,
                "violations": [(idx, viol) for idx, viol in result.violations],
                "process_capability": result.process_capability
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
