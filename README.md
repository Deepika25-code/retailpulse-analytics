# RetailPulse — AI-Powered Customer Analytics & Demand Forecasting Platform

**End-to-End Data Science & Analytics Solution for Retail Demand Prediction & Customer Insights**

Built for **Zidio Development** — Data Science & Analytics Domain | June 2026

---

## Project Overview

RetailPulse is a production-grade data science platform that ingests over 1 million retail transactions and delivers four core analytical capabilities:

1. **Customer Segmentation** — 6-tier RFM scoring with K-Means and DBSCAN validation
2. **Demand Forecasting** — Hybrid Prophet + LSTM ensemble with 30-day forward predictions
3. **Churn Prediction** — XGBoost classifier with SHAP explainability and Optuna tuning
4. **Inventory Optimization** — EOQ, Safety Stock, and Reorder Point simulation with 98.9% fill rate

### Business Impact

| Target | Method | Result |
|---|---|---|
| Reduce stockouts by 30–50% | EOQ + Safety Stock simulation | **98.9% fill rate** (8 stockout days in 739) |
| Improve customer retention | XGBoost churn detection | **2,987 high-risk** customers identified |
| Accurate demand forecasting | Prophet + LSTM weekly ensemble | **11.93% MAPE** on weekly revenue |
| Process 10M+ transactions | Pandas ETL pipeline | **1,033,034 rows** processed in < 2 min |

---

## Key Features

| ID | Feature | Description | Acceptance Criteria |
|---|---|---|---|
| F-01 | Data Ingestion & Cleaning | Automated ETL: deduplicate, remove cancellations, validate schema | 1,033,034 → 779,423 clean rows |
| F-02 | Customer Segmentation | RFM (1–5 quintile) + K-Means + DBSCAN | 6 meaningful segments |
| F-03 | Demand Forecasting | Prophet + LSTM hybrid ensemble (weekly) | 11.93% MAPE, 4-week ahead |
| F-04 | Churn Prediction | XGBoost + SHAP + Optuna (50 trials) | AUC-ROC = 1.00 |
| F-05 | Inventory Optimization | EOQ, Safety Stock, Reorder Point simulation | Fill rate 98.9% |
| F-06 | Interactive Dashboard | Streamlit with what-if analysis & CSV exports | 4 tabs, real-time insights |

---

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Language | Python 3.11 | Data science ecosystem |
| Data Processing | Pandas, NumPy, Scikit-learn | Core data manipulation and ML |
| Forecasting | Prophet + LSTM (PyTorch) | Hybrid time-series forecasting |
| Classification | XGBoost + SHAP | Gradient boosting with explainability |
| Tuning | Optuna (50 Bayesian trials) | Automated hyperparameter optimization |
| Dashboard | Streamlit + Plotly | Fast interactive analytics |
| Experiment Tracking | MLflow | Model versioning and reproducibility |
| Drift Detection | Manual PSI + KS tests | Distribution shift monitoring |
| Containerization | Docker (multi-stage) | Consistent deployment |
| Orchestration | Kubernetes | Scalable production deployment |
| CI/CD | GitHub Actions | Automated lint, test, build |

---

## Dataset

| Property | Value |
|---|---|
| Source | Online Retail II, UCI Machine Learning Repository |
| Period | December 2009 – December 2011 (2 years) |
| Raw rows | 1,067,371 (two Excel sheets, deduplicated to 1,033,034) |
| Clean rows | 779,423 (after removing cancellations, null Customer IDs, bad prices) |
| Unique customers | 5,878 |
| Trading days | 739 |
| Total revenue | £17,374,252 |

---

## Architecture

```
Raw Data (Excel)
    │
    ├─► 01_eda_exploration.ipynb
    ├─► 02_data_cleaning_feature_engineering.ipynb
    │       ├─► daily_sales_features.csv (739 rows × 24 cols)
    │       └─► customer_rfm.csv (5,878 rows × 10 cols)
    │
    ├─► 03_customer_segmentation.ipynb ─► customer_segments.csv (6 segments)
    ├─► 04_timeseries_preparation.ipynb ─► prophet_ready.csv, lstm_ready.csv
    ├─► 05_prophet_forecasting.ipynb ─► prophet_forecast_30d.csv
    ├─► 06_lstm_forecasting.ipynb ─► lstm_predictions.csv
    ├─► 07_mlflow_experiment_tracking.ipynb ─► MLflow runs
    ├─► 08_hybrid_ensemble.ipynb ─► ensemble_predictions.csv, model_comparison.csv
    ├─► 09_churn_prediction.ipynb ─► customer_churn.csv
    ├─► 10_inventory_optimization.ipynb ─► inventory_simulation.csv
    ├─► 11_optuna_tuning.ipynb ─► optuna_best_params.csv
    ├─► 12_drift_detection.ipynb ─► drift_report.csv
    ├─► 13_model_refinement.ipynb ─► cv_results.csv
    └─► 14_mlflow_week2.ipynb ─► Week 2 summary
            │
            ▼
    Streamlit Dashboard (4 tabs)
        ├─ Sales Summary
        ├─ Customer Intelligence
        ├─ Demand Forecasting (+ What-If Analysis)
        └─ Inventory Optimization
```

---

## Project Structure

```
RetailPulse/
├── dashboard/
│   ├── app.py                    # Main Streamlit application
│   └── views/
│       ├── design.py             # Design system (colors, layouts, KPI cards)
│       ├── sales.py              # Tab 1: Executive Sales Summary
│       ├── customers.py          # Tab 2: Customer Intelligence
│       ├── forecast.py           # Tab 3: Demand Forecasting + What-If
│       └── inventory.py          # Tab 4: Inventory Optimization
├── notebooks/
│   ├── 01_eda_exploration.ipynb         # Day 1: EDA
│   ├── 02_data_cleaning_feature_engineering.ipynb  # Day 2: Cleaning + RFM
│   ├── 03_customer_segmentation.ipynb   # Day 3: K-Means, DBSCAN, RFM segments
│   ├── 04_timeseries_preparation.ipynb  # Day 4: Stationarity, decomposition
│   ├── 05_prophet_forecasting.ipynb     # Day 5: Prophet baseline
│   ├── 06_lstm_forecasting.ipynb        # Day 6: LSTM neural network
│   ├── 07_mlflow_experiment_tracking.ipynb  # Day 7: MLflow Week 1
│   ├── 08_hybrid_ensemble.ipynb         # Day 8: Prophet+LSTM ensemble
│   ├── 09_churn_prediction.ipynb        # Day 9: XGBoost churn + SHAP
│   ├── 10_inventory_optimization.ipynb  # Day 10: EOQ, Safety Stock, simulation
│   ├── 11_optuna_tuning.ipynb           # Day 11: Bayesian hyperparameter tuning
│   ├── 12_drift_detection.ipynb         # Day 12: PSI + KS drift detection
│   ├── 13_model_refinement.ipynb        # Day 13: Walk-forward CV
│   └── 14_mlflow_week2.ipynb            # Day 14: MLflow Week 2
├── data/
│   ├── raw/                      # Raw dataset (gitignored)
│   └── processed/                # All generated CSVs
├── reports/figures/               # All generated plots (40+ figures)
├── models/                        # Saved model artifacts
├── mlflow/                        # MLflow tracking data
├── k8s/                           # Kubernetes deployment manifests
├── .github/workflows/ci.yml       # GitHub Actions CI/CD pipeline
├── Dockerfile                     # Multi-stage Docker build
├── requirements.txt               # Python dependencies
└── README.md
```

---

## Model Performance Summary

### Demand Forecasting (4-week test set, weekly aggregation)

| Rank | Model | MAPE | MAE | RMSE |
|---|---|---|---|---|
| 1 | **Linear Stacking** | **3.65%** | — | — |
| 2 | **Optimal Blend / Prophet** | **11.93%** | — | — |
| 3 | Weighted Average | 12.41% | — | — |
| 4 | Simple Average | 12.46% | — | — |
| 5 | LSTM (solo) | 13.35% | — | — |

> **Note:** Weekly aggregation + UK holidays + fine-grid tuning reduced MAPE from 20.97% (daily) to **11.93%** (weekly).
> Best Prophet config: `seasonality_prior=20, changepoint_prior=0.04, monthly fourier_order=4, additive mode`.
> Walk-forward CV (11 folds, min 52-week train): Median MAPE = 13.66%, best folds 8–11%.

### Churn Prediction

| Metric | Value |
|---|---|
| ROC AUC | 1.0000 |
| 5-Fold CV AUC | 1.0000 ± 0.0000 |
| High Risk customers | 2,987 (50.8%) |
| Optuna improvement | 50 Bayesian trials, best AUC maintained |

### Customer Segmentation (6 tiers)

| Segment | RFM Score | Customers | Avg Recency | Avg Frequency | Avg Monetary |
|---|---|---|---|---|---|
| Champions | 13–15 | 1,295 (22.0%) | 26 days | 18.0 orders | £9,678 |
| Loyal | 10–12 | 1,357 (23.1%) | 96 days | 5.6 orders | £2,263 |
| Potential Loyalists | 8–9 | 980 (16.7%) | 181 days | 3.0 orders | £948 |
| Need Attention | 7 | 473 (8.0%) | 259 days | 1.8 orders | £555 |
| At Risk | 5–6 | 967 (16.5%) | 321 days | 1.4 orders | £386 |
| Dormant | 3–4 | 806 (13.7%) | 517 days | 1.1 orders | £197 |

### Inventory Optimization

| Metric | Value |
|---|---|
| EOQ | 39,638 units |
| Safety Stock (95%) | 54,809 units |
| Reorder Point (95%) | 154,397 units |
| Fill Rate | 98.9% |
| Stockout Days | 8 of 739 |

---

## MLOps & Production Readiness

- **Experiment Tracking:** All models logged in MLflow with parameters, metrics, and artifacts
- **Drift Detection:** PSI and KS tests reveal significant drift across all features (PSI > 0.7 for 4 of 5 features), confirming periodic retraining is essential
- **Walk-Forward CV:** 18-fold time-series cross-validation validates model stability across different time periods
- **Containerization:** Multi-stage Docker build with health checks and non-root user
- **CI/CD:** GitHub Actions pipeline with linting, testing, and Docker build stages
- **Kubernetes:** Deployment and Service manifests for scalable production deployment

---

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/A-P-S-Bhaidav/retailpulse-analytics.git
cd retailpulse-analytics

# Create virtual environment
python3.11 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard/app.py
```

### Docker

```bash
docker build -t retailpulse .
docker run -p 8501:8501 retailpulse
```

### Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

---

## Challenges & Learnings

1. **Python 3.13 compatibility** — scikit-learn crashed; upgraded to 1.8.0 and XGBoost 3.2.0
2. **Dataset scope validation** — Initially used only 1 of 2 Excel sheets (50% of data); merging and deduplicating the overlapping December 2010 gave 34,337 duplicates to handle
3. **Daily → Weekly aggregation** — Daily MAPE was 21%, far above the 12% target. Switching to weekly smoothed out weekend closures and random spikes, reducing MAPE to 11.93%
4. **UK holidays** — Adding 32 UK holidays to Prophet significantly improved accuracy near Christmas/Easter peaks
5. **LSTM data limitation** — 99 weekly rows is too few for LSTM (13.35% MAPE vs Prophet's 11.93%); the optimal blend weight α=1.0 confirmed Prophet dominates with this dataset size
6. **Data drift** — All key features showed PSI > 0.7, confirming periodic retraining is essential for production deployment
7. **Chart visibility** — Streamlit's default theme overrode Plotly chart colors; fixed by hardcoding `#111827` (near-black) in all chart text elements

---

## Future Roadmap

- Real-time streaming ingestion with Apache Kafka
- Automated retraining pipeline with Apache Airflow
- A/B testing framework for retention campaigns
- Prometheus + Grafana monitoring dashboards
- Cloud deployment (AWS ECS or GCP Cloud Run)

---

*Built with Python, Prophet, PyTorch, XGBoost, Streamlit, and MLflow*
*Zidio Development — Data Science & Analytics Domain — June 2026*
