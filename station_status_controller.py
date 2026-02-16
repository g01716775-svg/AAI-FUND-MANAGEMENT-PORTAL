# controllers/station_status_controller.py
import streamlit as st # This import is correct
from models.fund_request_model import FundRequestModel

class StationStatusController:

    @staticmethod
    def update_status(request_id: int, new_status: str, l1_value: str = None):
        """Handles the logic for updating a fund request's station-side status."""
        if not new_status:
            st.error("You have not yet selected the stage.")
            return

        l1_decimal = None
        if new_status == "FC":
            if not l1_value:
                st.error("Please enter the L1 value for the FC stage.")
                return
            try:
                l1_decimal = float(l1_value)
            except ValueError:
                st.error("Invalid L1 value. Please enter a number.")
                return

        FundRequestModel.update_station_status(request_id, new_status, l1_decimal)
        st.success(f"Status for request {request_id} updated to '{new_status}'.")
        st.rerun()