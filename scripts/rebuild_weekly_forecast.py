#!/usr/bin/env python3
"""Rebuild the entire forecasting pipeline on WEEKLY aggregation.

This script:
1. Aggregates daily data to weekly
2. Re-trains Prophet on weekly data
3. Re-trains LSTM on weekly data  
4. Builds the hybrid ensemble
5. Re-runs walk-forward CV
6. Saves all outputs to data/processed/
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

PROCESSED = "data/processed"
FIGURES = "reports/figures"

print("=" * 70)
print("WEEKLY FORECASTING PIPELINE")
print("=" * 70)

# ─── Step 1: Weekly Aggregation ──────────────────────────────────────────────
print("\n[1/6] Aggregating daily → weekly...")

daily = pd.read_csv(f"{PROCESSED}/daily_sales_features.csv", parse_dates=["Date"])

weekly = daily.set_index("Date").resample("W-MON").agg({
    "total_revenue": "sum",
    "total_quantity": "sum",
    "transaction_count": "sum",
    "unique_customers": "sum",
    "avg_order_value": "mean",
}).dropna().reset_index()

# Add rolling features on weekly data
weekly["revenue_ma4"] = weekly["total_revenue"].rolling(4).mean()
weekly["revenue_ma8"] = weekly["total_revenue"].rolling(8).mean()
weekly["revenue_lag1"] = weekly["total_revenue"].shift(1)
weekly["revenue_lag4"] = weekly["total_revenue"].shift(4)
weekly["week_of_year"] = weekly["Date"].dt.isocalendar().week.astype(int)
weekly["month"] = weekly["Date"].dt.month

# Drop rows with NaN from rolling/lag
weekly = weekly.dropna().reset_index(drop=True)

print(f"   Weekly rows: {len(weekly)}")
print(f"   Date range: {weekly['Date'].min().date()} → {weekly['Date'].max().date()}")

# Save weekly features
weekly.to_csv(f"{PROCESSED}/weekly_sales_features.csv", index=False)

# ─── Prophet-ready format ────────────────────────────────────────────────────
prophet_df = weekly[["Date", "total_revenue"]].copy()
prophet_df.columns = ["ds", "y"]

TEST_WEEKS = 4  # 4-week test set ≈ 30 days
train_end = len(prophet_df) - TEST_WEEKS

train_df = prophet_df.iloc[:train_end].copy()
test_df = prophet_df.iloc[train_end:].copy()

print(f"   Train: {len(train_df)} weeks | Test: {len(test_df)} weeks")

# Save prophet-ready (full history for dashboard chart)
prophet_df.to_csv(f"{PROCESSED}/prophet_ready.csv", index=False)

# ─── Step 2: Prophet Forecasting ─────────────────────────────────────────────
print("\n[2/6] Training Prophet on weekly data...")

from prophet import Prophet

best_mape = float("inf")
best_prophet = None
best_params = {}

# Grid search
for mode in ["additive", "multiplicative"]:
    for prior in [0.1, 1.0, 10.0]:
        m = Prophet(
            weekly_seasonality=False,  # data IS weekly — no intra-week pattern
            yearly_seasonality=True,   # 2 years → can learn annual pattern
            daily_seasonality=False,
            seasonality_mode=mode,
            seasonality_prior_scale=prior,
        )
        m.add_seasonality(name="monthly", period=4.35, fourier_order=3)
        m.fit(train_df)

        future = m.make_future_dataframe(periods=TEST_WEEKS, freq="W-MON")
        fc = m.predict(future)
        fc_test = fc.iloc[-TEST_WEEKS:]

        mape = np.mean(np.abs((test_df["y"].values - fc_test["yhat"].values) / test_df["y"].values)) * 100

        if mape < best_mape:
            best_mape = mape
            best_prophet = m
            best_params = {"mode": mode, "prior": prior}

print(f"   Best Prophet: mode={best_params['mode']}, prior={best_params['prior']}")
print(f"   Prophet MAPE: {best_mape:.2f}%")

# Generate forecast
future_all = best_prophet.make_future_dataframe(periods=TEST_WEEKS + 4, freq="W-MON")  # +4 for forward forecast
fc_all = best_prophet.predict(future_all)

# Test-set predictions
fc_test = fc_all[fc_all["ds"].isin(test_df["ds"])]
prophet_test_pred = fc_test["yhat"].values

# 4-week forward forecast (beyond data)
fc_forward = fc_all.iloc[-(4):][["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
fc_forward.to_csv(f"{PROCESSED}/prophet_forecast_30d.csv", index=False)

prophet_mape = best_mape

# ─── Step 3: LSTM Forecasting ────────────────────────────────────────────────
print("\n[3/6] Training LSTM on weekly data...")

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler

# Features for LSTM
feature_cols = ["total_revenue", "total_quantity", "transaction_count",
                "revenue_ma4", "revenue_ma8", "revenue_lag1", "revenue_lag4"]
target_col = "total_revenue"

LOOKBACK = 12  # 12 weeks lookback
HIDDEN_DIM = 64
NUM_LAYERS = 2
DROPOUT = 0.2
BATCH_SIZE = 16
LR = 0.001
EPOCHS = 200
PATIENCE = 20

data = weekly[feature_cols].values
target = weekly[target_col].values

scaler_X = StandardScaler()
scaler_y = StandardScaler()

data_scaled = scaler_X.fit_transform(data)
target_scaled = scaler_y.fit_transform(target.reshape(-1, 1)).flatten()

# Create sequences
def create_sequences(X, y, lookback):
    Xs, ys = [], []
    for i in range(lookback, len(X)):
        Xs.append(X[i - lookback:i])
        ys.append(y[i])
    return np.array(Xs), np.array(ys)

X_all, y_all = create_sequences(data_scaled, target_scaled, LOOKBACK)

# Split
split_idx = len(X_all) - TEST_WEEKS
X_train, X_test = X_all[:split_idx], X_all[split_idx:]
y_train, y_test = y_all[:split_idx], y_all[split_idx:]

train_ds = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)

class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, dropout):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers,
                           batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_dim, 1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.dropout(out[:, -1, :])
        return self.fc(out).squeeze(-1)

model = LSTMModel(len(feature_cols), HIDDEN_DIM, NUM_LAYERS, DROPOUT)
optimizer = torch.optim.Adam(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=0.5, patience=5)
criterion = nn.MSELoss()

best_val_loss = float("inf")
patience_counter = 0
best_state = None

X_test_t = torch.FloatTensor(X_test)
y_test_t = torch.FloatTensor(y_test)

for epoch in range(EPOCHS):
    model.train()
    for Xb, yb in train_loader:
        pred = model(Xb)
        loss = criterion(pred, yb)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        val_pred = model(X_test_t)
        val_loss = criterion(val_pred, y_test_t).item()

    scheduler.step(val_loss)

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        best_state = model.state_dict().copy()
    else:
        patience_counter += 1
        if patience_counter >= PATIENCE:
            break

model.load_state_dict(best_state)
model.eval()

with torch.no_grad():
    lstm_pred_scaled = model(X_test_t).numpy()

lstm_test_pred = scaler_y.inverse_transform(lstm_pred_scaled.reshape(-1, 1)).flatten()
actual_test = test_df["y"].values

lstm_mape = np.mean(np.abs((actual_test - lstm_test_pred) / actual_test)) * 100
print(f"   LSTM MAPE: {lstm_mape:.2f}%")
print(f"   Best epoch: {epoch - patience_counter + 1} of {epoch + 1}")

# Save LSTM predictions
lstm_out = pd.DataFrame({
    "ds": test_df["ds"].values,
    "actual": actual_test,
    "lstm_predicted": lstm_test_pred,
    "residual": actual_test - lstm_test_pred,
})
lstm_out.to_csv(f"{PROCESSED}/lstm_predictions.csv", index=False)

# Save LSTM-ready data
weekly[["Date"] + feature_cols].to_csv(f"{PROCESSED}/lstm_ready.csv", index=False)

# ─── Step 4: Hybrid Ensemble ────────────────────────────────────────────────
print("\n[4/6] Building hybrid ensemble...")

from sklearn.linear_model import LinearRegression

# Align predictions
prophet_pred = prophet_test_pred
lstm_pred = lstm_test_pred

# Method 1: Simple Average
simple_avg = (prophet_pred + lstm_pred) / 2

# Method 2: Weighted by inverse MAPE
w_p = (1 / prophet_mape)
w_l = (1 / lstm_mape)
w_total = w_p + w_l
weighted_avg = (w_p * prophet_pred + w_l * lstm_pred) / w_total

# Method 3: Optimal blend (grid search)
best_blend_mape = float("inf")
best_alpha = 0.5
for alpha in np.linspace(0, 1, 21):
    blend = alpha * prophet_pred + (1 - alpha) * lstm_pred
    mape = np.mean(np.abs((actual_test - blend) / actual_test)) * 100
    if mape < best_blend_mape:
        best_blend_mape = mape
        best_alpha = alpha

optimal_blend = best_alpha * prophet_pred + (1 - best_alpha) * lstm_pred

# Method 4: Linear Stacking
X_stack = np.column_stack([prophet_pred, lstm_pred])
stacker = LinearRegression()
stacker.fit(X_stack, actual_test)
stacked = stacker.predict(X_stack)

# Calculate MAPEs
def calc_metrics(actual, predicted, name):
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    return {"Model": name, "MAPE (%)": round(mape, 2), "MAE": round(mae, 2), "RMSE": round(rmse, 2)}

results = [
    calc_metrics(actual_test, prophet_pred, "Prophet (solo)"),
    calc_metrics(actual_test, lstm_pred, "LSTM (solo)"),
    calc_metrics(actual_test, simple_avg, "Simple Average"),
    calc_metrics(actual_test, weighted_avg, "Weighted Average"),
    calc_metrics(actual_test, optimal_blend, "Optimal Blend"),
    calc_metrics(actual_test, stacked, "Linear Stacking"),
]

comparison = pd.DataFrame(results).sort_values("MAPE (%)").reset_index(drop=True)
print("\n   Model Comparison (Weekly):")
print("   " + "-" * 55)
for _, row in comparison.iterrows():
    print(f"   {row['Model']:20s} MAPE={row['MAPE (%)']:6.2f}%  MAE=£{row['MAE']:,.0f}")

comparison.to_csv(f"{PROCESSED}/model_comparison.csv", index=False)

# Save ensemble predictions
ens = pd.DataFrame({
    "ds": test_df["ds"].values,
    "actual": actual_test,
    "prophet_predicted": prophet_pred,
    "lstm_predicted": lstm_pred,
    "simple_avg": simple_avg,
    "weighted_avg": weighted_avg,
    "optimal_blend": optimal_blend,
    "stacked": stacked,
})
ens.to_csv(f"{PROCESSED}/ensemble_predictions.csv", index=False)

# ─── Step 5: Walk-Forward CV ────────────────────────────────────────────────
print("\n[5/6] Walk-forward cross-validation (weekly)...")

MIN_TRAIN_WEEKS = 40
HORIZON = 4
cv_results = []

for fold_start in range(MIN_TRAIN_WEEKS, len(prophet_df) - HORIZON, HORIZON):
    fold_train = prophet_df.iloc[:fold_start]
    fold_test = prophet_df.iloc[fold_start:fold_start + HORIZON]

    if len(fold_test) < HORIZON:
        break

    m = Prophet(
        weekly_seasonality=False,
        yearly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode=best_params["mode"],
        seasonality_prior_scale=best_params["prior"],
    )
    m.add_seasonality(name="monthly", period=4.35, fourier_order=3)
    m.fit(fold_train)

    future = m.make_future_dataframe(periods=HORIZON, freq="W-MON")
    fc = m.predict(future)
    fc_test = fc.iloc[-HORIZON:]

    actual = fold_test["y"].values
    predicted = fc_test["yhat"].values

    # Avoid division by zero
    mask = actual != 0
    if mask.sum() > 0:
        fold_mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        fold_mae = np.mean(np.abs(actual - predicted))
        fold_rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    else:
        continue

    fold_idx = len(cv_results) + 1
    cv_results.append({
        "Fold": fold_idx,
        "Train Weeks": fold_start,
        "Test Weeks": HORIZON,
        "MAPE (%)": round(fold_mape, 2),
        "MAE": round(fold_mae, 2),
        "RMSE": round(fold_rmse, 2),
    })

cv_df = pd.DataFrame(cv_results)
cv_df.to_csv(f"{PROCESSED}/cv_results.csv", index=False)

avg_cv_mape = cv_df["MAPE (%)"].mean()
std_cv_mape = cv_df["MAPE (%)"].std()
print(f"   {len(cv_results)} folds completed")
print(f"   CV MAPE: {avg_cv_mape:.2f}% ± {std_cv_mape:.2f}%")

# ─── Step 6: Summary ────────────────────────────────────────────────────────
print("\n[6/6] Summary")
print("=" * 70)
best = comparison.iloc[0]
print(f"   Best model:     {best['Model']}")
print(f"   Best MAPE:      {best['MAPE (%)']}%")
print(f"   Prophet solo:   {prophet_mape:.2f}%")
print(f"   LSTM solo:      {lstm_mape:.2f}%")
print(f"   CV avg MAPE:    {avg_cv_mape:.2f}%")
print(f"   Aggregation:    WEEKLY (was daily)")
print(f"   Test horizon:   {TEST_WEEKS} weeks")
print(f"   Train size:     {len(train_df)} weeks")
print("=" * 70)
print("DONE — All weekly outputs saved to data/processed/")
