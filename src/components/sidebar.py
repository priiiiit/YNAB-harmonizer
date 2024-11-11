import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.title("Navigation")
        
        # Add description
        st.markdown("""
        ### Available Tools
        - **Home**: Import transactions
        - **Transaction Matcher**: Compare transactions between sources
        """) 