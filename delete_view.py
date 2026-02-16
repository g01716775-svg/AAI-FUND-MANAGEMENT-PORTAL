# views/delete_view.py
import streamlit as st # This import is correct
from controllers.delete_controller import DeleteController

def delete_view():
    """
    A transient view to handle deletion actions based on session state
    and then redirect back.
    """
    delete_info = st.session_state.get("delete_info")
    previous_page = st.session_state.get("previous_page", "login")

    if not delete_info:
        st.warning("No item selected for deletion.")
        st.session_state["page"] = previous_page
        st.rerun()
        return

    item_type = delete_info.get("type")
    item_id = delete_info.get("id")

    # Clear the delete info to prevent re-deletion on rerun
    if "delete_info" in st.session_state:
        del st.session_state["delete_info"]

    if item_type == "fund_request":
        DeleteController.delete_fund_request(item_id)
    elif item_type == "station":
        DeleteController.delete_station(item_id)

    # Redirect back to the previous page
    st.session_state["page"] = previous_page
    st.rerun()