import streamlit as st
import pandas as pd # This import is correct
import decimal
from models.fund_request_model import FundRequestModel

def station_summary_view(user):
    """
    Renders the Station Summary page, showing financial details for each station.
    """
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")
    st.markdown("""
        <style>
        .st-expander {
            border: none !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
            border-radius: 12px !important;
            overflow: hidden;
            margin-bottom: 1rem;
        }
        .st-expander header {
            font-weight: 600;
            font-size: 1.25rem;
        }
        [data-testid="stSidebar"] { background-color: #0F172A; }
        .profile-card { background: #1E293B; color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center; }
        .profile-card h3 { font-size: 18px; margin: 0; }
        .profile-card p { font-size: 14px; color: #94A3B8; margin-top: 4px; }
        [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label { padding: 0.75rem 1rem; border-radius: 8px; }
        [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p { color: white !important; }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover { background-color: #2563EB; }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) { background-color: #2563EB; }
        </style>
    """, unsafe_allow_html=True)
    st.title("Station Financial Summary")
    st.markdown("---")

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.markdown(
            f"""
            <div class="profile-card">
                <h3>{user.get('name', 'User')}</h3>
                <p>{user.get('designation', 'RHQ Member')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        PAGES = {"Dashboard": "rhq_dashboard", "Pending Requests": "rhq_dashboard", "Approved Requests": "rhq_dashboard", "Add to Fund Pool": "rhq_dashboard", "Station Summary": "station_summary"}
        selection = st.radio("View", list(PAGES.keys()), index=4)
        st.divider()
        if st.button("Logout"):
            for key in ['user', 'page']: st.session_state.pop(key, None)
            st.session_state["page"] = "login"
            st.rerun()
    if PAGES[selection] != "station_summary":
        st.session_state["page"] = PAGES[selection]
        st.rerun()

    # Fetch the summary data from the model
    summary_data = FundRequestModel.get_station_summary()

    if not summary_data:
        st.warning("No station summary data available.")
        return
        
    # --- Search Bar for Stations ---
    search_term = st.text_input("Search by Station Name")
    if search_term:
        search_term = search_term.lower()
        summary_data = [
            s for s in summary_data if search_term in s.get('station_name', '').lower()
        ]

    # --- Fetch all requests to show details within each station card ---
    all_requests = FundRequestModel.get_all_requests()
    approved_requests = [
        req for req in all_requests 
        if req.get('rhq_status') in ('APPROVED', 'TOKEN_PROVIDED')
    ]
    
    # --- Group requests by station name for easy lookup ---
    requests_by_station = {}
    for req in approved_requests:
        station_name_key = req.get('station_name')
        if station_name_key not in requests_by_station:
            requests_by_station[station_name_key] = []
        requests_by_station[station_name_key].append(req)

    # --- New Colorful and Organized Layout ---
    for station in summary_data:
        station_name = station.get('station_name', 'Unknown Station')
        assigned = decimal.Decimal(station.get('assigned_amount', 0.0))
        used = decimal.Decimal(station.get('used_amount', 0.0))
        residual = decimal.Decimal(station.get('residual_amount', 0.0))

        # Use an expander for each station for better organization
        with st.expander(f"📊 {station_name}", expanded=False):
            
            # Calculate usage percentage for the progress bar
            if assigned > 0:
                used_percent = min(100, int((used / assigned) * 100))
            else:
                used_percent = 0
                
            # Display a progress bar for visual representation of usage
            st.progress(used_percent / 100, text=f"{used_percent}% of assigned funds have been used.")
            
            st.markdown("---") # Visual separator
            
            # Use columns for a clean metric layout
            col1, col2, col3 = st.columns(3)
            
            col1.metric("Assigned Amount", f"₹{assigned:,.2f}")
            col2.metric("Used Amount", f"₹{used:,.2f}")

            # Color-code the residual amount for quick insights
            residual_color = "normal" if residual > (assigned * decimal.Decimal('0.2')) else "inverse"
            col3.metric("Residual Amount", f"₹{residual:,.2f}", delta_color=residual_color)
            
            st.markdown("---")
            st.markdown("##### Approved Requests")

            station_reqs = requests_by_station.get(station_name, [])
            if not station_reqs:
                st.caption("No active approved requests for this station.")
            else:
                data = []
                for req in station_reqs:
                    # Calculate amounts for each individual request
                    req_approved = decimal.Decimal(req.get('amount_granted') or req.get('token_amount') or 0)
                    req_used = decimal.Decimal(req.get('expenditure') or 0)
                    req_remaining = req_approved - req_used

                    data.append({
                        "Request ID": req.get('request_id'),
                        "Purpose": req.get('purpose'),
                        "Approved": f"₹{req_approved:,.2f}",
                        "Used": f"₹{req_used:,.2f}",
                        "Remaining": f"₹{req_remaining:,.2f}"
                    })
                
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True, hide_index=True)


    if st.button("Refresh Data"):
        st.rerun()