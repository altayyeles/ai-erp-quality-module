# 🏭 AI-Powered ERP Quality Module

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **AI destekli ERP Kalite Modülü** — Yapay zeka ve makine öğrenmesi ile üretim süreçlerinde kalite yönetimi, öngörücü bakım, tedarikçi risk skorlaması ve görsel denetim sistemi.

---

## 📋 İçindekiler

- [Genel Bakış](#genel-bakış)
- [Mimari](#mimari)
- [Modüller](#modüller)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [API Dokümantasyonu](#api-dokümantasyonu)
- [Teknoloji Stack](#teknoloji-stack)
- [Geliştirici Notu](#geliştirici-notu)

---

## 🎯 Genel Bakış

Bu proje, üretim süreçlerinde yapay zeka destekli kalite yönetimi sağlayan kapsamlı bir ERP modülüdür. Sistem, gerçek zamanlı sensör verilerini analiz ederek defekt tahmini, öngörücü bakım, tedarikçi risk değerlendirmesi ve görsel kalite kontrol yetenekleri sunar.

### Temel Özellikler

- 🔮 **Öngörücü Kalite Analizi**: XGBoost + SHAP ile defekt tahmin modeli
- 🔧 **Öngörücü Bakım**: Random Forest ile RUL (Remaining Useful Life) tahmini
- 🚚 **Tedarikçi Skorlaması**: K-Means clustering + IsolationForest ile risk analizi
- 👁️ **Görsel Denetim**: OpenCV + YOLO ile defekt tespiti
- 📊 **KPI Raporlama**: OEE, FPY, DPMO, Cpk metrikleri ve alert yönetimi
- 📈 **SPC Analizi**: İstatistiksel proses kontrol grafikleri (X-bar, R, p-charts)

---

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                      STREAMLIT DASHBOARD                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Quality  │ │  Maint.  │ │ Supplier │ │  Vision  │      │
│  │Prediction│ │ Monitor  │ │ Scoring  │ │ Inspect  │      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │
└───────┼────────────┼────────────┼─────────────┼────────────┘
        │            │            │             │
        └────────────┴────────────┴─────────────┘
                     │
        ┌────────────▼────────────────────────────────────────┐
        │              FASTAPI REST API                       │
        │  ┌──────────────────────────────────────────────┐  │
        │  │  /quality  /maintenance  /suppliers  /vision │  │
        │  └──────────────────────────────────────────────┘  │
        └────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼────────────────────────────────────────┐
        │                  MODULES LAYER                      │
        │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐  │
        │  │ Quality  │ │  Maint.  │ │ Supplier │ │Vision│  │
        │  │  Model   │ │RUL Model │ │  Scorer  │ │ CV   │  │
        │  └──────────┘ └──────────┘ └──────────┘ └──────┘  │
        └────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼────────────────────────────────────────┐
        │                  DATA LAYER                         │
        │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐  │
        │  │ SQLite   │ │  Models  │ │  Sensor  │ │Image │  │
        │  │   DB     │ │   PKL    │ │  Data    │ │ Data │  │
        │  └──────────┘ └──────────┘ └──────────┘ └──────┘  │
        └─────────────────────────────────────────────────────┘
```

---

## 🧩 Modüller

### 1. Quality Module (Kalite Modülü)

**Dosyalar:**
- `modules/quality/predictive_model.py` — XGBoost tabanlı defekt tahmin modeli
- `modules/quality/spc_analysis.py` — İstatistiksel proses kontrol analizi

**Özellikler:**
- XGBoost classifier ile defekt olasılığı tahmini
- SHAP (SHapley Additive exPlanations) ile model açıklanabilirliği
- X-bar, R, p-chart kontrol grafikleri
- Western Electric kuralları ile anomali tespiti
- Cp, Cpk proses yetenek analizi

**Kullanım:**
```python
from modules.quality.predictive_model import QualityPredictiveModel

model = QualityPredictiveModel()
result = model.predict_defect_probability({
    'air_temperature': 298.0,
    'process_temperature': 308.0,
    'rotational_speed': 1500.0,
    'torque': 40.0,
    'tool_wear': 100.0,
    'vibration': 0.5,
    'humidity': 60.0,
    'pressure': 1.0
})

print(f"Defect Probability: {result.defect_probability:.2%}")
print(f"Risk Level: {result.risk_level}")
```

### 2. Maintenance Module (Bakım Modülü)

**Dosyalar:**
- `modules/maintenance/rul_model.py` — Random Forest ile RUL tahmini
- `modules/maintenance/sensor_monitor.py` — Gerçek zamanlı sensör izleme

**Özellikler:**
- 8 makine (M001-M008) için gerçek zamanlı durum izleme
- Random Forest Regressor ile RUL tahmini
- Bakım aciliyet seviyesi belirleme (NORMAL/WARNING/CRITICAL)
- Sensör trend analizi ve anomali tespiti

**Kullanım:**
```python
from modules.maintenance.rul_model import RULModel
from modules.maintenance.sensor_monitor import SensorMonitor

# RUL prediction
rul_model = RULModel()
result = rul_model.predict(sensor_data)
print(f"RUL: {result['rul_hours']:.1f} hours")
print(f"Urgency: {result['maintenance_urgency']}")

# Machine monitoring
monitor = SensorMonitor()
machines = monitor.get_all_machines()
for machine in machines:
    print(f"{machine['machine_id']}: {machine['status']}")
```

### 3. Supplier Module (Tedarikçi Modülü)

**Dosyalar:**
- `modules/supplier/supplier_score.py` — Ağırlıklı skorlama sistemi
- `modules/supplier/procurement_advisor.py` — Satın alma danışmanlık

**Özellikler:**
- Ağırlıklı skorlama (Quality 30%, Delivery 25%, Defect 20%, Price 15%, Response 10%)
- K-Means clustering ile kategorizasyon
- IsolationForest ile anomali tespiti
- Risk seviyesi belirleme (LOW/MEDIUM/HIGH/CRITICAL)
- Satın alma önerileri (RECOMMEND/MONITOR/REVIEW/REJECT)

**Kullanım:**
```python
from modules.supplier.supplier_score import SupplierScorer
from modules.supplier.procurement_advisor import ProcurementAdvisor

scorer = SupplierScorer()
result = scorer.score({
    'supplier_id': 'SUP-001',
    'quality_score': 0.85,
    'on_time_delivery_rate': 0.90,
    'defect_rate': 0.03,
    'price_competitiveness': 0.75,
    'response_time_days': 2.0,
    'years_of_partnership': 3.0
})

print(f"Score: {result['overall_score']:.1f}")
print(f"Risk: {result['risk_level']}")
print(f"Category: {result['category']}")
```

### 4. Vision Module (Görsel Denetim Modülü)

**Dosyalar:**
- `modules/vision/visual_inspection.py` — OpenCV ile defekt tespiti
- `modules/vision/anomaly_detector.py` — Görsel anomali analizi

**Özellikler:**
- Canny edge detection ve kontur analizi
- Brightness, contrast ve noise analizi
- Histogram entropy hesaplama
- Edge density değerlendirme
- YOLO entegrasyonu ile OpenCV fallback

**Kullanım:**
```python
from modules.vision.visual_inspection import VisualInspector
from modules.vision.anomaly_detector import AnomalyDetector

# Visual inspection
inspector = VisualInspector()
with open('product_image.jpg', 'rb') as f:
    result = inspector.inspect_bytes(f.read())
    
print(f"Defects Found: {result['defects_found']}")
print(f"Quality Score: {result['quality_score']:.1f}")

# Anomaly detection
detector = AnomalyDetector()
result = detector.detect_bytes(image_bytes)
print(f"Is Anomaly: {result['is_anomaly']}")
print(f"Anomaly Type: {result['anomaly_type']}")
```

### 5. Reporting Module (Raporlama Modülü)

**Dosyalar:**
- `modules/reporting/kpi_engine.py` — KPI hesaplama motoru
- `modules/reporting/alert_system.py` — SQLite tabanlı alert yönetimi

**Özellikler:**
- OEE, FPY, DPMO, Cpk hesaplama
- 30 günlük trend analizi
- SQLite ile alert yönetimi
- Severity seviyeleri (INFO/WARNING/ERROR/CRITICAL)

**Kullanım:**
```python
from modules.reporting.kpi_engine import KPIEngine
from modules.reporting.alert_system import AlertSystem

# KPI metrics
kpi = KPIEngine()
snapshot = kpi.get_snapshot()
print(f"OEE: {snapshot['oee']:.1f}%")
print(f"FPY: {snapshot['fpy']:.1f}%")

# Alerts
alerts = AlertSystem()
active_alerts = alerts.get_active_alerts()
for alert in active_alerts:
    print(f"[{alert['severity']}] {alert['title']}")
```

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- Docker (opsiyonel)

### Manuel Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/altayyeles/ai-erp-quality-module.git
cd ai-erp-quality-module

# Sanal ortam oluşturun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# (Opsiyonel) Geliştirme bağımlılıkları
pip install -r requirements-dev.txt
```

### Docker ile Kurulum

```bash
# Docker Compose ile başlatın
docker-compose up -d

# Logları kontrol edin
docker-compose logs -f
```

---

## 💻 Kullanım

### FastAPI Backend

```bash
# API sunucusunu başlatın
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# API dokümantasyonu
# http://localhost:8000/docs
```

### Streamlit Dashboard

```bash
# Dashboard'u başlatın
streamlit run dashboard/app.py

# Dashboard URL
# http://localhost:8501
```

---

## 📚 API Dokümantasyonu

### API Endpoints

#### Quality Module

```bash
# Defect prediction
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

# Feature importance
GET /api/v1/quality/feature-importance

# SPC analysis
GET /api/v1/quality/spc-analysis
```

#### Maintenance Module

```bash
# RUL prediction
POST /api/v1/maintenance/predict-rul
{
  "air_temperature": 298.0,
  ...
}

# Get all machines
GET /api/v1/maintenance/machines

# Get specific machine
GET /api/v1/maintenance/machines/M001
```

#### Supplier Module

```bash
# Score supplier
POST /api/v1/suppliers/score
{
  "supplier_id": "SUP-001",
  "quality_score": 0.85,
  "on_time_delivery_rate": 0.90,
  "defect_rate": 0.03,
  "price_competitiveness": 0.75,
  "response_time_days": 2.0,
  "years_of_partnership": 3.0
}

# Get procurement advice
POST /api/v1/suppliers/advise
{...}
```

#### Vision Module

```bash
# Visual inspection
POST /api/v1/vision/inspect
Content-Type: multipart/form-data
file: <image_file>

# Detect anomaly
POST /api/v1/vision/detect-anomaly
Content-Type: multipart/form-data
file: <image_file>
```

#### Dashboard Module

```bash
# Get KPI snapshot
GET /api/v1/dashboard/kpis

# Get active alerts
GET /api/v1/dashboard/alerts

# Dismiss alert
DELETE /api/v1/dashboard/alerts/{alert_id}
```

### cURL Örnekleri

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

# Get machines
curl "http://localhost:8000/api/v1/maintenance/machines"

# Score supplier
curl -X POST "http://localhost:8000/api/v1/suppliers/score" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_id": "SUP-001",
    "quality_score": 0.85,
    "on_time_delivery_rate": 0.90,
    "defect_rate": 0.03,
    "price_competitiveness": 0.75,
    "response_time_days": 2.0,
    "years_of_partnership": 3.0
  }'

# Visual inspection
curl -X POST "http://localhost:8000/api/v1/vision/inspect" \
  -F "file=@product_image.jpg"
```

---

## 🛠️ Teknoloji Stack

### Backend
- **FastAPI** — Modern, hızlı web framework
- **Uvicorn** — ASGI web sunucusu
- **Pydantic** — Veri validasyonu

### Machine Learning
- **XGBoost** — Gradient boosting framework (Quality)
- **scikit-learn** — Random Forest, K-Means, IsolationForest
- **SHAP** — Model açıklanabilirliği
- **TensorFlow/Keras** — Deep learning (opsiyonel)

### Computer Vision
- **OpenCV** — Görsel işleme
- **Ultralytics YOLO** — Nesne tespiti (opsiyonel)
- **Pillow** — Görsel manipülasyonu

### Dashboard & Visualization
- **Streamlit** — İnteraktif dashboard
- **Plotly** — İnteraktif grafikler
- **Matplotlib/Seaborn** — Statik grafikler
- **Pandas** — Veri manipülasyonu

### Database & Storage
- **SQLite** — Hafif veritabanı (KPI, Alerts)
- **SQLAlchemy** — ORM (opsiyonel)
- **joblib** — Model serializasyonu

### DevOps
- **Docker** — Konteynerizasyon
- **Docker Compose** — Multi-container orkestrasyon

---

## 📂 Proje Yapısı

```
ai-erp-quality-module/
├── api/                          # FastAPI backend
│   ├── main.py                   # Ana uygulama
│   └── routes/                   # API route'ları
│       ├── quality.py
│       ├── maintenance.py
│       ├── supplier.py
│       ├── vision.py
│       └── dashboard.py
├── modules/                      # İş mantığı modülleri
│   ├── quality/
│   │   ├── predictive_model.py
│   │   └── spc_analysis.py
│   ├── maintenance/
│   │   ├── rul_model.py
│   │   └── sensor_monitor.py
│   ├── supplier/
│   │   ├── supplier_score.py
│   │   └── procurement_advisor.py
│   ├── vision/
│   │   ├── visual_inspection.py
│   │   └── anomaly_detector.py
│   └── reporting/
│       ├── kpi_engine.py
│       └── alert_system.py
├── dashboard/                    # Streamlit dashboard
│   ├── app.py                    # Ana sayfa
│   └── pages/                    # Alt sayfalar
│       ├── 1_Quality_Prediction.py
│       ├── 2_Maintenance.py
│       ├── 3_Supplier.py
│       ├── 4_Vision.py
│       └── 5_Reports.py
├── data/                         # Veri dizini
│   ├── raw/                      # Ham veri
│   ├── processed/                # İşlenmiş veri
│   ├── kpi_metrics.db           # KPI veritabanı
│   └── alerts.db                # Alert veritabanı
├── models/                       # Eğitilmiş modeller
│   ├── quality_model.pkl
│   └── rul_model.pkl
├── Dockerfile                    # Docker imajı
├── docker-compose.yml           # Çoklu konteyner yapılandırması
├── requirements.txt             # Python bağımlılıkları
└── README.md                    # Dokümantasyon
```

---

## 🎓 Geliştirici Notu

Bu proje **LED Yazılım Staj Projesi** kapsamında geliştirilmiştir. Proje, gerçek dünya üretim ortamlarında kullanılabilecek yapay zeka destekli kalite yönetim sistemi geliştirme deneyimi sağlamak amacıyla tasarlanmıştır.

### Öğrenilen Konular

- Makine öğrenmesi model geliştirme ve deployment
- REST API tasarımı ve FastAPI kullanımı
- Computer vision ile görsel kalite kontrol
- İstatistiksel proses kontrolü (SPC)
- Gerçek zamanlı veri izleme ve alerting
- Docker ile konteynerizasyon
- Streamlit ile interaktif dashboard geliştirme

---

## 📝 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

---

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

---

## 📧 İletişim

**Proje:** AI-Powered ERP Quality Module  
**Geliştirici:** LED Yazılım Staj Projesi  
**GitHub:** [@altayyeles](https://github.com/altayyeles)

---

## ⭐ Yıldız Vermeyi Unutmayın!

Projeyi beğendiyseniz GitHub'da ⭐ vermeyi unutmayın!
