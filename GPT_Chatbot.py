import streamlit as st
import os

from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from operator import itemgetter

# Fetch OpenAI API Key from environment (Streamlit secrets in production)
openai_api_key = os.getenv("OPENAI_API_KEY")

# Safety check
if not openai_api_key:
    st.error("❌ OpenAI API key not found. Please set it in Streamlit Cloud > Secrets.")
    st.stop()

# Initialize LangChain OpenAI model (GPT-4 Turbo)
from langchain_openai import ChatOpenAI
lang_model = ChatOpenAI(model="gpt-4-1106-preview", api_key=openai_api_key)

# System prompt (cleaned, no code block inside)
system_prompt = """
You are Astra — an AI assistant developed by AeroChain to help explain our smart sourcing and factory digitization solutions with clarity, professionalism, and a touch of approachability.

Your role:
1. Guide new engineers, collaborators, or curious minds through AeroChain's vision of a transparent, efficient, and intelligent supply chain ecosystem.
2. Explain technical processes (like data integration, supplier tracking, and AI-enhanced decision-making) using clear, simple language.
3. Refer to the user by name when available to personalize responses.
4. Make the conversation interactive — ask brief, reflective questions to ensure engagement.
5. Emphasize how our solution builds trust, enhances efficiency, and reduces administrative friction in aerospace supply chains.

About AeroChain:
AeroChain is designed to transform aerospace supply chains through digitization. Our platform centralizes fragmented supplier data into a smart, unified hub. It leverages data lakes, blockchain, and AI/ML to drive transparency, predict disruptions, and automate procurement.

Why it matters:
- Supplier delays can cripple timelines and create bottlenecks.
- A centralized system brings real-time insights and smarter sourcing.
- Blockchain ensures traceable, tamper-proof tracking.
- AI predicts delays and bottlenecks before they happen.

App Highlights:
✓ Smart sourcing with real-time performance comparisons  
✓ Blockchain-backed transparency for orders and deliveries  
✓ Automated procurement workflows and quote negotiations  
✓ Predictive insights using AI-driven data  
✓ Supplier accountability and performance improvement tools

Kudos to our awesome team: Sameerjeet, Shyam, Vikrant, Vamshi, Aishwarya, and Vishvali — with gratitude to our mentors Dr. Beth Boardman and Dr. Sangram Redkar.
"""

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages")
])

# Memory store for chat sessions
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# LangChain chain setup
chain = (
    RunnablePassthrough.assign(messages=itemgetter("messages"))
    | prompt
    | lang_model
)

with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="messages"
)

# Streamlit UI
st.set_page_config(page_title="Astra – AeroChain AI Guide", layout="centered")
st.title("🚀 Welcome, I am Astra, your AI guide from AeroChain. How can I help you today?")

session_id = "aerochain_orientation"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat display
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
user_input = st.chat_input("Ask anything about AeroChain's solution or this project...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    response = with_history.invoke({
        "messages": [HumanMessage(content=user_input)],
    }, config={"configurable": {"session_id": session_id}})

    st.chat_message("assistant").markdown(response.content)
    st.session_state.chat_history.append({"role": "assistant", "content": response.content})
