# controllers/station_dashboard_controller.py
import streamlit as st
from utils.session_manager import current_user
from views.station_dashboard_view import station_dashboard_view

class StationDashboardController:

    @staticmethod
    def show():
        user = current_user()
        if not user or user["role"] != "STATION":
            st.error("Unauthorized Access!")
            st.session_state["page"] = "login"
            st.rerun()

        station_dashboard_view(user)