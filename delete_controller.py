# controllers/delete_controller.py
import streamlit as st # This import is correct
from models.fund_request_model import FundRequestModel
from models.station_model import StationModel

class DeleteController:

    @staticmethod
    def delete_fund_request(request_id: int):
        """Handles the deletion of a fund request."""
        try:
            if FundRequestModel.delete_request(request_id):
                st.success(f"Successfully deleted fund request ID: {request_id}")
            else:
                st.warning("Could not delete fund request. It may have already been removed.")
        except Exception as e:
            st.error(f"An error occurred while deleting the fund request: {e}")

    @staticmethod
    def delete_station(station_id: int):
        """Handles the deletion of a station."""
        try:
            StationModel.delete_station(station_id)
            st.success(f"Successfully deleted station.")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An error occurred while deleting the station: {e}")