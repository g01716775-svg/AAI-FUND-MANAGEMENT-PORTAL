# views/register_station_view.py
import streamlit as st # This import is correct
from controllers.auth_controller import AuthController
from models.station_model import StationModel

DEPARTMENTS = ["IT", "CNS", "ATM", "Tech", "Finance", "HR", "OPS"]

def register_station_view():
    st.set_page_config(page_title="Register Station", page_icon="📝", layout="centered")

    stations = StationModel.get_all_stations()
    station_options = {s["station_id"]: s["station_name"] for s in stations}
    station_display = [f"{sid} - {name}" for sid, name in station_options.items()]
    
    st.markdown("<div class='title'>Register as Station Member</div>", unsafe_allow_html=True)

    with st.form("register_station_form"):
        name = st.text_input("Full Name")
        designation = st.text_input("Designation")
        email = st.text_input("Official Email")
        department = st.selectbox("Department", DEPARTMENTS)
        station_choice = st.selectbox("Select Station", ["-- Select Station --"] + station_display)
        station_id = None
        if station_choice != "-- Select Station --":
            try:
                station_id = int(station_choice.split(" - ")[0])
            except Exception:
                station_id = None

        password = st.text_input("Password", type="password")
        password2 = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Create Station Account")
        if submitted:
            if password != password2:
                st.error("Passwords do not match.")
            else:
                AuthController.register_station(name, designation, email, password, department, station_id)

    if st.button("Back"):
        st.session_state["page"] = "login"
        st.rerun()
