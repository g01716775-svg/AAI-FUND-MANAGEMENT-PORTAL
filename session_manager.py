import streamlit as st

def start_session(user: dict):
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user.get("user_id")
    st.session_state["name"] = user.get("name")
    st.session_state["email"] = user.get("email")
    st.session_state["role"] = user.get("role")
    st.session_state["department"] = user.get("department")
    st.session_state["station_id"] = user.get("station_id")
    st.session_state["station_name"] = user.get("station_name")
    st.session_state["designation"] = user.get("designation")  # <-- add this


def end_session():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

# Alias for convenience
logout = end_session

def current_user():
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        return {
            "user_id": st.session_state.get("user_id"),
            "name": st.session_state.get("name"),
            "email": st.session_state.get("email"),
            "role": st.session_state.get("role"),
            "department": st.session_state.get("department"),
            "station_id": st.session_state.get("station_id"),
            "station_name": st.session_state.get("station_name"),
            "designation": st.session_state.get("designation"),  # <-- add this
        }
    return None

