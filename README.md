# 🏭 AI-Powered ERP Quality Module

**An intelligent manufacturing quality management system powered by AI and machine learning**

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Overview

AI-ERP Quality Module is a comprehensive manufacturing quality management system that leverages artificial intelligence and machine learning to provide:

- **Predictive Quality Analysis** - XGBoost-based defect prediction with SHAP explainability
- **Predictive Maintenance** - Random Forest RUL (Remaining Useful Life) estimation
- **Supplier Risk Scoring** - K-Means clustering and IsolationForest for supplier evaluation
- **Computer Vision Inspection** - OpenCV-based visual defect detection
- **Real-time KPI Monitoring** - OEE, FPY, DPMO, Cpk tracking with SQLite backend

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI-ERP Quality Module                     │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌─────▼─────┐       ┌────▼────┐
   │ FastAPI │         │ Streamlit │       │ SQLite  │
   │   API   │         │ Dashboard │       │   DB    │
   └────┬────┘         └─────┬─────┘       └────┬────┘
        │                    │                   │
        └────────────────────┼───────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
   ┌────▼────┐                              ┌────▼────┐
   │  Quality│                              │Reporting│
   │  Module │                              │ Module  │
   └─────────┘                              └─────────┘
   ┌─────────┐                              ┌─────────┐
   │Maintenance                             │ Vision  │
   │  Module │                              │ Module  │
   └─────────┘                              └─────────┘
   ┌─────────┐
   │Supplier │
   │ Module  │
   └─────────┘
```

## 🚀 Features

### 1. 🔮 Quality Prediction Module
- **XGBoost Classifier** for defect probability prediction
- **SHAP Integration** for model explainability
- **SPC (Statistical Process Control)** monitoring with control charts
- Real-time sensor data analysis (8 parameters)
- Risk level classification (LOW, MEDIUM, HIGH, CRITICAL)
- Actionable recommendations based on predictions

### 2. 🔧 Predictive Maintenance Module
- **Random Forest Regressor** for RUL estimation
- Real-time monitoring of **8 machines** (M001-M008)
- Sensor health assessment
- Maintenance urgency classification (NORMAL, WARNING, CRITICAL)
- Historical trend analysis
- Fleet-wide health summary

### 3. 🚚 Supplier Management Module
- **Weighted scoring system** (Quality 30%, Delivery 25%, Defects 20%, Price 15%, Response 10%)
- Risk-based classification (LOW, MEDIUM, HIGH, CRITICAL)
- Supplier categorization (PREFERRED, APPROVED, CONDITIONAL, DISQUALIFIED)
- **Procurement Advisory System** with confidence scoring
- Multi-supplier comparison and ranking
- Anomaly detection using IsolationForest

### 4. 👁️ Computer Vision Module
- **OpenCV-based** visual inspection
- Edge detection and contour analysis
- Brightness/contrast evaluation
- Defect region mapping with coordinates
- **Anomaly detection** using multiple algorithms:
  - Brightness anomaly detection
  - Noise and blur analysis
  - Texture uniformity assessment
  - Histogram distribution analysis

### 5. 📊 Reporting & KPI Module
- **OEE (Overall Equipment Effectiveness)** calculation
- **FPY (First Pass Yield)** monitoring
- **DPMO (Defects Per Million Opportunities)** tracking
- **Cpk (Process Capability Index)** analysis
- Historical trend visualization (7, 14, 30, 60, 90 days)
- Machine-specific KPI reports
- **SQLite-based Alert System** with severity levels (INFO, WARNING, ERROR, CRITICAL)

## 📦 Technology Stack

### Backend
- **FastAPI** - Modern async web framework
- **Python 3.9+** - Core language
- **scikit-learn** - Machine learning algorithms
- **XGBoost** - Gradient boosting for classification
- **SHAP** - Model explainability
- **OpenCV** - Computer vision processing
- **SQLite** - Lightweight database

### Frontend
- **Streamlit** - Interactive dashboard framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing

### ML Models
- **XGBoost Classifier** - Quality prediction
- **Random Forest Regressor** - RUL estimation
- **K-Means Clustering** - Supplier segmentation
- **IsolationForest** - Anomaly detection

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Uvicorn** - ASGI server

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- Docker & Docker Compose (optional)
- Git

### Method 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/altayyeles/ai-erp-quality-module.git
cd ai-erp-quality-module

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data models

# Copy environment configuration
cp .env.example .env
```

### Method 2: Docker Installation

```bash
# Clone the repository
git clone https://github.com/altayyeles/ai-erp-quality-module.git
cd ai-erp-quality-module

# Build and run with Docker Compose
docker-compose up --build
```

## 🚀 Usage

### Starting the API Server

```bash
# Local
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Docker
docker-compose up api
```

API will be available at: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Starting the Dashboard

```bash
# Local
streamlit run dashboard/app.py

# Docker
docker-compose up dashboard
```

Dashboard will be available at: `http://localhost:8501`

## 📡 API Endpoints

### Quality Endpoints
```bash
# Predict defect probability
POST /api/v1/quality/predict
{
  "air_temperature": 298.0,
  "process_temperature": 308.0,
  "rotational_speed": 1500.0,
  "torque": 40.0,
  "tool_wear": 100.0,
  "vibration": 0.5,
  "humidity": 60.0,
  "pressure": 1.0
}

# Get SPC status
GET /api/v1/quality/spc-status
```

### Maintenance Endpoints
```bash
# Predict RUL
POST /api/v1/maintenance/predict-rul
{
  "machine_id": "M001",
  "air_temperature": 298.0,
  ...
}

# Get all machines status
GET /api/v1/maintenance/machines

# Get specific machine status
GET /api/v1/maintenance/machines/M001
```

### Supplier Endpoints
```bash
# Score supplier
POST /api/v1/suppliers/score
{
  "supplier_id": "SUP-001",
  "on_time_delivery_rate": 0.90,
  "quality_score": 0.85,
  "price_competitiveness": 0.75,
  "defect_rate": 0.03,
  "response_time_days": 2.0,
  "years_of_partnership": 3.0
}

# Get procurement advice
POST /api/v1/suppliers/advise
```

### Vision Endpoints
```bash
# Visual inspection
POST /api/v1/vision/inspect
Content-Type: multipart/form-data
file: [image file]

# Anomaly detection
POST /api/v1/vision/detect-anomaly
Content-Type: multipart/form-data
file: [image file]
```

### Dashboard Endpoints
```bash
# Get KPIs
GET /api/v1/dashboard/kpis

# Get active alerts
GET /api/v1/dashboard/alerts

# Dismiss alert
DELETE /api/v1/dashboard/alerts/{alert_id}
```

## 📊 Dashboard Pages

### 1. Home (Main Page)
- Overview of all modules
- Key metrics at a glance
- Quick navigation

### 2. 🔮 Quality Prediction
- Sensor input form
- Real-time defect prediction
- SHAP feature importance visualization
- SPC control charts
- Risk-based recommendations

### 3. 🔧 Predictive Maintenance
- Fleet overview with 8 machines
- Machine status cards with color coding
- Detailed sensor readings
- RUL prediction and trends
- Maintenance scheduling

### 4. 🚚 Supplier Scoring
- Supplier metrics input form
- Weighted performance scoring
- Risk level assessment
- Procurement recommendations
- Multi-supplier comparison

### 5. 👁️ Visual Inspection
- Image upload interface
- Visual defect detection
- Anomaly detection analysis
- Quality score calculation
- Defect region mapping

### 6. 📊 KPI Reports & Alerts
- Real-time KPI monitoring (OEE, FPY, DPMO, Cpk)
- Historical trend visualization
- Alert management system
- Machine-specific KPI reports
- Production summary

## 🧪 Example Usage

### Python API Client Example

```python
import requests

# Quality prediction
response = requests.post(
    "http://localhost:8000/api/v1/quality/predict",
    json={
        "air_temperature": 298.0,
        "process_temperature": 310.0,
        "rotational_speed": 1450.0,
        "torque": 45.0,
        "tool_wear": 150.0,
        "vibration": 0.7,
        "humidity": 65.0,
        "pressure": 1.02
    }
)

print(response.json())
```

### cURL Example

```bash
# Quality prediction
curl -X POST "http://localhost:8000/api/v1/quality/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "air_temperature": 298.0,
    "process_temperature": 308.0,
    "rotational_speed": 1500.0,
    "torque": 40.0,
    "tool_wear": 100.0,
    "vibration": 0.5,
    "humidity": 60.0,
    "pressure": 1.0
  }'

# Get machine status
curl -X GET "http://localhost:8000/api/v1/maintenance/machines/M001"

# Get KPIs
curl -X GET "http://localhost:8000/api/v1/dashboard/kpis"
```

## 🗂️ Project Structure

```
ai-erp-quality-module/
├── api/                          # FastAPI application
│   ├── main.py                   # API entry point
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       ├── quality.py            # Quality endpoints
│       ├── maintenance.py        # Maintenance endpoints
│       ├── supplier.py           # Supplier endpoints
│       ├── vision.py             # Vision endpoints
│       └── dashboard.py          # Dashboard endpoints
├── modules/                      # Core business logic
│   ├── __init__.py
│   ├── quality/
│   │   ├── __init__.py
│   │   ├── predictive_model.py  # XGBoost quality model
│   │   └── spc_analysis.py      # SPC monitoring
│   ├── maintenance/
│   │   ├── __init__.py
│   │   ├── rul_model.py         # Random Forest RUL model
│   │   └── sensor_monitor.py   # Real-time monitoring
│   ├── supplier/
│   │   ├── __init__.py
│   │   ├── supplier_score.py    # Scoring system
│   │   └── procurement_advisor.py # Advisory system
│   ├── vision/
│   │   ├── __init__.py
│   │   ├── visual_inspection.py # OpenCV inspection
│   │   └── anomaly_detector.py  # Anomaly detection
│   └── reporting/
│       ├── __init__.py
│       ├── kpi_engine.py        # KPI calculations
│       └── alert_system.py      # Alert management
├── dashboard/                    # Streamlit dashboard
│   ├── app.py                   # Main dashboard page
│   └── pages/
│       ├── 1_Quality_Prediction.py
│       ├── 2_Maintenance.py
│       ├── 3_Supplier.py
│       ├── 4_Vision.py
│       └── 5_Reports.py
├── data/                        # Data storage
│   ├── README.md
│   ├── download_datasets.py
│   ├── kpi_metrics.db          # KPI database
│   └── alerts.db               # Alerts database
├── models/                      # Trained ML models
├── Dockerfile                   # Docker configuration
├── docker-compose.yml          # Docker Compose config
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── setup.py                    # Package setup
├── .env.example               # Environment variables template
├── .gitignore
└── README.md                  # This file
```

## 🔒 Security Features

- Input validation using Pydantic models
- SQL injection prevention with parameterized queries
- CORS middleware for API security
- Environment-based configuration
- Graceful error handling with fallback modes

## 🤝 Contributing

This project is part of the **LED Yazılım Staj Projesi** (LED Software Internship Project).

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Developer

**LED Yazılım Staj Projesi**
- AI-Powered ERP Quality Module
- Manufacturing Intelligence System
- Version 1.0.0

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Streamlit for the intuitive dashboard framework
- scikit-learn, XGBoost, and SHAP for ML capabilities
- OpenCV for computer vision processing
- The entire Python data science ecosystem

## 📞 Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

---

**Built with ❤️ for the manufacturing industry**
