# 🏭 AI-Powered ERP Quality Module

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Proje Açıklaması / Project Description

### 🇹🇷 Türkçe

AI-Powered ERP Quality Module, üretim süreçlerinde yapay zeka destekli kalite yönetimi sağlayan kapsamlı bir sistemdir. Makine öğrenimi, bilgisayar görüsü ve istatistiksel süreç kontrolü tekniklerini kullanarak üretim kalitesini optimize eder.

**Temel Özellikler:**
- 🔮 **Öngörücü Kalite Analizi**: XGBoost + SHAP ile hata olasılığı tahmini
- 🔧 **Öngörücü Bakım**: Random Forest ile RUL (Remaining Useful Life) tahmini
- 🚚 **Tedarikçi Risk Skorlaması**: Çok kriterli ağırlıklı skorlama sistemi
- 👁️ **Görsel Denetim**: OpenCV tabanlı hata tespiti ve anomali analizi
- 📊 **Gerçek Zamanlı KPI Dashboard**: OEE, FPY, DPMO, Cpk metrikleri
- 🔔 **Akıllı Uyarı Sistemi**: Öncelikli uyarı yönetimi

### 🇬🇧 English

AI-Powered ERP Quality Module is a comprehensive system for AI-assisted quality management in manufacturing processes. It optimizes production quality using machine learning, computer vision, and statistical process control techniques.

**Key Features:**
- 🔮 **Predictive Quality Analysis**: Defect probability prediction with XGBoost + SHAP
- 🔧 **Predictive Maintenance**: RUL (Remaining Useful Life) prediction with Random Forest
- 🚚 **Supplier Risk Scoring**: Multi-criteria weighted scoring system
- 👁️ **Visual Inspection**: OpenCV-based defect detection and anomaly analysis
- 📊 **Real-Time KPI Dashboard**: OEE, FPY, DPMO, Cpk metrics
- 🔔 **Smart Alert System**: Priority-based alert management

---

## 🚀 Kurulum / Installation

### Gereksinimler / Requirements

- Python 3.10 or higher
- pip package manager
- (Optional) Docker & Docker Compose

### Pip ile Kurulum / Installation with Pip

```bash
# Repository'yi klonlayın / Clone the repository
git clone https://github.com/altayyeles/ai-erp-quality-module.git
cd ai-erp-quality-module

# Sanal ortam oluşturun / Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Bağımlılıkları yükleyin / Install dependencies
pip install -r requirements.txt

# Geliştirme bağımlılıkları (opsiyonel) / Development dependencies (optional)
pip install -r requirements-dev.txt
```

### Docker ile Kurulum / Installation with Docker

```bash
# Docker Compose ile çalıştırın / Run with Docker Compose
docker-compose up -d

# API: http://localhost:8000
# Dashboard: http://localhost:8501
```

---

## 📖 Kullanım / Usage

### FastAPI Backend

```bash
# API sunucusunu başlatın / Start API server
cd api
python main.py

# API Documentation: http://localhost:8000/docs
# Alternative docs: http://localhost:8000/redoc
```

### Streamlit Dashboard

```bash
# Dashboard'u başlatın / Start dashboard
streamlit run dashboard/app.py

# Dashboard: http://localhost:8501
```

---

## 🔌 API Endpoints

### Health & Root
- `GET /` - Root endpoint with API information
- `GET /health` - Health check with module status

### Quality Module (`/api/v1/quality`)
- `POST /predict` - Predict defect probability from sensor readings
- `POST /spc` - Statistical Process Control analysis

### Maintenance Module (`/api/v1/maintenance`)
- `POST /predict-rul` - Predict Remaining Useful Life
- `GET /machines` - Get status of all 8 machines
- `GET /machines/{machine_id}` - Get specific machine status

### Supplier Module (`/api/v1/suppliers`)
- `POST /score` - Calculate supplier risk score
- `POST /advise` - Get procurement recommendations

### Vision Module (`/api/v1/vision`)
- `POST /inspect` - Visual inspection with defect detection
- `POST /detect-anomaly` - Anomaly detection in images

### Dashboard Module (`/api/v1/dashboard`)
- `GET /kpis` - Get current KPI snapshot
- `GET /alerts` - Get active alerts
- `DELETE /alerts/{alert_id}` - Dismiss an alert

---

## 📊 Dashboard Sayfaları / Dashboard Pages

### 1. 🔮 Quality Prediction
- Sensor data input with interactive sliders
- Real-time defect probability prediction
- SHAP feature contribution visualization
- Risk level assessment
- Actionable recommendations

### 2. 🔧 Maintenance
- 8-machine real-time monitoring (M001-M008)
- RUL predictions for each machine
- Maintenance urgency classification
- Sensor readings with gauge visualizations
- Maintenance schedule sorted by urgency

### 3. 🚚 Supplier Scoring
- Supplier performance data input
- Weighted multi-criteria scoring
- Risk level and category assignment
- Procurement action recommendations
- Detailed score breakdown

### 4. 👁️ Vision Inspection
- Image upload for inspection
- OpenCV-based defect detection
- Anomaly detection with multiple methods
- Quality score calculation
- Image quality metrics

### 5. 📊 Reports & KPIs
- Real-time KPI gauges (OEE, FPY, DPMO, Cpk)
- Overall performance summary
- Active alert management
- Alert creation and dismissal
- Alert statistics by severity and source

---

## 🏗️ Proje Yapısı / Project Structure

```
ai-erp-quality-module/
├── api/                          # FastAPI Backend
│   ├── main.py                   # Main application entry
│   ├── __init__.py
│   └── routes/                   # API route modules
│       ├── __init__.py
│       ├── quality.py            # Quality prediction routes
│       ├── maintenance.py        # Maintenance routes
│       ├── supplier.py           # Supplier routes
│       ├── vision.py             # Vision inspection routes
│       └── dashboard.py          # Dashboard routes
│
├── modules/                      # Core business logic
│   ├── __init__.py
│   ├── quality/                  # Quality prediction module
│   │   ├── __init__.py
│   │   ├── predictive_model.py  # XGBoost + SHAP model
│   │   └── spc_analysis.py      # Statistical Process Control
│   ├── maintenance/              # Predictive maintenance
│   │   ├── __init__.py
│   │   ├── rul_model.py         # Random Forest RUL model
│   │   └── sensor_monitor.py    # Machine monitoring
│   ├── supplier/                 # Supplier management
│   │   ├── __init__.py
│   │   ├── supplier_score.py    # Weighted scoring
│   │   └── procurement_advisor.py  # Procurement recommendations
│   ├── vision/                   # Computer vision
│   │   ├── __init__.py
│   │   ├── visual_inspection.py # OpenCV inspection
│   │   └── anomaly_detector.py  # Anomaly detection
│   └── reporting/                # KPI & alerts
│       ├── __init__.py
│       ├── kpi_engine.py        # KPI calculations
│       └── alert_system.py      # Alert management
│
├── dashboard/                    # Streamlit Dashboard
│   ├── app.py                   # Main dashboard page
│   └── pages/                   # Multi-page dashboard
│       ├── 1_Quality_Prediction.py
│       ├── 2_Maintenance.py
│       ├── 3_Supplier.py
│       ├── 4_Vision.py
│       └── 5_Reports.py
│
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── test_quality.py
│   ├── test_maintenance.py
│   ├── test_supplier.py
│   ├── test_vision.py
│   ├── test_reporting.py
│   └── test_api.py
│
├── data/                         # Data directory
│   ├── README.md
│   └── download_datasets.py
│
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose setup
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.py                      # Package setup
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

---

## 🛠️ Teknoloji Stack'i / Technology Stack

### Backend
- **FastAPI** - Modern, high-performance web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Machine Learning
- **XGBoost** - Gradient boosting for quality prediction
- **scikit-learn** - Random Forest for RUL prediction
- **SHAP** - Model interpretability

### Computer Vision
- **OpenCV** - Image processing and defect detection
- **NumPy** - Numerical computations

### Dashboard
- **Streamlit** - Interactive web dashboard
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation

### Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support

### Database & Storage
- **In-memory storage** - Alert system (can be extended to SQLite/PostgreSQL)

---

## 🧪 Testing / Testler Çalıştırma

```bash
# Tüm testleri çalıştır / Run all tests
pytest

# Verbose output ile / With verbose output
pytest -v

# Coverage raporu ile / With coverage report
pytest --cov=modules --cov=api

# Belirli bir test dosyası / Specific test file
pytest tests/test_quality.py

# Belirli bir test / Specific test
pytest tests/test_api.py::TestRootEndpoints::test_health_endpoint
```

---

## 🔐 Güvenlik / Security

- API rate limiting önerilir / API rate limiting recommended
- Production ortamında HTTPS kullanın / Use HTTPS in production
- Environment variables ile hassas bilgileri saklayın / Store sensitive data in environment variables
- CORS ayarlarını production için kısıtlayın / Restrict CORS settings for production

---

## 📈 KPI Açıklamaları / KPI Descriptions

### OEE (Overall Equipment Effectiveness)
**Hedef:** ≥ 85%
- **Hesaplama:** Availability × Performance × Quality
- **Dünya standardı:** 85% ve üzeri

### FPY (First Pass Yield)
**Hedef:** ≥ 95%
- İlk denemede başarılı geçen ürün oranı
- **Formül:** (Başarılı Ürün / Toplam Ürün) × 100

### DPMO (Defects Per Million Opportunities)
**Hedef:** ≤ 35,000
- Milyon fırsatta hata sayısı
- **Formül:** (Hatalar / (Ürünler × Fırsatlar)) × 1,000,000

### Cpk (Process Capability Index)
**Hedef:** ≥ 1.33
- Süreç yeterlilik indeksi
- **Değerlendirme:**
  - Cpk < 1.0: Yetersiz süreç
  - Cpk 1.0-1.33: Kabul edilebilir
  - Cpk ≥ 1.33: Yeterli süreç
  - Cpk ≥ 2.0: Mükemmel süreç

---

## 🤝 Katkıda Bulunma / Contributing

1. Fork yapın / Fork the repository
2. Feature branch oluşturun / Create feature branch (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin / Commit changes (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin / Push to branch (`git push origin feature/amazing-feature`)
5. Pull Request açın / Open a Pull Request

---

## 📝 Lisans / License

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Geliştirici / Developer

**LED Yazılım Staj Projesi**

AI-Powered ERP Quality Module v1.0.0

---

## 📞 İletişim / Contact

- **GitHub Issues:** [Project Issues](https://github.com/altayyeles/ai-erp-quality-module/issues)
- **Pull Requests:** [Project PRs](https://github.com/altayyeles/ai-erp-quality-module/pulls)

---

## 🙏 Teşekkürler / Acknowledgments

- FastAPI community
- Streamlit team
- scikit-learn contributors
- OpenCV developers
- All open-source contributors

---

**⭐ Beğendiyseniz yıldız vermeyi unutmayın! / Don't forget to star if you like it!**
