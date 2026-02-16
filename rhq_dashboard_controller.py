# controllers/rhq_dashboard_controller.py

import streamlit as st
from views.rhq_dashboard_view import rhq_dashboard_view

class RHQDashboardController:

    @staticmethod
    def show(user):  # ✅ Accepts user as argument
        if not user or user["role"] != "RHQ":
            st.error("Unauthorized Access!")
            st.session_state["page"] = "login"
            st.rerun()

        rhq_dashboard_view(user)