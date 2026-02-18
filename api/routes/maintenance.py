"""
Maintenance Module API Routes
Endpoints for predictive maintenance and RUL estimation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class MachineData(BaseModel):
    air_temperature: float = 298.0
    process_temperature: float = 308.0
    rotational_speed: float = 1500.0
    torque: float = 40.0
    tool_wear: float = 100.0
    vibration: float = 0.5
    humidity: float = 60.0
    pressure: float = 1.0


@router.post("/predict-rul")
async def predict_rul(machine_data: MachineData):
    """Predict Remaining Useful Life (RUL) for a machine."""
    try:
        from modules.maintenance.rul_model import RULModel
        
        model = RULModel()
        result = model.predict(machine_data.dict())
        
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/machines")
async def get_all_machines():
    """Get status of all machines."""
    try:
        from modules.maintenance.sensor_monitor import SensorMonitor
        
        monitor = SensorMonitor()
        machines = monitor.get_all_machines()
        
        return {"status": "success", "data": machines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/machines/{machine_id}")
async def get_machine_status(machine_id: str):
    """Get detailed status of a specific machine."""
    try:
        from modules.maintenance.sensor_monitor import SensorMonitor
        
        monitor = SensorMonitor()
        status = monitor.get_machine_status(machine_id)
        
        return {"status": "success", "data": status}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
