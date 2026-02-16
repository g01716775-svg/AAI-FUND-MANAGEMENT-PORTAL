# views/station_dashboard_view.py
import streamlit as st
import pandas as pd
from models.fund_request_model import FundRequestModel
from utils.session_manager import logout
from controllers.station_status_controller import StationStatusController

def station_dashboard_view(user):
    """
    Displays the Station dashboard, allowing users to see their fund requests
    and delete them.
    """
    st.title(f"Station Dashboard - {user['station_name']}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"Welcome, {user['name']}")
    with col2:
        st.button("Logout", on_click=logout, use_container_width=True)

    st.header("Your Fund Requests")

    all_requests = FundRequestModel.get_all_requests()
    station_requests = [req for req in all_requests if req['station_id'] == user['station_id']]

    if not station_requests:
        st.info("You have not made any fund requests yet.")
        # Placeholder for creating a new request could go here
        return

    df = pd.DataFrame(station_requests)

    # Define the full workflow for status updates
    workflow_stages = [
        "AAES", "Bidding", "Technical Bidding Evaluation",
        "Final Bidding Evaluation", "FC", "Work Completion"
    ]

    for index, row in df.iterrows():
        st.subheader(f"Request ID: {row['request_id']} - {row['purpose']}")
        cols = st.columns([3, 1])
        with cols[0]:
            st.text(f"Status: {row['rhq_status'] or 'PENDING'}")
            st.text(f"Amount Requested: {row['amount_requested']}")
            st.text(f"Amount Granted: {row['amount_granted'] or 0.0}")
        with cols[1]:
            if st.button("Delete", key=f"delete_station_req_{row['request_id']}", use_container_width=True):
                st.session_state["previous_page"] = "station_dashboard"
                st.session_state["delete_info"] = {"type": "fund_request", "id": row['request_id']}
                st.session_state["page"] = "delete_item"
                st.rerun()

        # --- Status Update Workflow for Approved Requests ---
        if row['rhq_status'] in ('APPROVED', 'TOKEN_PROVIDED'):
            st.markdown("---")
            st.write("**Update Work Progress**")

            current_status = row.get('station_status')
            current_index = workflow_stages.index(current_status) if current_status in workflow_stages else -1
            available_stages = workflow_stages[current_index + 1:]

            if current_status == "Work Completion":
                st.success("Work progress is marked as complete.")
            else:
                form_key = f"status_form_{row['request_id']}"
                with st.form(key=form_key):
                    col1, col2 = st.columns(2)
                    with col1:
                        # The selectbox should show all remaining stages
                        new_status = st.selectbox(
                            "Select Next Stage", 
                            options=[""] + available_stages, 
                            key=f"status_{row['request_id']}"
                        )

                    l1_value = None
                    if new_status == "FC":
                        with col2:
                            l1_value = st.text_input("Enter L1 Value", key=f"l1_{row['request_id']}")

                    if st.form_submit_button("Update Status"):
                        StationStatusController.update_status(row['request_id'], new_status, l1_value)

        st.divider()