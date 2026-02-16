# controllers/dashboard_data_controller.py

from flask import jsonify
from models.fund_request_model import FundRequestModel

class DashboardDataController:

    @staticmethod
    def get_rhq_summary():
        """
        Provides data for the RHQ dashboard charts.
        """
        try:
            # Data for Pool vs. Approved Funds Donut Chart
            total_pool = FundRequestModel.get_pool()
            total_approved = FundRequestModel.get_total_approved_funds()
            remaining_pool = total_pool - total_approved

            # Data for Station Performance Bar Chart
            station_summary = FundRequestModel.get_station_summary()

            # Data for Request Status Pie Chart
            status_summary = FundRequestModel.get_request_status_summary()

            response = {
                "pool_summary": {
                    "labels": ["Remaining in Pool", "Total Approved"],
                    "data": [float(remaining_pool), float(total_approved)]
                },
                "station_summary": {
                    "labels": [s['station_name'] for s in station_summary],
                    "assigned_data": [float(s['assigned_amount']) for s in station_summary],
                    "used_data": [float(s['used_amount']) for s in station_summary]
                },
                "status_summary": {
                    "labels": [s['rhq_status'] for s in status_summary],
                    "data": [s['status_count'] for s in status_summary]
                }
            }
            return jsonify(response)
        except Exception as e:
            return jsonify({"error": str(e)}), 500