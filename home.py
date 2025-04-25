import streamlit as st

def home_run():
    st.markdown("# :blue-background[HOME SWEET HOME]")
    st.caption("Simulate and visualize satellite orbits with various propagation models based on data.")

    st.markdown("ℹ️ Technical Info & Credits")
    st.markdown("""
                - 📡 TLE Data Source: [CelesTrak](https://celestrak.org/)
                - 📦 Core Libraries: `numpy`, `pandas`, `plotly`, `astropy`, `streamlit`
                - 🚀 Functionality: Satellite orbit propagation using SGP4 and numerical models (RK4, Encke, etc.)
                - 📈 Features: 3D orbit visualization, Ground Track mapping, altitude & velocity analysis, periodicity detection
                - 🧠 Developer: Beomsu Park
                - 🛠️ GitHub Repository: [github.com/qkrqjatn218](https://github.com/qkrqjatn218)
                """)
    
    st.image("image/image.jpg", caption="Earth view from space. Image by NASA.")

