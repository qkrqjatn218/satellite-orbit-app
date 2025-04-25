import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import os


TLE_CATEGORIES = {
    "Special-Interest Satellites": {
        "Last 30 Days' Launches": "https://celestrak.org/NORAD/elements/gp.php?GROUP=last-30-days&FORMAT=tle",
        "Space Stations": "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle",
        "100 Brightest": "https://celestrak.org/NORAD/elements/gp.php?GROUP=visual&FORMAT=tle",
        "Active Satellites": "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle",
        "Analyst Satellites": "https://celestrak.org/NORAD/elements/gp.php?GROUP=analyst&FORMAT=tle",
        "Russian ASAT Debris (COSMOS 1408)": "https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-1408-debris&FORMAT=tle",
        "Chinese ASAT Debris (FENGYUN 1C)": "https://celestrak.org/NORAD/elements/gp.php?GROUP=fengyun-1c-debris&FORMAT=tle",
        "IRIDIUM 33 Debris": "https://celestrak.org/NORAD/elements/gp.php?GROUP=iridium-33-debris&FORMAT=tle",
        "COSMOS 2251 Debris": "https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-2251-debris&FORMAT=tle"
    },

    "Weather & Earth Resources Satellites": {
        "Weather": "https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle",
        "NOAA": "https://celestrak.org/NORAD/elements/gp.php?GROUP=noaa&FORMAT=tle",
        "GOES": "https://celestrak.org/NORAD/elements/gp.php?GROUP=goes&FORMAT=tle",
        "Earth Resources": "https://celestrak.org/NORAD/elements/gp.php?GROUP=resource&FORMAT=tle",
        "Search & Rescue (SARSAT)": "https://celestrak.org/NORAD/elements/gp.php?GROUP=sarsat&FORMAT=tle",
        "Disaster Monitoring": "https://celestrak.org/NORAD/elements/gp.php?GROUP=dmc&FORMAT=tle",
        "TDRSS": "https://celestrak.org/NORAD/elements/gp.php?GROUP=tdrss&FORMAT=tle",
        "ARGOS": "https://celestrak.org/NORAD/elements/gp.php?GROUP=argos&FORMAT=tle",
        "Planet": "https://celestrak.org/NORAD/elements/gp.php?GROUP=planet&FORMAT=tle",
        "Spire": "https://celestrak.org/NORAD/elements/gp.php?GROUP=spire&FORMAT=tle"
    },

    "Communications Satellites": {
        "Active Geosynchronous": "https://celestrak.org/NORAD/elements/gp.php?GROUP=geo&FORMAT=tle",
        "GEO Protected Zone": "https://celestrak.org/NORAD/elements/gp.php?SPECIAL=gpz&FORMAT=tle",
        "GEO Protected Zone Plus": "https://celestrak.org/NORAD/elements/gp.php?SPECIAL=gpz-plus&FORMAT=tle",
        "Intelsat": "https://celestrak.org/NORAD/elements/gp.php?GROUP=intelsat&FORMAT=tle",
        "SES": "https://celestrak.org/NORAD/elements/gp.php?GROUP=ses&FORMAT=tle",
        "Eutelsat": "https://celestrak.org/NORAD/elements/gp.php?GROUP=eutelsat&FORMAT=tle",
        "Iridium": "https://celestrak.org/NORAD/elements/gp.php?GROUP=iridium&FORMAT=tle",
        "Iridium NEXT": "https://celestrak.org/NORAD/elements/gp.php?GROUP=iridium-NEXT&FORMAT=tle",
        "Starlink": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
        "OneWeb": "https://celestrak.org/NORAD/elements/gp.php?GROUP=oneweb&FORMAT=tle",
        "Orbcomm": "https://celestrak.org/NORAD/elements/gp.php?GROUP=orbcomm&FORMAT=tle",
        "Globalstar": "https://celestrak.org/NORAD/elements/gp.php?GROUP=globalstar&FORMAT=tle",
        "Swarm": "https://celestrak.org/NORAD/elements/gp.php?GROUP=swarm&FORMAT=tle",
        "Amateur Radio": "https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle",
        "SatNOGS": "https://celestrak.org/NORAD/elements/gp.php?GROUP=satnogs&FORMAT=tle",
        "Experimental Comm": "https://celestrak.org/NORAD/elements/gp.php?GROUP=x-comm&FORMAT=tle",
        "Other Comm": "https://celestrak.org/NORAD/elements/gp.php?GROUP=other-comm&FORMAT=tle",
        "Gorizont": "https://celestrak.org/NORAD/elements/gp.php?GROUP=gorizont&FORMAT=tle",
        "Raduga": "https://celestrak.org/NORAD/elements/gp.php?GROUP=raduga&FORMAT=tle",
        "Molniya": "https://celestrak.org/NORAD/elements/gp.php?GROUP=molniya&FORMAT=tle"
    },

    "Navigation Satellites": {
        "GNSS": "https://celestrak.org/NORAD/elements/gp.php?GROUP=gnss&FORMAT=tle",
        "GPS Operational": "https://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle",
        "GLONASS Operational": "https://celestrak.org/NORAD/elements/gp.php?GROUP=glo-ops&FORMAT=tle",
        "Galileo": "https://celestrak.org/NORAD/elements/gp.php?GROUP=galileo&FORMAT=tle",
        "Beidou": "https://celestrak.org/NORAD/elements/gp.php?GROUP=beidou&FORMAT=tle",
        "Satellite-Based Augmentation System": "https://celestrak.org/NORAD/elements/gp.php?GROUP=sbas&FORMAT=tle",
        "NNSS": "https://celestrak.org/NORAD/elements/gp.php?GROUP=nnss&FORMAT=tle",
        "Russian LEO Navigation": "https://celestrak.org/NORAD/elements/gp.php?GROUP=musson&FORMAT=tle"
    },

    "Scientific Satellites": {
        "Space & Earth Science": "https://celestrak.org/NORAD/elements/gp.php?GROUP=science&FORMAT=tle",
        "Geodetic": "https://celestrak.org/NORAD/elements/gp.php?GROUP=geodetic&FORMAT=tle",
        "Engineering": "https://celestrak.org/NORAD/elements/gp.php?GROUP=engineering&FORMAT=tle",
        "Education": "https://celestrak.org/NORAD/elements/gp.php?GROUP=education&FORMAT=tle"
    },

    "Miscellaneous Satellites": {
        "Miscellaneous Military": "https://celestrak.org/NORAD/elements/gp.php?GROUP=military&FORMAT=tle",
        "Radar Calibration": "https://celestrak.org/NORAD/elements/gp.php?GROUP=radar&FORMAT=tle",
        "CubeSats": "https://celestrak.org/NORAD/elements/gp.php?GROUP=cubesat&FORMAT=tle",
        "Other Satellites": "https://celestrak.org/NORAD/elements/gp.php?GROUP=other&FORMAT=tle"
    }
}


def fetch_tle(url):
    try:
        r = requests.get(url)
        lines = r.text.strip().splitlines()
        records = [(lines[i], lines[i+1], lines[i+2]) for i in range(0, len(lines), 3)]
        df = pd.DataFrame(records, columns=["Name", "TLE Line 1", "TLE Line 2"])
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# def search_run():
#     st.title("🛰 CelesTrak 위성 데이터 검색기")
#     st.markdown("위성 데이터셋을 선택하고 위성 이름으로 검색하세요.")

#     category = st.selectbox("📂 카테고리 선택", list(TLE_CATEGORIES.keys()))
#     dataset = st.selectbox("📁 데이터셋 선택", list(TLE_CATEGORIES[category].keys()))

#     if st.button("🔄 데이터 불러오기"):
#         url = TLE_CATEGORIES[category][dataset]
#         df = fetch_tle(url)
#         if df is not None:
#             st.session_state.tle_dataframe = df
#             st.success(f"`{dataset}` 데이터셋이 로드되었습니다!")

#     if "tle_dataframe" in st.session_state and st.session_state.tle_dataframe is not None:
#         search = st.text_input("🔍 위성 이름 검색")
#         df = st.session_state.tle_dataframe
#         if search:
#             df = df[df["Name"].str.contains(search, case=False, na=False)]
#         st.dataframe(df.reset_index(drop=True))

def search_run():
    st.markdown("# :blue-background[Search satellite TLE data]")
    st.caption("Select a satellite dataset and search by satellite name.")

    category = st.selectbox("Select a category", list(TLE_CATEGORIES.keys()))
    dataset = st.selectbox("Select a dataset", list(TLE_CATEGORIES[category].keys()))

    if st.button("Importing data"):
        url = TLE_CATEGORIES[category][dataset]
        df = fetch_tle(url)
        if df is not None:
            st.session_state.tle_dataframe = df
            st.badge("Success", icon=":material/check:", color="green")


    if "tle_dataframe" in st.session_state and st.session_state.tle_dataframe is not None:
        df = st.session_state.tle_dataframe

        search = st.text_input("Search for satellite names")
        if search:
            df = df[df["Name"].str.contains(search, case=False, na=False)]

        st.markdown("### Satellite list (click to select)")
        
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection("single", use_checkbox=True) 
        grid_options = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            height=500,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme="material"
        )

        selected_rows = grid_response.get("selected_rows", [])
        st.write(" Selected rows ")
        st.write(selected_rows)

        if selected_rows is not None:
            selected = selected_rows.iloc[0].to_dict()
            st.write(selected)
            
            line1 = selected.get("TLE Line 1")
            line2 = selected.get("TLE Line 2")

            st.session_state["tle_line1"] = line1
            st.session_state["tle_line2"] = line2

            st.success(f"{selected.get('Name', 'Unknown')} is selected. Go to the propagation page.")

