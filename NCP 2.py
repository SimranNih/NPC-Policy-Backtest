import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================
# 1. LOAD DATA
# ============================

fx = pd.read_csv(r"C:\Users\Simran Nihalani\OneDrive\Documents\Models\usdchn.csv")
y2 = pd.read_csv(r"C:\Users\Simran Nihalani\OneDrive\Documents\Models\china_2y.csv")
y10 = pd.read_csv(r"C:\Users\Simran Nihalani\OneDrive\Documents\Models\china_10y.csv")

# Keep only Date and Price columns (Investing.com fix)
fx = fx[["Date","Price"]]
y2 = y2[["Date","Price"]]
y10 = y10[["Date","Price"]]

fx.columns = ["Date","USDCNH"]
y2.columns = ["Date","Y2"]
y10.columns = ["Date","Y10"]

# ============================
# 2. CLEAN DATA
# ============================

# Convert dates
fx["Date"] = pd.to_datetime(fx["Date"], format="mixed", dayfirst=True, errors="coerce")
y2["Date"] = pd.to_datetime(y2["Date"], format="mixed", errors="coerce")
y10["Date"] = pd.to_datetime(y10["Date"], format="mixed", errors="coerce")

fx = fx.dropna(subset=["Date"])
y2 = y2.dropna(subset=["Date"])
y10 = y10.dropna(subset=["Date"])

# Remove commas if present
fx["USDCNH"] = fx["USDCNH"].astype(str).str.replace(",", "")
y2["Y2"] = y2["Y2"].astype(str).str.replace(",", "")
y10["Y10"] = y10["Y10"].astype(str).str.replace(",", "")

# Convert to numeric
fx["USDCNH"] = pd.to_numeric(fx["USDCNH"], errors="coerce")
y2["Y2"] = pd.to_numeric(y2["Y2"], errors="coerce")
y10["Y10"] = pd.to_numeric(y10["Y10"], errors="coerce")

# Set index
fx = fx.set_index("Date")
y2 = y2.set_index("Date")
y10 = y10.set_index("Date")

# ============================
# 3. MERGE DATA
# ============================

df = pd.concat([fx, y2, y10], axis=1)
df = df.sort_index()

# Forward fill yields (common in macro data)
df["Y2"] = df["Y2"].ffill().bfill()
df["Y10"] = df["Y10"].ffill().bfill()

# Drop missing FX values
df = df.dropna(subset=["USDCNH"])

# ============================
# 4. CALCULATE RETURNS
# ============================

log_returns = np.log(df["USDCNH"] / df["USDCNH"].shift(1))

# FX realized volatility
fx_vol = log_returns.rolling(30).std() * np.sqrt(252)

# Yield curve slope
df["Curve"] = df["Y10"] - df["Y2"]

fx_vol = fx_vol.dropna()

# ============================
# 5. POLICY EVENTS
# ============================

policy_events = [
    "2020-05-22",
    "2021-12-06",
    "2022-04-29",
    "2023-07-24",
    "2024-03-05",
    "2025-03-05",
    "2026-03-05"
]

event_dates = pd.to_datetime(policy_events)

# ============================
# 6. EVENT STUDY
# ============================

results = []

for event in event_dates:

    idx = fx_vol.index.get_indexer([event], method="nearest")[0]

    if idx < 10 or idx + 10 >= len(fx_vol):
        continue

    vol_before = fx_vol.iloc[idx-10:idx].mean()
    vol_after = fx_vol.iloc[idx:idx+10].mean()

    curve_before = df["Curve"].iloc[idx-10:idx].mean()
    curve_after = df["Curve"].iloc[idx:idx+10].mean()

    results.append({
        "Event": fx_vol.index[idx].date(),
        "FX_Vol_Before": vol_before,
        "FX_Vol_After": vol_after,
        "Curve_Before": curve_before,
        "Curve_After": curve_after,
        "Curve_Change": curve_after - curve_before
    })

results = pd.DataFrame(results)

print("\nPolicy Event Study")
print(results)

# ============================
# 7. SUMMARY STATS
# ============================

print("\nAverage FX Vol Change:", (results["FX_Vol_After"] - results["FX_Vol_Before"]).mean())
print("Average Curve Change:", results["Curve_Change"].mean())

# ============================
# 8. FX VOL CHART
# ============================

plt.figure(figsize=(10,5))
plt.plot(fx_vol)

for e in event_dates:
    plt.axvline(e, color="red", linestyle="--")

plt.title("CNH Volatility Around Policy Events")
plt.show()

# ============================
# 9. YIELD CURVE CHART
# ============================

plt.figure(figsize=(10,5))
plt.plot(df["Curve"])

for e in event_dates:
    plt.axvline(e, color="red", linestyle="--")

plt.title("China Yield Curve (10Y - 2Y)")
plt.show()

# ============================
# 10. STATISTICAL TEST
# ============================

curve_moves = results["Curve_Change"].dropna()

mean_move = curve_moves.mean()
std_move = curve_moves.std()

t_stat = mean_move / (std_move / np.sqrt(len(curve_moves)))

prob_steepen = (curve_moves > 0).mean()

print("\nSignal Statistics")
print("Mean Curve Move:", mean_move)
print("T-Statistic:", t_stat)
print("Probability of Steepening:", prob_steepen)

#============================
# 11. EVENT-TIME CURVE REACTION
# ============================

window = 10
event_curves = []

for event in event_dates:

    if event not in df.index:
        event = df.index[df.index.get_indexer([event], method="nearest")[0]]

    idx = df.index.get_loc(event)

    if idx < window or idx + window >= len(df):
        continue

    curve_window = df["Curve"].iloc[idx-window:idx+window+1].values

    # normalize to event day
    curve_window = curve_window - curve_window[window]

    event_curves.append(curve_window)

event_curves = np.array(event_curves)

avg_curve = event_curves.mean(axis=0)

event_time = np.arange(-window, window+1)

plt.figure(figsize=(10,5))
plt.plot(event_time, avg_curve)
plt.axvline(0, linestyle="--")
plt.title("Average Curve Reaction Around Policy Events")
plt.xlabel("Days from Event")
plt.ylabel("Curve Change (10Y-2Y)")
plt.show()