# controllers/auth_controller.py
import streamlit as st # This import is correct
from models.user_model import UserModel
from models.station_model import StationModel
from utils.password_hash import hash_password, verify_password
from utils.session_manager import start_session

class AuthController:

    @staticmethod
    def login(email: str, password: str):
        if not email or not password:
            st.error("Please enter both email and password.")
            return

        user = UserModel.get_user_by_email(email.strip().lower())
        if not user:
            st.error("User not found.")
            return

        if not verify_password(password, user["password_hash"]):
            st.error("Incorrect password.")
            return

        start_session(user)
        st.success(f"Welcome, {user['name']} ({user['role']})")
        # route
        if user["role"] == "RHQ":
            st.session_state["page"] = "rhq_dashboard"
        else:
            st.session_state["page"] = "station_dashboard"
        st.rerun()

    @staticmethod
    def register_rhq(name: str, designation: str, email: str, password: str, department: str):
        # validation
        if not all([name, designation, email, password, department]):
            st.error("Please fill all mandatory fields.")
            return

        email = email.strip().lower()
        if UserModel.get_user_by_email(email):
            st.error("Email already registered.")
            return

        try:
            pwd_hash = hash_password(password)
            UserModel.create_user(
                name=name.strip(),
                designation=designation.strip(),
                email=email,
                password_hash=pwd_hash,
                role="RHQ",
                department=department,
                station_id=None,
                station_name=None
            )
            st.success("RHQ registration successful. Please login.")
            st.session_state["page"] = "login"
            st.rerun()
        except Exception as e:
            st.error(f"Registration failed: {e}")

    @staticmethod
    def register_station(name: str, designation: str, email: str, password: str, department: str, station_id: int):
        # validation
        if not all([name, designation, email, password, department, station_id]):
            st.error("Please fill all mandatory fields.")
            return

        email = email.strip().lower()
        if UserModel.get_user_by_email(email):
            st.error("Email already registered.")
            return

        # validate station exists
        stations = StationModel.get_all_stations()
        station_map = {s["station_id"]: s["station_name"] for s in stations}
        if station_id not in station_map:
            st.error("Selected station does not exist.")
            return

        try:
            pwd_hash = hash_password(password)
            UserModel.create_user(
                name=name.strip(),
                designation=designation.strip(),
                email=email,
                password_hash=pwd_hash,
                role="STATION",
                department=department,
                station_id=station_id,
                station_name=station_map[station_id]
            )
            st.success("Station user registration successful. Please login.")
            st.session_state["page"] = "login"
            st.rerun()
        except Exception as e:
            st.error(f"Registration failed: {e}")
