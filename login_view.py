# views/login_view.py
import streamlit as st # This import is correct
from controllers.auth_controller import AuthController

def login_view():
    st.set_page_config(page_title="AAI Fund Management Portal - Login", page_icon="🛫", layout="centered")
    st.markdown("""
    <style>
    .page-bg { background:#f4f6f9; padding:40px 0; }
    .card{background:#fff;padding:28px;border-radius:12px;box-shadow:0 8px 30px rgba(15,23,42,0.08);width:520px;margin:auto;}
    .title{color:#0b3d91;font-weight:700;text-align:center;font-size:34px;margin-bottom:6px;}
    .subtitle{ color:#5b6b7a;text-align:center;margin-bottom:18px;}
    input { border-radius: 8px !important; }
    .stButton>button { border-radius:10px !important; height:44px; font-weight:700;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='title'>🛫 AAI Fund Management Portal - Login</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Secure access for RHQ & Station members</div>", unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Official Email", placeholder="Enter your official mail")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Login")
        if submitted:
            AuthController.login(email, password)

    st.markdown("<hr/>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Register"):
            st.session_state["page"] = "choose_role"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
