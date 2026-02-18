"""
Supplier Module API Routes
Endpoints for supplier risk scoring and procurement advisory
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class SupplierData(BaseModel):
    supplier_id: Optional[str] = 'SUP-001'
    on_time_delivery_rate: float = 0.90
    quality_score: float = 0.85
    price_competitiveness: float = 0.75
    defect_rate: float = 0.03
    response_time_days: float = 2.0
    years_of_partnership: float = 3.0


@router.post("/score")
async def score_supplier(supplier: SupplierData):
    """Score a supplier based on performance metrics."""
    try:
        from modules.supplier.supplier_score import SupplierScorer
        scorer = SupplierScorer()
        result = scorer.score(supplier.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advise")
async def procurement_advice(supplier: SupplierData):
    """Get procurement advisory for a supplier."""
    try:
        from modules.supplier.procurement_advisor import ProcurementAdvisor
        advisor = ProcurementAdvisor()
        result = advisor.advise(supplier.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
