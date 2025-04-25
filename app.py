import streamlit as st
from Report import propagation as propagation_module
from Report import results as result_module
from Tool import search as search_module
import home as home_module

# st.set_page_config(layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("DEMO")
    st.subheader("LOGIN")

    username = st.text_input("username")
    password = st.text_input("password", type="password")

    if st.button("login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
        else:
            st.error("failed!")


def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()


def main_app():
    st.set_page_config(layout="wide")

    #--------------------------------------------------------------------------------------------------#
    login_page = st.Page(login, title="Log in", icon=":material/login:")
    logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
    Home = st.Page(home_module.home_run, title="Home", icon=":material/home:", default=True)
    propagation = st.Page(propagation_module.propagation_run, title="propagation", icon=":material/dashboard:")
    search = st.Page(search_module.search_run, title="Search", icon=":material/search:")
    results_page = st.Page("Report/results.py", title="Results", icon=":material/bar_chart:")
    #--------------------------------------------------------------------------------------------------#

    pg = st.navigation(
        {
            "Account": [logout_page],
            "Home" : [Home],
            "Reports": [propagation, results_page],
            "Tools": [search],
        }
    )
    pg.run()
    
    st.sidebar.title("Options")
    st.sidebar.radio("options", ["option1", "option2"])


if __name__ == "__main__":
    if st.session_state.logged_in:
        main_app()
    else:
        login()
