import streamlit as st
import yaml
from yaml.loader import SafeLoader


def logout():
    """Log out the current user."""
    st.session_state['authentication_status'] = None
    st.rerun()
