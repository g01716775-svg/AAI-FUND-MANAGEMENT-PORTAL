import streamlit as st
from utils.session_manager import current_user
from models.db import add_dashboard_refresh_column

# Ensure the `dashboard_refresh` column exists before starting the app
add_dashboard_refresh_column()

def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    page = st.session_state["page"]

    if page == "login":
        from views.login_view import login_view
        login_view()
    elif page == "choose_role":
        from views.choose_role_view import choose_role_view
        choose_role_view()
    elif page == "register_rhq":
        from views.register_rhq_view import register_rhq_view
        register_rhq_view()
    elif page == "register_station":
        from views.register_station_view import register_station_view
        register_station_view()
    elif page == "rhq_dashboard":
        from controllers.rhq_dashboard_controller import RHQDashboardController
        RHQDashboardController.show(current_user())
    elif page == "station_summary":
        from views.station_summary_view import station_summary_view
        station_summary_view(current_user())
    elif page == "rhq_analytics":
        from views.rhq_analytics_view import rhq_analytics_view
        rhq_analytics_view(current_user())
    elif page == "station_dashboard":
        from controllers.station_dashboard_controller import StationDashboardController
        StationDashboardController.show()
        
    elif page == "delete_item":
        from views.delete_view import delete_view
        delete_view()

if __name__ == "__main__":
    main()