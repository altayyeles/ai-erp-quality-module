"""
Vision Module API Routes
Endpoints for visual inspection and anomaly detection
"""

from fastapi import APIRouter, HTTPException, UploadFile, File

router = APIRouter()


@router.post("/inspect")
async def visual_inspect(file: UploadFile = File(...)):
    """Perform visual inspection on an uploaded image."""
    try:
        from modules.vision.visual_inspection import VisualInspector
        inspector = VisualInspector()
        contents = await file.read()
        result = inspector.inspect_bytes(contents)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-anomaly")
async def detect_anomaly(file: UploadFile = File(...)):
    """Detect visual anomalies in an uploaded image."""
    try:
        from modules.vision.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector()
        contents = await file.read()
        result = detector.detect_bytes(contents)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
