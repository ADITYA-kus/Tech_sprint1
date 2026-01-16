import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests

# 1. SETTINGS & STYLING
st.set_page_config(page_title="Energy Shield: Governance AI", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - PARAMETER CONTROL
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092040.png", width=80)
    st.title("Admin Console")
    st.info("Adjust parameters to simulate energy theft scenarios.")
    
    # Input Sliders (Matching your 15 features)
    acorn = st.selectbox("Social Class (Governance Layer)", ["Affluent", "Comfortable", "Adversity"])
    u_sum = st.slider("Total Daily Usage (kWh)", 0.0, 50.0, 5.0)
    u_std = st.slider("Usage Variance (Flatness)", 0.0, 5.0, 0.2)
    u_temp = st.slider("Outside Temperature (°C)", -5, 30, 2)
    u_max = u_sum * 0.4 # Proxy for daily_max
    u_min = u_sum * 0.05 # Proxy for energy_min
    u_med = u_sum / 24 # Proxy for energy_median

# 3. HEADER - GLOBAL IMPACT (Zone A)
st.title("🛡️ Energy Shield AI: Forensic Governance Dashboard")
m1, m2 = st.columns(2)
m1.metric("Total Profiles Analyzed", "3.47M", "Ready")
m2.metric("Theft Detection Rate", "3.01%", "-0.2%")
# m3.metric("Revenue Protection", "£1.2M", "Target")
# m4.metric("Governance Equity", "High", "Verified")

# 4. MAIN INTERFACE
if st.button("🚀 RUN FORENSIC INSPECTION"):
    # Call FastAPI
    payload = {
        "energy_sum": u_sum, "energy_std": u_std, "energy_max": u_max,
        "energy_min": u_min, "energy_median": u_med, "acorn_grouped": acorn,
        "temp_min": u_temp, "temp_max": u_temp + 5
    }
    
    # Assuming FastAPI is running at port 8000
    try:
        res = requests.post("http://127.0.0.1:8000/inspect", json=payload).json()
        
        # --- ZONE B: DEEP-DIVE FORENSIC ---
        col_left, col_right = st.columns([1.5, 1])
        
        with col_left:
            st.subheader("🕵️ Behavioral Signature Analysis")
            # Weather Sensitivity Heatmap
            # Creating a localized heatmap showing where this user sits vs normal
            heat_data = pd.DataFrame({
                'Temp': [u_temp], 'Usage': [u_sum], 'Risk': [res['risk_score']]
            })
            fig_heat = px.density_heatmap(heat_data, x="Temp", y="Usage", 
                                         color_continuous_scale="Reds" if res['status']=="Suspicious" else "Greens",
                                         range_x=[-5, 30], range_y=[0, 50],
                                         title="Environmental Sensitivity Mapping")
            st.plotly_chart(fig_heat, use_container_width=True)

        with col_right:
            st.subheader("🎯 Risk Verdict")
            color = "red" if res['status'] == "Suspicious" else "green"
            st.markdown(f"<h1 style='text-align: center; color: {color};'>{res['status']}</h1>", unsafe_allow_html=True)
            
            # Gauge Chart
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = res['risk_score'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Confidence Score"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': color}}
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)

        # --- ZONE C: EXPLAINABLE AI (XAI) ---
        st.divider()
        st.subheader("📋 Explainable AI (XAI): Evidence Table")
        
        # Table showing why the decision was made using your 15 features
        evidence = {
            "Feature Indicator": ["Peer Ratio", "Flatness Index", "Peak Intensity", "Weather Response"],
            "Measured Value": [f"{res['peer_ratio']}x", f"{1/(u_std+0.01):.2f}", f"{(u_max/(u_sum/24+0.1)):.2f}", f"{u_temp}°C"],
            "Threshold Check": ["< 0.3x" if res['peer_ratio'] < 0.3 else "Normal", 
                                "> 10.0" if u_std < 0.1 else "Normal",
                                "Low" if u_max < 1.0 else "Normal",
                                "Anomaly" if (u_temp < 5 and u_sum < 2) else "Normal"],
            "Status": ["🚩 Fail" if res['peer_ratio'] < 0.3 else "✅ Pass",
                       "🚩 Fail" if u_std < 0.1 else "✅ Pass",
                       "✅ Pass", "🚩 Fail" if (u_temp < 5 and u_sum < 2) else "✅ Pass"]
        }
        st.table(pd.DataFrame(evidence))
        st.info(f"**AI Reasoning:** {res['analysis']}")
        
    except Exception as e:
        st.error(f"API Connection Failed: {e}. Ensure FastAPI is running on port 8000.")

    