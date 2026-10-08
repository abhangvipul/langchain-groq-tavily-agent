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
    page_title="AgentIQ",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# MODERN LIGHT THEME - UI ONLY
# ============================================================

st.markdown("""
<style>

    /* ==============================
       GLOBAL PAGE
    ============================== */

    .stApp {
        background-color: #F5F7FB;
        color: #0F172A;
    }

    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background-color: transparent;
    }


    /* ==============================
       SIDEBAR
    ============================== */

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
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


    /* ==============================
       MAIN BRAND
    ============================== */

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
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 27px;
        font-weight: 700;
        box-shadow: 0 8px 22px rgba(37, 99, 235, 0.20);
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


    /* ==============================
       STATUS BADGE
    ============================== */

    .agent-status {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background-color: #ECFDF5;
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
        background-color: #10B981;
        border-radius: 50%;
    }


    /* ==============================
       SECTION HEADINGS
    ============================== */

    .section-heading {
        font-size: 20px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 5px;
        margin-bottom: 5px;
    }

    .section-description {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 18px;
        line-height: 1.6;
    }


    /* ==============================
       TEXT AREA
    ============================== */

    div[data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 14px !important;
        color: #0F172A !important;
        font-size: 15px !important;
        padding: 16px !important;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.035);
    }

    div[data-testid="stTextArea"] textarea:hover {
        border-color: #94A3B8 !important;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.10) !important;
    }


    /* ==============================
       PRIMARY BUTTON
    ============================== */

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        color: #FFFFFF;
        border: none;
        border-radius: 12px;
        min-height: 48px;
        font-size: 15px;
        font-weight: 650;
        box-shadow: 0 7px 18px rgba(37, 99, 235, 0.18);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1D4ED8, #1E40AF);
        transform: translateY(-1px);
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.25);
    }


    /* ==============================
       SELECT BOX
    ============================== */

    div[data-baseweb="select"] > div {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
    }


    /* ==============================
       EXPANDER
    ============================== */

    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        overflow: hidden;
        margin-top: 22px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.025);
    }

    div[data-testid="stExpander"] summary {
        color: #0F172A !important;
        font-weight: 650 !important;
    }


    /* ==============================
       ALERTS
    ============================== */

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }


    /* ==============================
       ANSWER HEADER
    ============================== */

    .answer-header {
        display: flex;
        align-items: center;
        gap: 11px;
        margin-top: 30px;
        margin-bottom: 13px;
    }

    .answer-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background-color: #EFF6FF;
        color: #2563EB;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }

    .answer-title {
        font-size: 20px;
        font-weight: 700;
        color: #0F172A;
    }


    /* ==============================
       ANSWER CARD
    ============================== */

    .answer-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.035);
        color: #334155;
        font-size: 15px;
        line-height: 1.75;
    }


    /* ==============================
       TOOL BADGE
    ============================== */

    .tool-badge {
        display: inline-block;
        padding: 5px 10px;
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #DBEAFE;
        border-radius: 7px;
        font-size: 12px;
        font-weight: 650;
    }


    /* ==============================
       SIDEBAR CARDS
    ============================== */

    .sidebar-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 13px;
        margin-top: 10px;
    }

    .sidebar-card-title {
        font-size: 12px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 5px;
    }

    .sidebar-card-text {
        font-size: 11px;
        color: #64748B;
        line-height: 1.5;
    }


    /* ==============================
       TECHNOLOGY CARDS
    ============================== */

    .tech-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 17px;
        text-align: center;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.025);
    }

    .tech-name {
        font-size: 14px;
        font-weight: 700;
        color: #0F172A;
    }

    .tech-description {
        font-size: 11px;
        color: #64748B;
        margin-top: 4px;
    }


    /* ==============================
       DIVIDER
    ============================== */

    .soft-divider {
        height: 1px;
        background-color: #E2E8F0;
        margin: 24px 0;
    }


    /* ==============================
       FOOTER
    ============================== */

    .agent-footer {
        text-align: center;
        color: #94A3B8;
        font-size: 11px;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #E2E8F0;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SECURE CREDENTIAL RETRIEVAL
# ============================================================

# This pulls safely from Streamlit Cloud Secrets or local
# .streamlit/secrets.toml

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY", "")

# Sync secrets to the OS environment so LangChain tools can
# find them natively

if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

if TAVILY_API_KEY:
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY


# ============================================================
# SIDEBAR CONFIGURATION
# ============================================================

with st.sidebar:

    st.markdown("""
    <div style="
        font-size:25px;
        font-weight:750;
        color:#0F172A;
        margin-bottom:3px;
    ">
        ✦ AgentIQ
    </div>

    <div style="
        color:#64748B;
        font-size:12px;
        margin-bottom:24px;
    ">
        AI Agent Control Center
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Agent Settings")

    max_steps = st.slider(
        "Max Agent Loops",
        min_value=1,
        max_value=10,
        value=5
    )

    model_choice = st.selectbox(
        "LLM Model Core",
        [
            "openai/gpt-oss-120b",
            "llama-3.3-70b-versatile"
        ]
    )

    st.markdown(
        '<div class="soft-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown("### 🔌 Available Tools")

    st.markdown("""
    <div class="sidebar-card">

        <div class="sidebar-card-title">
            🌐 Tavily Search
        </div>

        <div class="sidebar-card-text">
            Searches the web for recent information,
            news and current events.
        </div>

    </div>

    <div class="sidebar-card">

        <div class="sidebar-card-title">
            📚 Wikipedia
        </div>

        <div class="sidebar-card-text">
            Retrieves established facts,
            definitions and background information.
        </div>

    </div>

    <div class="sidebar-card">

        <div class="sidebar-card-title">
            ➕ Arithmetic Tools
        </div>

        <div class="sidebar-card-text">
            Custom tools for addition and multiplication.
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="soft-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown("### 🔐 System Status")

    if GROQ_API_KEY and TAVILY_API_KEY:
        st.success("System Status: Fully Authenticated")
    else:
        st.error("System Status: Missing Cloud Secrets")

    st.markdown("""
    <div class="sidebar-card">

        <div class="sidebar-card-title">
            Technology Stack
        </div>

        <div class="sidebar-card-text">
            LangChain<br>
            Groq<br>
            Tavily<br>
            Wikipedia<br>
            Streamlit
        </div>

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# MAIN BRAND HEADER
# ============================================================

st.markdown("""
<div class="agent-brand">

    <div class="agent-icon">
        ✦
    </div>

    <div>

        <div class="agent-title">
            AgentIQ
        </div>

        <div class="agent-subtitle">
            Intelligent AI Agent powered by Groq + Tavily
        </div>

    </div>

</div>

<div class="agent-status">

    <span class="status-dot"></span>

    Agent Online

</div>
""", unsafe_allow_html=True)


# ============================================================
# MAIN PAGE INTRODUCTION
# ============================================================

st.markdown(
    '<div class="section-heading">Ask your AI Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-description">
        Ask questions, search the web, retrieve knowledge,
        or perform calculations using intelligent tools.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DEFINE CUSTOM TOOLS
# ============================================================

@tool
def add(a: int, b: int) -> int:
    """Add two integers and return the sum. Use this whenever asked to add numbers."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the product. Use this whenever asked to multiply numbers."""
    return a * b


# ============================================================
# AGENT RUNTIME EXECUTION LOOP
# ============================================================

def run_agent_ui(question: str, tools, tool_map, llm_with_tools):

    SYSTEM_PROMPT = """You are a helpful research assistant with access to tools.
    Rules:
    - If a question has several parts, answer EVERY part. Call one tool per part.
    - Use the add/multiply tools for arithmetic instead of calculating it yourself.
    - Use wikipedia for established facts and definitions.
    - Use tavily_search for recent news and current events.
    - Finish with a clear, well-organised answer in plain language."""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question)
    ]

    with st.expander(
        "🔍 View Agent Execution Trace Logs",
        expanded=True
    ):

        for step in range(1, max_steps + 1):

            ai_msg = llm_with_tools.invoke(messages)

            messages.append(ai_msg)

            if not ai_msg.tool_calls:

                st.success(
                    f"Step {step}: No more tools needed. "
                    f"Generating final answer..."
                )

                return ai_msg.content

            st.markdown(
                f"""
                <div style="
                    margin-top:12px;
                    margin-bottom:8px;
                    color:#0F172A;
                    font-weight:700;
                ">
                    Step {step}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.caption(
                f"Model requested "
                f"{len(ai_msg.tool_calls)} tool execution(s):"
            )

            for tool_call in ai_msg.tool_calls:

                name = tool_call["name"]

                selected_tool = tool_map.get(name)

                st.markdown(
                    f"""
                    <span class="tool-badge">
                        🔧 {name}
                    </span>
                    """,
                    unsafe_allow_html=True
                )

                st.code(
                    f"Running tool: {name}({tool_call['args']})",
                    language="python"
                )

                if selected_tool is None:

                    messages.append(
                        ToolMessage(
                            content=f"Error: no tool named '{name}'",
                            tool_call_id=tool_call["id"]
                        )
                    )

                    continue

                try:

                    # ORIGINAL CODE - UNCHANGED
                    result = selected_tool.invoke(tool_call)

                    messages.append(result)

                    st.caption(
                        "✅ Tool successfully executed."
                    )

                except Exception as e:

                    messages.append(
                        ToolMessage(
                            content=str(e),
                            tool_call_id=tool_call["id"]
                        )
                    )

                    st.error(
                        f"❌ Tool execution failed: {e}"
                    )

    return "Agent execution timed out without reaching an answer."


# ============================================================
# MAIN QUESTION INPUT
# ============================================================

user_question = st.text_area(
    "Ask the Agent a multi-part question:",
    value=(
        "What is LangChain? Also, what is 5 multiplied by 15? "
        "Summarize the recent news about AI agents."
    ),
    height=135,
    label_visibility="collapsed",
    placeholder=(
        "Ask anything... For example: "
        "What is LangChain and what are the latest developments "
        "in AI agents?"
    )
)


# ============================================================
# SUGGESTED QUESTIONS
# ============================================================

st.markdown("""
<div style="
    color:#64748B;
    font-size:12px;
    font-weight:650;
    margin-top:8px;
    margin-bottom:8px;
">
    TRY ASKING
</div>

<div style="
    display:flex;
    flex-wrap:wrap;
    gap:7px;
    margin-bottom:8px;
">

    <span style="
        background:#FFFFFF;
        border:1px solid #E2E8F0;
        color:#475569;
        border-radius:50px;
        padding:7px 12px;
        font-size:12px;
    ">
        What is LangChain?
    </span>

    <span style="
        background:#FFFFFF;
        border:1px solid #E2E8F0;
        color:#475569;
        border-radius:50px;
        padding:7px 12px;
        font-size:12px;
    ">
        Latest AI agent news
    </span>

    <span style="
        background:#FFFFFF;
        border:1px solid #E2E8F0;
        color:#475569;
        border-radius:50px;
        padding:7px 12px;
        font-size:12px;
    ">
        Calculate 25 × 40
    </span>

    <span style="
        background:#FFFFFF;
        border:1px solid #E2E8F0;
        color:#475569;
        border-radius:50px;
        padding:7px 12px;
        font-size:12px;
    ">
        Explain RAG simply
    </span>

</div>
""", unsafe_allow_html=True)


# ============================================================
# MAIN PAGE CORE PROCESS
# ============================================================

if st.button("✦  Find Answer"):

    if not GROQ_API_KEY or not TAVILY_API_KEY:

        st.error(
            "❌ Cannot run. Please add your credentials "
            "inside your Streamlit App settings dashboard."
        )

    else:

        with st.spinner(
            "Agent is reasoning and executing tools..."
        ):

            try:

                # Initialize tools dynamically

                api_wrapper = WikipediaAPIWrapper(
                    top_k_results=2,
                    doc_content_chars_max=1500
                )

                wiki_tool = WikipediaQueryRun(
                    api_wrapper=api_wrapper
                )

                tavily_tool = TavilySearch(
                    max_results=5,
                    topic="general"
                )

                tools = [
                    wiki_tool,
                    tavily_tool,
                    add,
                    multiply
                ]

                tool_map = {
                    t.name: t
                    for t in tools
                }

                # Initialize LLM

                llm = ChatGroq(
                    model=model_choice,
                    temperature=0
                )

                llm_with_tools = llm.bind_tools(tools)

                # Run core agent

                final_output = run_agent_ui(
                    user_question,
                    tools,
                    tool_map,
                    llm_with_tools
                )

                # ====================================================
                # FINAL ANSWER
                # ====================================================

                st.markdown("""
                <div class="answer-header">

                    <div class="answer-icon">
                        ✦
                    </div>

                    <div class="answer-title">
                        Final Synthesized Answer
                    </div>

                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    '<div class="answer-card">',
                    unsafe_allow_html=True
                )

                st.markdown(final_output)

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

                # ====================================================
                # TECHNOLOGY SECTION
                # ====================================================

                st.markdown("""
                <div style="
                    margin-top:30px;
                    margin-bottom:12px;
                    font-size:17px;
                    font-weight:700;
                    color:#0F172A;
                ">
                    ⚡ Agent Technology
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.markdown("""
                    <div class="tech-card">

                        <div style="
                            font-size:23px;
                            margin-bottom:6px;
                        ">
                            ⚡
                        </div>

                        <div class="tech-name">
                            Groq
                        </div>

                        <div class="tech-description">
                            LLM Engine
                        </div>

                    </div>
                    """, unsafe_allow_html=True)

                with col2:

                    st.markdown("""
                    <div class="tech-card">

                        <div style="
                            font-size:23px;
                            margin-bottom:6px;
                        ">
                            🔗
                        </div>

                        <div class="tech-name">
                            LangChain
                        </div>

                        <div class="tech-description">
                            Agent Framework
                        </div>

                    </div>
                    """, unsafe_allow_html=True)

                with col3:

                    st.markdown("""
                    <div class="tech-card">

                        <div style="
                            font-size:23px;
                            margin-bottom:6px;
                        ">
                            🌐
                        </div>

                        <div class="tech-name">
                            Tavily
                        </div>

                        <div class="tech-description">
                            Web Search
                        </div>

                    </div>
                    """, unsafe_allow_html=True)

                with col4:

                    st.markdown("""
                    <div class="tech-card">

                        <div style="
                            font-size:23px;
                            margin-bottom:6px;
                        ">
                            📚
                        </div>

                        <div class="tech-name">
                            Wikipedia
                        </div>

                        <div class="tech-description">
                            Knowledge Source
                        </div>

                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:

                st.error(
                    f"Initialization Error: {e}"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="agent-footer">
    AgentIQ · Built with Streamlit · LangChain · Groq · Tavily
</div>
""", unsafe_allow_html=True)
