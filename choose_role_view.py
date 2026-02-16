# views/choose_role_view.py
import streamlit as st # This import is correct

def choose_role_view():
    st.set_page_config(page_title="Register - Choose Role", page_icon="📝", layout="centered")
    st.markdown("""
    <style>
    .card{background:#fff;padding:32px;border-radius:12px;box-shadow:0 8px 30px rgba(15,23,42,0.06);width:560px;margin:auto;}
    .title{color:#0b3d91;font-weight:700;text-align:center;font-size:28px;margin-bottom:6px;}
    .help{color:#5b6b7a;text-align:center;margin-bottom:18px;}
    .role-btn{width:200px; height:52px; border-radius:10px; font-weight:700;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'> 📝 Create an account</div>", unsafe_allow_html=True)
    st.markdown("<div class='help'>Select the role you want to register as</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1,1], gap="large")
    with col1:
        if st.button("Register as RHQ", key="reg_rhq"):
            st.session_state["register_role"] = "RHQ"
            st.session_state["page"] = "register_rhq"
            st.rerun()
    with col2:
        if st.button("Register as Station", key="reg_station"):
            st.session_state["register_role"] = "STATION"
            st.session_state["page"] = "register_station"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
