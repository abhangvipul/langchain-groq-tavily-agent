import os
import streamlit as st
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

# --- STREAMLIT UI CONFIGURATION ---
st.set_page_config(page_title="AI Agent Framework", page_icon="🤖", layout="wide")
st.title("🤖 LangChain & Groq AI Agent Dashboard")
st.write("Convert your Jupyter loop into an interactive local application.")

# --- SIDEBAR: SECURE CREDENTIAL INPUT ---
with st.sidebar:
    st.header("🔑 API Configurations")
    groq_key = st.text_input("Groq API Key", type="password")
    tavily_key = st.text_input("Tavily API Key", type="password")
    
    st.markdown("---")
    max_steps = st.slider("Max Agent Loops", min_value=1, max_value=10, value=5)
    model_choice = st.selectbox("LLM Model Core", ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"])

# --- DEFINE CUSTOM TOOLS ---
@tool
def add(a: int, b: int) -> int:
    """Add two integers and return the sum. Use this whenever asked to add numbers."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the product. Use this whenever asked to multiply numbers."""
    return a * b

# --- AGENT RUNTIME EXECUTION LOOP ---
def run_agent_ui(question: str, tools, tool_map, llm_with_tools):
    SYSTEM_PROMPT = """You are a helpful research assistant with access to tools.
    Rules:
    - If a question has several parts, answer EVERY part. Call one tool per part.
    - Use the add/multiply tools for arithmetic instead of calculating it yourself.
    - Use wikipedia for established facts and definitions.
    - Use tavily_search for recent news and current events.
    - Finish with a clear, well-organised answer in plain language."""

    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=question)]
    
    # Create an expander box to show live execution steps
    with st.expander("🕵️‍♂️ View Agent Execution Trace Logs", expanded=True):
        for step in range(1, max_steps + 1):
            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

            if not ai_msg.tool_calls:
                st.success(f"Step {step}: No more tools needed. Generating final answer...")
                return ai_msg.content

            st.markdown(f"**Step {step}**: Model requested `{len(ai_msg.tool_calls)}` tool execution(s):")
            
            for tool_call in ai_msg.tool_calls:
                name = tool_call["name"]
                selected_tool = tool_map.get(name)
                st.code(f"Running tool: {name}({tool_call['args']})", language="python")

                if selected_tool is None:
                    messages.append(ToolMessage(content=f"Error: no tool named '{name}'", tool_call_id=tool_call["id"]))
                    continue

                try:
                    result = selected_tool.invoke(tool_call)
                    messages.append(result)
                    st.caption("✅ Tool successfully executed.")
                except Exception as e:
                    messages.append(ToolMessage(content=str(e), tool_call_id=tool_call["id"]))
                    st.error(f"❌ Tool execution failed: {e}")
                    
    return "Agent execution timed out without reaching an answer."

# --- MAIN PAGE CORE PROCESS ---
user_question = st.text_area("✍️ Ask the Agent a multi-part question:", 
                             value="What is LangChain? Also, what is 5 multiplied by 15? Summarize the recent news about AI agents.")

if st.button("🚀 Execute Agent Loop"):
    if not groq_key or not tavily_key:
        st.warning("⚠️ Please provide both your Groq and Tavily API keys in the sidebar.")
    else:
        # Set environment keys dynamically
        os.environ["GROQ_API_KEY"] = groq_key
        os.environ["TAVILY_API_KEY"] = tavily_key

        with st.spinner("Agent is reasoning and executing tools..."):
            try:
                # Initialize tools dynamically
                api_wrapper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=1500)
                wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
                tavily_tool = TavilySearch(max_results=5, topic="general")
                
                tools = [wiki_tool, tavily_tool, add, multiply]
                tool_map = {t.name: t for t in tools}

                # Initialize LLM
                llm = ChatGroq(model=model_choice, temperature=0)
                llm_with_tools = llm.bind_tools(tools)

                # Run core agent
                final_output = run_agent_ui(user_question, tools, tool_map, llm_with_tools)
                
                # Render final results clean
                st.markdown("### 🏆 Final Synthesized Answer")
                st.info(final_output)

            except Exception as e:
                st.error(f"Initialization Error: {e}")
