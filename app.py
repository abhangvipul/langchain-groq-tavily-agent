import os
import streamlit as st

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AgentIQ | AI Research Agent",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS — MODERN LIGHT THEME
# ============================================================

st.markdown("""
<style>

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    .stApp {
        background: #F8FAFC;
    }

    .main .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    /* --------------------------------------------------------
       REMOVE DEFAULT STREAMLIT ELEMENTS
    -------------------------------------------------------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0F172A;
    }

    /* --------------------------------------------------------
       BRAND HEADER
    -------------------------------------------------------- */

    .brand-container {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 10px;
    }

    .brand-icon {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: #2563EB;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 25px;
        font-weight: 700;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.18);
    }

    .brand-title {
        font-size: 32px;
        font-weight: 750;
        letter-spacing: -1px;
        color: #0F172A;
        line-height: 1.1;
    }

    .brand-subtitle {
        color: #64748B;
        font-size: 15px;
        margin-top: 4px;
    }

    /* --------------------------------------------------------
       STATUS BADGE
    -------------------------------------------------------- */

    .status-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 18px;
        margin-bottom: 30px;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 6px 12px;
        border-radius: 999px;
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #047857;
        font-size: 12px;
        font-weight: 650;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        background: #10B981;
        border-radius: 50%;
    }

    /* --------------------------------------------------------
       HERO
    -------------------------------------------------------- */

    .hero-title {
        font-size: 19px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 5px;
    }

    .hero-description {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 18px;
    }

    /* --------------------------------------------------------
       QUERY CARD
    -------------------------------------------------------- */

    .query-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
    }

    /* Text area */

    div[data-testid="stTextArea"] textarea {
        background: #F8FAFC !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        color: #0F172A !important;
        font-size: 15px !important;
        padding: 15px !important;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border: 1px solid #2563EB !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.10) !important;
    }

    /* --------------------------------------------------------
       BUTTON
    -------------------------------------------------------- */

    .stButton > button {
        width: 100%;
        background: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 11px;
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 650;
        transition: all 0.2s ease;
        min-height: 46px;
    }

    .stButton > button:hover {
        background: #1D4ED8;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.20);
        transform: translateY(-1px);
    }

    /* --------------------------------------------------------
       SUGGESTED QUESTIONS
    -------------------------------------------------------- */

    .suggestion-title {
        font-size: 12px;
        font-weight: 650;
        color: #64748B;
        margin-top: 10px;
        margin-bottom: 8px;
    }

    .suggestion {
        display: inline-block;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        color: #475569;
        border-radius: 999px;
        padding: 7px 12px;
        margin-right: 6px;
        margin-bottom: 5px;
        font-size: 12px;
    }

    /* --------------------------------------------------------
       SECTION TITLES
    -------------------------------------------------------- */

    .section-title {
        display: flex;
        align-items: center;
        gap: 9px;
        font-size: 17px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 28px;
        margin-bottom: 12px;
    }

    /* --------------------------------------------------------
       ANSWER CARD
    -------------------------------------------------------- */

    .answer-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
        margin-bottom: 18px;
    }

    .answer-label {
        color: #2563EB;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 12px;
    }

    /* --------------------------------------------------------
       TRACE CARD
    -------------------------------------------------------- */

    .trace-header {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 14px 17px;
        color: #0F172A;
        font-weight: 650;
    }

    /* --------------------------------------------------------
       TOOL BADGE
    -------------------------------------------------------- */

    .tool-badge {
        display: inline-block;
        padding: 5px 10px;
        background: #EFF6FF;
        color: #1D4ED8;
        border-radius: 7px;
        font-size: 12px;
        font-weight: 650;
    }

    /* --------------------------------------------------------
       INFO CARDS
    -------------------------------------------------------- */

    .info-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
    }

    .info-number {
        font-size: 22px;
        font-weight: 750;
        color: #0F172A;
    }

    .info-label {
        color: #64748B;
        font-size: 11px;
        margin-top: 3px;
    }

    /* --------------------------------------------------------
       SIDEBAR CARDS
    -------------------------------------------------------- */

    .sidebar-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px;
        margin-top: 12px;
    }

    .sidebar-card-title {
        font-size: 12px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 7px;
    }

    .sidebar-card-text {
        font-size: 11px;
        color: #64748B;
        line-height: 1.5;
    }

    /* --------------------------------------------------------
       DIVIDER
    -------------------------------------------------------- */

    .soft-divider {
        height: 1px;
        background: #E2E8F0;
        margin: 25px 0;
    }

    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .footer {
        text-align: center;
        color: #94A3B8;
        font-size: 11px;
        margin-top: 40px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SECURE CREDENTIAL RETRIEVAL
# ============================================================

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY", "")

if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

if TAVILY_API_KEY:
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div style="
        font-size:24px;
        font-weight:750;
        color:#0F172A;
        margin-bottom:4px;
    ">
        ✦ AgentIQ
    </div>

    <div style="
        color:#64748B;
        font-size:12px;
        margin-bottom:22px;
    ">
        AI Research Agent
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Agent Settings")

    max_steps = st.slider(
        "Maximum Agent Steps",
        min_value=1,
        max_value=10,
        value=5
    )

    model_choice = st.selectbox(
        "AI Model",
        [
            "openai/gpt-oss-120b",
            "llama-3.3-70b-versatile"
        ]
    )

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 🔌 Available Tools")

    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-card-title">🌐 Tavily Search</div>
        <div class="sidebar-card-text">
            Searches the web for recent information,
            news and current events.
        </div>
    </div>

    <div class="sidebar-card">
        <div class="sidebar-card-title">📚 Wikipedia</div>
        <div class="sidebar-card-text">
            Retrieves established facts,
            definitions and background information.
        </div>
    </div>

    <div class="sidebar-card">
        <div class="sidebar-card-title">➕ Arithmetic</div>
        <div class="sidebar-card-text">
            Custom tools for addition and multiplication.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 🔐 System Status")

    if GROQ_API_KEY and TAVILY_API_KEY:
        st.success("System Ready")
    else:
        st.error("Missing API Secrets")

    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-card-title">Technology Stack</div>
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
# MAIN HEADER
# ============================================================

st.markdown("""
<div class="brand-container">

    <div class="brand-icon">
        ✦
    </div>

    <div>
        <div class="brand-title">
            AgentIQ
        </div>

        <div class="brand-subtitle">
            AI Research Agent powered by Groq + Tavily
        </div>
    </div>

</div>

<div class="status-row">
    <div class="status-badge">
        <span class="status-dot"></span>
        Agent Online
    </div>

    <div style="
        color:#94A3B8;
        font-size:12px;
    ">
        Think • Reason • Act
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# HERO SECTION
# ============================================================

st.markdown("""
<div class="hero-title">
    Ask your AI research assistant
</div>

<div class="hero-description">
    Ask questions, search the web, retrieve knowledge and perform
    calculations using intelligent tool selection.
</div>
""", unsafe_allow_html=True)


# ============================================================
# CUSTOM TOOLS
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
# AGENT EXECUTION FUNCTION
# ============================================================

def run_agent_ui(question: str, tools, tool_map, llm_with_tools):

    SYSTEM_PROMPT = """
    You are a helpful AI research assistant with access to multiple tools.

    Rules:

    - If a question has several parts, answer EVERY part.
    - Call appropriate tools for each part.
    - Use add/multiply tools for arithmetic instead of calculating yourself.
    - Use Wikipedia for established facts and definitions.
    - Use Tavily Search for recent news, current events and web information.
    - Do not use Tavily unnecessarily for simple established facts.
    - Finish with a clear, well-organised answer in plain language.
    - Use headings and bullet points when useful.
    """

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question)
    ]

    # Trace container
    with st.expander(
        "🔍 View Agent Activity",
        expanded=False
    ):

        st.markdown("""
        <div style="
            color:#64748B;
            font-size:13px;
            margin-bottom:15px;
        ">
            Watch the agent decide which tools to use.
        </div>
        """, unsafe_allow_html=True)

        for step in range(1, max_steps + 1):

            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

            # Final response
            if not ai_msg.tool_calls:

                st.success(
                    f"Step {step} · Agent completed reasoning"
                )

                return ai_msg.content

            st.markdown(
                f"""
                <div style="
                    margin-top:14px;
                    margin-bottom:8px;
                    font-weight:650;
                    color:#0F172A;
                ">
                    Step {step}
                </div>
                """,
                unsafe_allow_html=True
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
                    f"Tool: {name}\nArguments: {tool_call.get('args', {})}",
                    language="text"
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
                    # Extract the arguments generated by the LLM
                    tool_args = tool_call.get("args", {})

                    # Execute the tool using the arguments directly
                    result = selected_tool.invoke(tool_args)

                    # Add the result back to the conversation
                    messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        )
                    )

                    st.caption("✓ Tool executed successfully")

                except Exception as e:

                    error_message = str(e)

                    messages.append(
                        ToolMessage(
                            content=f"Tool execution error: {error_message}",
                            tool_call_id=tool_call["id"]
                        )
                    )

                    st.error(
                        f"Tool execution failed: {error_message}"
                    )

    return "The agent reached the maximum number of execution steps."


# ============================================================
# QUERY INPUT
# ============================================================

user_question = st.text_area(
    "Your question",
    value="",
    height=125,
    placeholder=(
        "Example: What is LangChain? "
        "Calculate 5 × 15 and summarize the latest news about AI agents."
    ),
    label_visibility="collapsed"
)


# ============================================================
# SUGGESTIONS
# ============================================================

st.markdown(
    '<div class="suggestion-title">Try asking</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div>
    <span class="suggestion">What is LangChain?</span>
    <span class="suggestion">Latest AI agent news</span>
    <span class="suggestion">Calculate 25 × 40</span>
    <span class="suggestion">Explain RAG in simple words</span>
</div>
""", unsafe_allow_html=True)


# ============================================================
# EXECUTE BUTTON
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

execute = st.button(
    "✦  Find Answer",
    use_container_width=True
)


# ============================================================
# MAIN AGENT PROCESS
# ============================================================

if execute:

    if not user_question.strip():

        st.warning(
            "Please enter a question before running the agent."
        )

    elif not GROQ_API_KEY or not TAVILY_API_KEY:

        st.error(
            "Cannot run the agent. Please configure GROQ_API_KEY "
            "and TAVILY_API_KEY in your Streamlit secrets."
        )

    else:

        # ----------------------------------------------------
        # Create Tools
        # ----------------------------------------------------

        with st.spinner(
            "Agent is thinking, selecting tools and researching..."
        ):

            try:

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

                # ------------------------------------------------
                # Initialize Groq
                # ------------------------------------------------

                llm = ChatGroq(
                    model=model_choice,
                    temperature=0
                )

                llm_with_tools = llm.bind_tools(tools)

                # ------------------------------------------------
                # Run Agent
                # ------------------------------------------------

                final_output = run_agent_ui(
                    user_question,
                    tools,
                    tool_map,
                    llm_with_tools
                )

                # ------------------------------------------------
                # Result Header
                # ------------------------------------------------

                st.markdown(
                    """
                    <div class="section-title">
                        <span>✦</span>
                        <span>Research Result</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ------------------------------------------------
                # Answer Card
                # ------------------------------------------------

                st.markdown(
                    """
                    <div class="answer-card">
                        <div class="answer-label">
                            AI SYNTHESIZED ANSWER
                        </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(final_output)

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

                # ------------------------------------------------
                # Agent Information Cards
                # ------------------------------------------------

                st.markdown(
                    '<div class="section-title">⚡ Agent Summary</div>',
                    unsafe_allow_html=True
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(
                        """
                        <div class="info-card">
                            <div class="info-number">Groq</div>
                            <div class="info-label">LLM Engine</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(
                        """
                        <div class="info-card">
                            <div class="info-number">Tavily</div>
                            <div class="info-label">Web Search</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col3:
                    st.markdown(
                        """
                        <div class="info-card">
                            <div class="info-number">4</div>
                            <div class="info-label">Available Tools</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            except Exception as e:

                st.error(
                    f"Initialization Error: {e}"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
    AgentIQ · Built with Streamlit, LangChain, Groq & Tavily
</div>
""", unsafe_allow_html=True)
