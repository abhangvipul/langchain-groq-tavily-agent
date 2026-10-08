import os
import streamlit as st
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage


# ============================================================
# STREAMLIT UI CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AgentIQ | AI Agent",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# MODERN LIGHT THEME - UI ONLY
# ============================================================

st.markdown("""
<style>

    /* ========================================================
       GLOBAL PAGE
    ======================================================== */

    .stApp {
        background: #F5F7FB;
        color: #0F172A;
    }

    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ========================================================
       SIDEBAR
    ======================================================== */

    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0F172A;
    }

    section[data-testid="stSidebar"] label {
        color: #475569 !important;
        font-weight: 600 !important;
    }

    /* ========================================================
       BRAND HEADER
    ======================================================== */

    .agent-brand {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 8px;
    }

    .agent-icon {
        width: 52px;
        height: 52px;
        border-radius: 15px;

        background: linear-gradient(
            135deg,
            #2563EB,
            #1D4ED8
        );

        color: #FFFFFF;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 27px;
        font-weight: 700;

        box-shadow:
            0 8px 22px rgba(37, 99, 235, 0.20);
    }

    .agent-title {
        font-size: 32px;
        font-weight: 750;
        color: #0F172A;
        letter-spacing: -1px;
        line-height: 1.1;
    }

    .agent-subtitle {
        color: #64748B;
        font-size: 14px;
        margin-top: 5px;
    }

    /* ========================================================
       STATUS BADGE
    ======================================================== */

    .agent-status {
        display: inline-flex;
        align-items: center;
        gap: 7px;

        background: #ECFDF5;
        color: #047857;

        border: 1px solid #A7F3D0;

        border-radius: 50px;

        padding: 6px 12px;

        font-size: 12px;
        font-weight: 650;

        margin-top: 14px;
        margin-bottom: 27px;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        background: #10B981;
        border-radius: 50%;
    }

    /* ========================================================
       SECTION HEADINGS
    =================
