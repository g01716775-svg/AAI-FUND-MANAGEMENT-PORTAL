# views/rhq_dashboard_view.py
import streamlit as st
import pandas as pd
from models.fund_request_model import FundRequestModel
from utils.session_manager import current_user, logout

def rhq_dashboard_view(user):
    """
    Displays the RHQ dashboard, including fund requests with delete functionality.
    """
    st.title(f"RHQ Dashboard - Welcome, {user['name']}")

    col1, col2 = st.columns([3, 1])
    with col2:
        st.button("Logout", on_click=logout, use_container_width=True)

    st.sidebar.title("Navigation")
    if st.sidebar.button("Dashboard", use_container_width=True):
        st.session_state["page"] = "rhq_dashboard"
        st.rerun()
    if st.sidebar.button("Manage Stations", use_container_width=True):
        st.session_state["page"] = "station_summary"
        st.rerun()
    if st.sidebar.button("Analytics", use_container_width=True):
        st.session_state["page"] = "rhq_analytics"
        st.rerun()

    st.header("All Fund Requests")

    requests = FundRequestModel.get_fund_requests_for_rhq(user)

    if not requests:
        st.info("No fund requests found.")
        return

    df = pd.DataFrame(requests)
    # Add a placeholder for the delete button column
    df["delete_action"] = ""
    
    # Display data in a more structured way
    for index, row in df.iterrows():
        st.subheader(f"Request ID: {row['request_id']} - {row['purpose']}")
        cols = st.columns([3, 1])
        with cols[0]:
            st.text(f"Station: {row['station_name']}")
            st.text(f"Status: {row['rhq_status']}")
            st.text(f"Station Progress: {row.get('station_status') or 'Not Started'}") # This line displays the progress
            st.text(f"Amount Requested: {row['amount_requested']}")
        with cols[1]:
            if st.button("Delete", key=f"delete_{row['request_id']}", use_container_width=True):
                st.session_state["previous_page"] = "rhq_dashboard"
                st.session_state["delete_info"] = {"type": "fund_request", "id": row['request_id']}
                st.session_state["page"] = "delete_item"
                st.rerun()
        st.divider()