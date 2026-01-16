
import warnings
from sklearn.exceptions import InconsistentVersionWarning

# This hides the version mismatch warning from the console
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np

app = FastAPI()

# 1. LOAD ASSETS
try:
    with open("isolation_forest_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("group_averages.pkl", "rb") as f:
        group_averages = pickle.load(f)
    print("✅ System Ready: Model & Peer Averages Loaded")
except Exception as e:
    print(f"❌ Error: {e}")

# 2. DATA SCHEMA (What the UI sends)
class HouseholdInput(BaseModel):
    energy_sum: float
    energy_std: float
    energy_max: float
    energy_min: float
    energy_median: float
    acorn_grouped: str
    temp_min: float
    temp_max: float

@app.post("/inspect")
async def inspect_household(data: HouseholdInput):
    # 1. PRE-CALCULATIONS (Recreating your features)
    peer_avg = group_averages.get(data.acorn_grouped, 5.0)
    peer_ratio = data.energy_sum / (peer_avg + 1e-6)
    flatness = 1 / (data.energy_std + 0.01)
    energy_mean = data.energy_sum / 24
    peak_intensity = data.energy_max / (energy_mean + 0.01)
    temp_gap = data.temp_max - data.temp_min

    # 2. THE ULTIMATE FEATURE LIST (Must match your 15 features EXACTLY)
    # The order below is the order from your training code:
    final_features = [
        data.energy_std,      # 1. daily_std (using energy_std as proxy)
        data.energy_sum,      # 2. daily_sum
        data.energy_max,      # 3. daily_max
        data.temp_min,        # 4. temperatureMin
        data.temp_max,        # 5. temperatureMax
        temp_gap,             # 6. temp_gap
        energy_mean,          # 7. energy_mean
        data.energy_max,      # 8. energy_max
        data.energy_std,      # 9. energy_std
        data.energy_min,      # 10. energy_min
        data.energy_sum,      # 11. energy_sum
        data.energy_median,   # 12. energy_median
        peer_ratio,           # 13. peer_ratio
        flatness,             # 14. flatness_index
        peak_intensity        # 15. peak_intensity
    ]

    # 3. CREATE DATAFRAME WITH CORRECT COLUMN NAMES
    # This prevents the "Feature names unseen at fit time" error
    feature_names = [
    'daily_std', 'daily_sum', 'daily_max',
    'temperatureMin', 'temperatureMax', 'temp_gap',
    'energy_mean', 'energy_max', 'energy_std',
    'energy_min', 'energy_sum', 'energy_median',
    'peer_ratio', 'flatness_index', 'peak_intensity'
]
    
    input_df = pd.DataFrame([final_features], columns=feature_names)

    # 4. PREDICT (Using 'loaded_model' or 'model' depending on your variable name)
    prediction = model.predict(input_df)
    status = "Suspicious" if prediction[0] == -1 else "Normal"
    
    return {
        "status": status,
        "risk_score": 85 if status == "Suspicious" else 15,
        "peer_ratio": round(peer_ratio, 2),
        "analysis": "Anomaly detected based on 15-point behavioral check." if status == "Suspicious" else "Normal behavior."
    }