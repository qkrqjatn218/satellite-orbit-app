import streamlit as st
from datetime import datetime, timedelta, date, time
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from astropy.coordinates import GCRS, ITRS, EarthLocation, CartesianRepresentation, CartesianDifferential
from astropy.time import Time
from astropy import units as u
import plotly.express as px

PROPAGATION_MODELS = {
    "SGP4": "project.source.sgp4_model", 
    "Numerical (RK4)": "project.source.rk4_model",
    "Encke": "project.source.encke_model"
}

def get_tle_input():
    st.markdown("### Data load(TLE)")

    # ✅ 세션에서 불러오기 (기본값 적용)
    default_line1 = st.session_state.get("tle_line1", "")
    default_line2 = st.session_state.get("tle_line2", "")

    method = st.radio("Choose an input method", ["Enter directly", "Upload files"], index=0)

    tle_line1, tle_line2 = "", ""

    if method == "Enter directly":
        tle_line1 = st.text_input("TLE Line 1", value=default_line1, key="tle_line1_input")
        tle_line2 = st.text_input("TLE Line 2", value=default_line2, key="tle_line2_input")

    else:
        uploaded_file = st.file_uploader("TLE data file (.txt)", type=["txt"])
        if uploaded_file:
            lines = uploaded_file.read().decode("utf-8").strip().splitlines()
            if len(lines) >= 3:
                tle_line1 = lines[1].strip()
                tle_line2 = lines[2].strip()
                st.success("Finished parsing Line 1/2 in the TLE file")
            else:
                st.warning("TLE file formats are not valid.")
        else:
            tle_line1 = default_line1
            tle_line2 = default_line2

    # 결과 확인
    with st.expander("Currently applied TLE"):
        st.code(f"{tle_line1}\n{tle_line2}")

    return tle_line1, tle_line2



def get_common_simulation_settings():
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### start time (UTC)")
        start_date = st.date_input("Start Date", value=date.today())
        start_time = st.time_input("Start time", value=datetime.today())
        start_datetime = datetime.combine(start_date, start_time)

    with col2:
        st.markdown("### duration (select units)")
        unit = st.selectbox("Time units", ["sec", "min", "hr"], index=1)
        value = st.number_input(f"{unit} Enter time in units", min_value=1)

        if unit == "sec":
            duration_sec = int(value)
        elif unit == "min":
            duration_sec = int(value * 60)
        elif unit == "hr":
            duration_sec = int(value * 3600)

        delta = timedelta(seconds=duration_sec)
        h, rem = divmod(delta.seconds, 3600)
        m, s = divmod(rem, 60)
        duration_min = duration_sec / 60

    st.markdown("### Coordinate Systems and Timesteps")
    frame = st.selectbox("Coordinate system", ["TEME", "GCRS", "ITRF"])
    timestep = st.slider("Timestep (sec)", min_value=10, max_value=3600, value=60)

    # 시각적 요약
    with st.expander("simulation settings", expanded=True):
        st.write(f"**Start time**: `{start_datetime}`")
        st.write(f"**Input time**: `{value} {unit}` → `{h}h {m}m {s}s`")
        st.write(f"**Total propagation time**: `{duration_min}m`")
        st.write(f"**Coordinate system**: `{frame}`")
        st.write(f"**Timestep**: `{timestep}s`")

    return {
        "start_datetime": start_datetime,
        "duration_min": duration_min,
        "frame": frame,
        "timestep": timestep
    }

def display_results(results: list[dict]):

    if not results:
        st.error("No results.")
        return
    
    # ----------------------------
    # 데이터 테이블
    # ----------------------------
    df = pd.DataFrame(results)

    st.markdown("### output (time-series)")
    st.dataframe(df, use_container_width=True)
    
    # ----------------------------
    # CSV. download
    # ----------------------------
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="CSV. download",
        data=csv,
        file_name="orbit_prediction.csv",
        mime="text/csv"
    )
    
    col1, col2 = st.columns(2)
    # ----------------------------
    # 궤적 시각화
    # ----------------------------
    with col1:
        st.markdown("### 3D trajectory")
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(
            x=df["x_km"], y=df["y_km"], z=df["z_km"],
            mode="lines", name="Orbit", line=dict(width=2)
        ))
        fig.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode="markers", name="Earth Center",
            marker=dict(size=5, color="red")
        ))
        fig.update_layout(
            scene=dict(
                xaxis_title="X (km)",
                yaxis_title="Y (km)",
                zaxis_title="Z (km)",
                aspectmode="data"
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=700,
            title="3D Orbit in GCRS"
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("### Ground Track")
        plot_ground_track(df)

    #----------------------------
    # 궤도 좌표축 주기성
    #----------------------------    
    st.markdown("### Orbital Coordinate Axis Periodicity (x/y/z)")
    fig_xyz = go.Figure()
    for axis in ["x_km", "y_km", "z_km"]:
        fig_xyz.add_trace(go.Scatter(x=df["datetime"], y=df[axis], name=axis))
    fig_xyz.update_layout(title="Time variation of X, Y, and Z coordinates", xaxis_title="Time", yaxis_title="km")
    st.plotly_chart(fig_xyz, use_container_width=True)



    # ----------------------------
    # 속도 크기 및 고도 계산
    # ----------------------------
    st.markdown("### Velocity magnitude and altitude changes")
    position_vecs = df[["x_km", "y_km", "z_km"]].to_numpy()
    velocity_vecs = df[["vx_kms", "vy_kms", "vz_kms"]].to_numpy()

    df["speed_kms"] = np.linalg.norm(velocity_vecs, axis=1)
    df["altitude_km"] = np.linalg.norm(position_vecs, axis=1) - 6371 

    col1, col2 = st.columns(2)

    with col1:
        st.line_chart(data=df, x="datetime", y="speed_kms", use_container_width=True)
    with col2:
        st.line_chart(data=df, x="datetime", y="altitude_km", use_container_width=True)
    
    
    #----------------------------
    # x-y 평면 궤도 투영
    #----------------------------    
    st.markdown("### x-y plane trajectory projection")
    fig_xy = go.Figure()
    fig_xy.add_trace(go.Scatter(
        x=df["x_km"], y=df["y_km"], mode='lines',
        name="xy-plane"
    ))
    fig_xy.update_layout(title="Top View: X vs Y",
                         xaxis_title="X (km)", yaxis_title="Y (km)",
                         height=500)
    st.plotly_chart(fig_xy, use_container_width=True)
    
    #----------------------------
    # 고도 및 속도 변화의 주기성
    #----------------------------    
    st.markdown("### Periodicity of altitude and velocity changes")
    fig_alt = go.Figure()
    fig_alt.add_trace(go.Scatter(x=df["datetime"], y=df["altitude_km"], name="Altitude (km)"))
    fig_alt.update_layout(title="Altitude change over time", xaxis_title="Time", yaxis_title="km")

    fig_speed = go.Figure()
    fig_speed.add_trace(go.Scatter(x=df["datetime"], y=df["speed_kms"], name="Speed (km/s)"))
    fig_speed.update_layout(title="Velocity changes over time", xaxis_title="Time", yaxis_title="km/s")
    
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(fig_alt, use_container_width=True)
    with col4:
        st.plotly_chart(fig_speed, use_container_width=True)


def plot_ground_track(df):
    lat_list, lon_list = [], []

    for i, row in df.iterrows():
        t = Time(row["datetime"], scale='utc')
        r = CartesianRepresentation([row["x_km"], row["y_km"], row["z_km"]] * u.km)
        v = CartesianDifferential([row["vx_kms"], row["vy_kms"], row["vz_kms"]] * u.km / u.s)
        r_full = r.with_differentials(v)

        gcrs = GCRS(r_full, obstime=t)
        itrs = gcrs.transform_to(ITRS(obstime=t))
        
        location = EarthLocation(
            x=itrs.x.to(u.m),
            y=itrs.y.to(u.m),
            z=itrs.z.to(u.m)
        )

        lat_list.append(location.lat.deg)
        lon_list.append(location.lon.deg)

    df["lat_deg"] = lat_list
    df["lon_deg"] = lon_list

    fig = px.scatter_geo(df,
                         lat="lat_deg",
                         lon="lon_deg",
                         hover_name="datetime",
                         title="Ground Track (ITRS)",
                         projection="natural earth")

    fig.update_traces(mode="lines+markers")
    st.plotly_chart(fig, use_container_width=True)


def propagation_run():
    st.markdown("# :blue-background[Simulate satellite orbital propagation]")

    model_name = st.selectbox("Select a propagation model", ["SGP4", "Numerical (RK4)", "Encke"])
    settings = None

    if model_name == "SGP4":
        st.markdown(":orange-badge[⚠️ Needs setting] :green-badge[Simplified General Perturbations model 4]")
        tle_line1, tle_line2 = get_tle_input()
        settings = get_common_simulation_settings()
        

    elif model_name == "Numerical (RK4)":
        st.markdown(":orange-badge[⚠️ Needs setting] :gray-badge[runge-kutta 4th order]")
        settings = get_common_simulation_settings()

        # 추가 옵션 예시
        order = st.selectbox("Integral order", [2, 4], index=1)
        include_perturb = st.checkbox("Include perturbation forces", value=True)
        settings.update({"order": order, "include_perturb": include_perturb})

    elif model_name == "Encke":
        st.markdown(":orange-badge[⚠️ Needs setting] :blue-badge[Encke's Method]")
        settings = get_common_simulation_settings()

        # Encke-specific options can go here
        encke_tol = st.number_input("tolerance", min_value=1e-12, value=1e-8, format="%.1e")
        settings.update({"tolerance": encke_tol})

    # 실행
    if settings and st.button("Start propagation"):
        st.session_state.propagation_settings = {
            "model": model_name,
            "tle_line1": tle_line1,
            "tle_line2": tle_line2,
            **settings
        }
        st.success(f"Start propagating to the {model_name} model.")
        st.page_link("Report/results.py", label="View Results", icon=":material/bar_chart:")

        

def model_interface(model_name, start_datetime, frame, timestep, duration_minutes, tle_line1, tle_line2):
    import importlib.util
    import sys
    import os
    from source import OP
    
    if model_name != "SGP4":
        raise ValueError("Currently, only SGP4 models are supported.")
    
    if model_name == "SGP4":
        return OP.SGP4propagate(start_datetime, duration_minutes, timestep, tle_line1, tle_line2, frame)

    '''
    추후 업데이트
    module_path = os.path.join("")
    spec = importlib.util.spec_from_file_location("", module_path)
    sgp4_module = importlib.util.module_from_spec(spec)
    sys.modules["sgp4_op"] = sgp4_module
    spec.loader.exec_module(sgp4_module)
    '''