"""
AI-Powered ERP Quality Module - FastAPI Application
Main entry point for the REST API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn

from api.routes import quality, maintenance, supplier, vision, dashboard

app = FastAPI(
    title="AI-Powered ERP Quality Module API",
    description="""
    ## AI Destekli ERP Kalite Modülü REST API

    Bu API, üretim süreçlerinde yapay zeka destekli kalite yönetimi sağlar.

    ### Modüller:
    - **Quality**: Öngörücü kalite tahmini (XGBoost + SHAP)
    - **Maintenance**: Öngörücü bakım (Random Forest + RUL)
    - **Supplier**: Tedarikçi risk skorlaması (K-Means + IsolationForest)
    - **Vision**: Computer Vision ile görsel denetim
    - **Dashboard**: Gerçek zamanlı özet veriler

    ### Geliştirici: LED Yazılım Staj Projesi
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quality.router,     prefix="/api/v1/quality",     tags=["Quality"])
app.include_router(maintenance.router, prefix="/api/v1/maintenance",  tags=["Maintenance"])
app.include_router(supplier.router,    prefix="/api/v1/suppliers",    tags=["Supplier"])
app.include_router(vision.router,      prefix="/api/v1/vision",       tags=["Vision"])
app.include_router(dashboard.router,   prefix="/api/v1/dashboard",    tags=["Dashboard"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AI-Powered ERP Quality Module API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "quality": "operational",
            "maintenance": "operational",
            "supplier": "operational",
            "vision": "operational",
            "dashboard": "operational"
        }
    })


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)