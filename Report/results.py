import streamlit as st
from Report.propagation import model_interface, display_results
import time

def result_run():
    st.markdown("# :blue-background[Orbit Propagation Results]")

    if "propagation_settings" not in st.session_state:
        st.warning("No simulation settings found.")
        return

    settings = st.session_state.propagation_settings

    with st.spinner("Running propagation..."):
        start_time = time.time()

        result = model_interface(
            model_name=settings["model"],
            start_datetime=settings["start_datetime"],
            frame=settings["frame"],
            timestep=settings["timestep"],
            duration_minutes=settings["duration_min"],
            tle_line1=settings["tle_line1"],
            tle_line2=settings["tle_line2"]
        )

        duration = time.time() - start_time
        st.success(f"✅ Propagation completed in `{duration:.2f}` seconds")

    display_results(result)

result_run()