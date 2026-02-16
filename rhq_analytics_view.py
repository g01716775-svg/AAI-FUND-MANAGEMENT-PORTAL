# views/rhq_analytics_view.py

import streamlit as st # This import is correct
import pandas as pd
import plotly.graph_objects as go
from models.fund_request_model import FundRequestModel
from decimal import Decimal

def rhq_analytics_view(user):
    """
    Displays the RHQ Analytics Dashboard with charts.
    """
    st.set_page_config(layout="wide")
    st.title("📊 RHQ Analytics Dashboard")
    st.write("Visual summary of fund allocation, station performance, and request statuses.")

    if st.button("⬅️ Back to Main Dashboard"):
        st.session_state["page"] = "rhq_dashboard"
        st.rerun()

    st.divider()

    # --- Fetch Data ---
    try:
        total_pool = FundRequestModel.get_pool()
        total_approved = FundRequestModel.get_total_approved_funds()
        station_summary = FundRequestModel.get_station_summary()
        status_summary = FundRequestModel.get_request_status_summary()
    except Exception as e:
        st.error(f"Failed to load dashboard data: {e}")
        return

    # Ensure consistent types for calculation to prevent TypeErrors
    dec_total_pool = Decimal(total_pool or 0)
    dec_total_approved = Decimal(total_approved or 0)
    remaining_pool = dec_total_pool - dec_total_approved

    # --- Create Charts ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Fund Pool Overview")
        if total_pool > 0:
            fig_pool = go.Figure(data=[go.Bar(
                x=["Remaining in Pool", "Total Approved"],
                y=[remaining_pool, dec_total_approved],
                marker_color=['#28a745', '#ffc107'],
                text=[f"₹{v:,.2f}" for v in [remaining_pool, dec_total_approved]],
                textposition='auto'
            )])
            fig_pool.update_layout(showlegend=False, yaxis_title="Amount (₹)")
            st.plotly_chart(fig_pool, use_container_width=True)
        else:
            st.info("Fund pool is currently empty.")

    with col2:
        st.subheader("Request Status Summary")
        if status_summary:
            fig_status = go.Figure(data=[go.Pie(
                labels=[s['rhq_status'] for s in status_summary],
                values=[s['status_count'] for s in status_summary],
                marker_colors=['#007bff', '#6c757d', '#28a745', '#dc3545', '#ffc107']
            )])
            fig_status.update_layout(legend_title_text='Status')
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No requests with statuses found.")

    st.divider()

    # --- Station Performance Bar Chart ---
    st.subheader("Fund Allocation by Station")
    if station_summary:
        # Convert to DataFrame for easier plotting
        df_station = pd.DataFrame(station_summary)
        df_station.set_index('station_name', inplace=True)

        # Prepare data for stacked bar chart if needed, or side-by-side
        chart_data = df_station[['assigned_amount', 'used_amount']].copy()
        chart_data.rename(columns={
            'assigned_amount': 'Amount Assigned',
            'used_amount': 'Amount Used'
        }, inplace=True)

        st.bar_chart(chart_data, use_container_width=True)

        with st.expander("View Raw Data"):
            st.dataframe(df_station.style.format({
                "assigned_amount": "₹{:,.2f}",
                "used_amount": "₹{:,.2f}",
                "residual_amount": "₹{:,.2f}"
            }), use_container_width=True)
    else:
        st.info("No station data available to display.")

    # --- Cleanup ---
    # The files from the previous attempt are no longer needed.
    # You can safely delete the following files:
    # - controllers/dashboard_data_controller.py
    # - templates/dashboards/rhq_dashboard.html (or controllers/rhq_dashboard.html)