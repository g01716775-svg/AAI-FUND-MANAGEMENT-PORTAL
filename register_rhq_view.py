# views/register_rhq_view.py
import streamlit as st # This import is correct
from controllers.auth_controller import AuthController

DEPARTMENTS = ["IT", "CNS", "ATM", "Tech", "Finance", "HR", "OPS"]

def register_rhq_view():
    st.set_page_config(page_title="Register RHQ", page_icon="📝", layout="centered")
    st.markdown("""
    <style>
    .card{background:#fff;padding:28px;border-radius:12px;box-shadow:0 8px 30px rgba(15,23,42,0.06);width:640px;margin:auto;}
    .title{color:#0b3d91;font-weight:700;text-align:center;font-size:28px;margin-bottom:6px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>Register as RHQ</div>", unsafe_allow_html=True)

    with st.form("register_rhq_form"):
        name = st.text_input("Full Name")
        designation = st.text_input("Designation")
        email = st.text_input("Official Email")
        department = st.selectbox("Department", DEPARTMENTS)
        password = st.text_input("Password", type="password")
        password2 = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Create RHQ Account")
        if submitted:
            if password != password2:
                st.error("Passwords do not match.")
            else:
                AuthController.register_rhq(name, designation, email, password, department)

    if st.button("Back"):
        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
