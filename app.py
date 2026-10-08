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
# UI STYLING ONLY
# ============================================================

st.markdown("""
<style>

    /* ==============================
       MAIN PAGE
       ============================== */

    .stApp {
        background-color: #F5F7FB;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Hide default Streamlit elements */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }


    /* ==============================
       SIDEBAR
       ============================== */

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
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

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: #475569;
    }


    /* ==============================
       BRANDING
       ============================== */

    .brand-title {
        font-size: 34px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -1px;
        margin-bottom: 2px;
    }

    .brand-subtitle {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 24px;
    }


    /* ==============================
       ONLINE STATUS
       ============================== */

    .online-status {
        display: inline-block;
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
        border-radius: 20px;
        padding: 6px 13px;
        font-size: 13px;
        font-weight: 650;
        margin-bottom: 18px;
    }


    /* ==============================
       MAIN HEADING
       ============================== */

    .main-heading {
        font-size: 32px;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 5px;
        letter-spacing: -0.7px;
    }

    .main-description {
        color: #64748B;
        font-size: 15px;
        margin-bottom: 20px;
    }


    /* ==============================
       QUESTION TEXT AREA
       ============================== */

    textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        line-height: 1.5 !important;
    }

    textarea:focus {
        border: 2px solid #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08) !important;
    }


    /* ==============================
       EXECUTE BUTTON
       ============================== */

    .stButton > button {
        width: 100%;
        min-height: 48px;
        border: none;
        border-radius: 10px;
        background: linear-gradient(
            135deg,
            #2563EB,
            #1D4ED8
        );
        color: #FFFFFF;
        font-size: 15px;
        font-weight: 700;
        box-shadow: 0 5px 14px rgba(37, 99, 235, 0.20);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(
            135deg,
            #1D4ED8,
            #1E40AF
        );
        color: #FFFFFF;
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.25);
    }


    /* ==============================
       EXPANDER / EXECUTION TRACE
       ============================== */

    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        margin-top: 20px;
    }

    div[data-testid="stExpander"] summary {
        color: #0F172A;
        font-weight: 700;
    }


    /* ==============================
       CODE BLOCK
       ============================== */

    div[data-testid="stCodeBlock"] {
        border-radius: 9px;
        border: 1px solid #E2E8F0;
    }


    /* ==============================
       ALERTS
       ============================== */

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }


    /* ==============================
       FINAL ANSWER
       ============================== */

    .answer-heading {
        font-size: 25px;
        font-weight: 800;
        color: #0F172A;
        margin-top: 28px;
        margin-bottom: 5px;
    }

    .answer-description {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 12px;
    }


    /* ==============================
       SIDEBAR TOOL CARDS
       ============================== */

    .tool-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 9px;
        padding: 9px 11px;
        margin-bottom: 8px;
        color: #334155;
        font-size: 13px;
        font-weight: 600;
    }


    /* ==============================
       TECHNOLOGY SECTION
       ============================== */

    .tech-heading {
        font-size: 21px;
        font-weight: 750;
        color: #0F172A;
        margin-top: 30px;
        margin-bottom: 12px;
    }


    /* ==============================
       FOOTER
       ============================== */

    .footer {
        text-align: center;
        color: #94A3B8;
        font-size: 12px;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #E2E8F0;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SECURE CREDENTIAL RETRIEVAL
# ============================================================

# This pulls safely from Streamlit Cloud Secrets or local .streamlit/secrets.toml
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY", "")

# Sync secrets to the OS environment so LangChain tools can find them natively
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

if TAVILY_API_KEY:
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# ============================================================
# MAIN TITLE
# ============================================================

st.title("🤖 AgentIQ")
st.write("Think. Reason. Act.")

# ============================================================
# SIDEBAR CONFIGURATION
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="brand-title">✦ AgentIQ</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-subtitle">'
        'AI Agent Control Center'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

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

    st.markdown("---")

    st.markdown("### 🛠️ Available Tools")

    st.markdown(
        '<div class="tool-card">🔎 Tavily Search</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="tool-card">📚 Wikipedia</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="tool-card">➕ Add / Multiply</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### 🔐 System Status")

    if GROQ_API_KEY and TAVILY_API_KEY:
        st.success("🔒 Fully Authenticated")
    else:
        st.error("⚠️ Missing Cloud Secrets")

    st.markdown("---")

    st.markdown("### 💻 Technology")

    st.caption("⚡ Groq")
    st.caption("🔗 LangChain")
    st.caption("🔎 Tavily")
    st.caption("📚 Wikipedia")


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
        "🕵️‍♂️ View Agent Execution Trace Logs",
        expanded=True
    ):

        for step in range(1, max_steps + 1):

            ai_msg = llm_with_tools.invoke(messages)

            messages.append(ai_msg)

            if not ai_msg.tool_calls:

                st.success(
                    f"Step {step}: No more tools needed. Generating final answer..."
                )

                return ai_msg.content

            st.markdown(
                f"**Step {step}**: Model requested "
                f"`{len(ai_msg.tool_calls)}` tool execution(s):"
            )

            for tool_call in ai_msg.tool_calls:

                name = tool_call["name"]

                selected_tool = tool_map.get(name)

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
# MAIN PAGE UI
# ============================================================

st.markdown(
    '<div class="online-status">🟢 Agent Online</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-heading">Ask your AI Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-description">'
    'Ask questions, perform calculations, research current information, '
    'or combine multiple tasks in a single request.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# QUESTION INPUT
# ============================================================

user_question = st.text_area(
    "✍️ Ask the Agent a multi-part question:",
    value=(
        "What is LangChain? Also, what is 5 multiplied by 15? "
        "Summarize the recent news about AI agents."
    ),
    height=140
)


# ============================================================
# EXECUTE AGENT
# ============================================================

if st.button("✦  Find Answer"):

    if not GROQ_API_KEY or not TAVILY_API_KEY:

        st.error(
            "❌ Cannot run. Please add your credentials inside "
            "your Streamlit App settings dashboard."
        )

    else:

        with st.spinner(
            "Agent is reasoning and executing tools..."
        ):

            try:

                # ====================================================
                # ORIGINAL TOOL INITIALIZATION
                # ====================================================

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
                    t.name: t for t in tools
                }


                # ====================================================
                # ORIGINAL LLM INITIALIZATION
                # ====================================================

                llm = ChatGroq(
                    model=model_choice,
                    temperature=0
                )

                llm_with_tools = llm.bind_tools(tools)


                # ====================================================
                # ORIGINAL AGENT EXECUTION
                # ====================================================

                final_output = run_agent_ui(
                    user_question,
                    tools,
                    tool_map,
                    llm_with_tools
                )


                # ====================================================
                # FINAL ANSWER UI
                # ====================================================

                st.markdown(
                    '<div class="answer-heading">'
                    '🏆 Final Synthesized Answer'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="answer-description">'
                    'The agent completed the requested tasks and '
                    'generated the response below.'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.info(final_output)


                # ====================================================
                # TECHNOLOGY SECTION
                # ====================================================

                st.markdown(
                    '<div class="tech-heading">Powered By</div>',
                    unsafe_allow_html=True
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown("### ⚡ Groq")
                    st.caption("Fast LLM inference")

                with col2:
                    st.markdown("### 🔗 LangChain")
                    st.caption("Agent orchestration")

                with col3:
                    st.markdown("### 🔎 Tavily")
                    st.caption("Web research")

                with col4:
                    st.markdown("### 📚 Wikipedia")
                    st.caption("Knowledge retrieval")


            except Exception as e:

                st.error(
                    f"Initialization Error: {e}"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'AgentIQ • Intelligent AI Agent Framework • '
    'Powered by Groq + LangChain'
    '</div>',
    unsafe_allow_html=True
)
