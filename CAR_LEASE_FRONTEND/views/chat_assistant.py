"""AI Negotiation Assistant page for ContractCoach."""
import streamlit as st
from services.api_service import APIService
from components.chat import render_chat_message


# Suggestion chips for quick prompts
SUGGESTION_CHIPS = [
    "APR negotiation",
    "Reduce down payment",
    "Dealer tactics",
    "Questions to ask"
]

# Default welcome message
WELCOME_MESSAGE = """Hi! I'm your AI negotiation coach. I'm here to help you get the best deal on your car lease.

I can help you with:
- 💬 **Talking points** for negotiating specific terms
- ❓ **Questions to ask** the dealer  
- 🛡️ **Dealer tactics** to watch out for
- 💰 **Strategies** to lower your costs

Upload a contract first, then ask me anything!"""


def get_contract_summary_message():
    """Generate a message summarizing the uploaded contract."""
    contract_data = st.session_state.get("contract_data") or {}
    sla = contract_data.get("sla") or {}
    if not sla:
        return None
    
    parts = ["I've analyzed your contract. Here's what I found:\n"]
    if sla.get("apr"):
        parts.append(f"- **APR:** {sla['apr']}")
    if sla.get("monthly_payment"):
        parts.append(f"- **Monthly Payment:** {sla['monthly_payment']}")
    if sla.get("lease_term_months"):
        parts.append(f"- **Lease Term:** {sla['lease_term_months']}")
    if sla.get("down_payment"):
        parts.append(f"- **Down Payment:** {sla['down_payment']}")
    if sla.get("mileage_allowance"):
        parts.append(f"- **Mileage Allowance:** {sla['mileage_allowance']}")
    if sla.get("residual_value"):
        parts.append(f"- **Residual Value:** {sla['residual_value']}")
    
    if len(parts) > 1:
        parts.append("\n**How can I help you negotiate these terms?**")
        return "\n".join(parts)
    return None


def initialize_chat():
    """Initialize chat history if not exists."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # If chat is empty, add welcome message
    if len(st.session_state.chat_history) == 0:
        # Check if contract is loaded and add summary
        contract_summary = get_contract_summary_message()
        if contract_summary:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": contract_summary
            })
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": WELCOME_MESSAGE
            })


def clear_chat_history():
    """Clear chat history but keep contract data."""
    contract_id = st.session_state.get("contract_id")
    if contract_id:
        APIService.clear_chat_history(contract_id)
    
    # Reset with contract summary if available
    contract_summary = get_contract_summary_message()
    if contract_summary:
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": contract_summary
        }]
    else:
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": WELCOME_MESSAGE
        }]


def send_message(message: str):
    """Send a message to the AI assistant."""
    if not message.strip():
        return
    
    # Check for contract_id
    contract_id = st.session_state.get("contract_id")
    if not contract_id:
        st.session_state.chat_history.append({
            "role": "user",
            "content": message
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "⚠️ Please upload a contract first in the **Contract Analysis** page to get personalized negotiation advice based on your specific terms."
        })
        return
    
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": message
    })
    
    # Send to API
    with st.spinner("🤔 Thinking..."):
        response = APIService.send_chat_message(
            message=message,
            contract_id=contract_id
        )
    
    # Add assistant response to history
    assistant_message = response.get("assistant_response", "I'm sorry, I couldn't process that request.")
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": assistant_message
    })


def render_chat_assistant():
    """Render the AI Negotiation Assistant page."""
    
    # Initialize chat
    initialize_chat()
    
    st.markdown("## 💬 AI Negotiation Assistant")
    st.markdown("Get personalized coaching for your car lease negotiation.")
    
    # Contract context indicator
    contract_id = st.session_state.get("contract_id")
    if contract_id and st.session_state.get("contract_data"):
        sla = st.session_state.contract_data.get("sla", {})
        if sla:
            st.success(f"📄 Contract #{contract_id} loaded - I can reference your specific terms!")
            
            # Load existing chat history from backend if this is first load
            if len(st.session_state.chat_history) <= 1:
                history_result = APIService.get_chat_history(contract_id)
                messages = history_result.get("messages", [])
                if messages:
                    st.session_state.chat_history = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in messages
                    ]
    else:
        st.warning("⚠️ Please upload a contract in **Contract Analysis** first to get personalized negotiation advice.")
    
    st.markdown("---")
    
    # Chat header with clear button
    header_col1, header_col2 = st.columns([3, 1])
    
    with header_col1:
        st.markdown("### 💭 Chat")
    
    with header_col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            clear_chat_history()
            st.rerun()
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # Suggestion chips
    st.markdown("")
    st.markdown("**Quick prompts:**")
    chip_cols = st.columns(len(SUGGESTION_CHIPS))
    
    for i, chip in enumerate(SUGGESTION_CHIPS):
        with chip_cols[i]:
            if st.button(chip, key=f"chip_{i}", use_container_width=True):
                # Generate contextual prompt based on chip
                if chip == "APR negotiation":
                    prompt = "What strategies can I use to negotiate a lower APR on my car lease?"
                elif chip == "Reduce down payment":
                    prompt = "How can I negotiate to reduce the down payment required for my lease?"
                elif chip == "Dealer tactics":
                    prompt = "What are common dealer tactics I should watch out for, and how should I respond?"
                elif chip == "Questions to ask":
                    prompt = "What are the most important questions I should ask the dealer before signing?"
                else:
                    prompt = chip
                    
                send_message(prompt)
                st.rerun()
    
    st.markdown("---")
    
    # Chat input
    user_input = st.chat_input("Type your question here...")
    
    if user_input:
        send_message(user_input)
        st.rerun()
    
    # Sidebar tips (shown as expander)
    with st.expander("💡 Negotiation Tips"):
        st.markdown("""
        **Before visiting the dealer:**
        - Research fair market prices
        - Know your credit score
        - Compare offers from multiple dealers
        
        **During negotiation:**
        - Focus on the total cost, not monthly payment
        - Don't reveal your budget upfront
        - Be willing to walk away
        
        **Key terms to negotiate:**
        - Selling price (capitalized cost)
        - Money factor (interest rate)
        - Down payment and fees
        - Mileage allowance
        """)
    
    # Contract context summary
    if st.session_state.get("contract_data"):
        with st.expander("📋 Your Contract Summary"):
            sla = st.session_state.contract_data.get("sla", {})
            if sla:
                summary_items = []
                if sla.get("apr"):
                    summary_items.append(f"**APR:** {sla['apr']}")
                if sla.get("monthly_payment"):
                    summary_items.append(f"**Monthly Payment:** {sla['monthly_payment']}")
                if sla.get("lease_term_months"):
                    summary_items.append(f"**Lease Term:** {sla['lease_term_months']}")
                if sla.get("down_payment"):
                    summary_items.append(f"**Down Payment:** {sla['down_payment']}")
                if sla.get("mileage_allowance"):
                    summary_items.append(f"**Mileage:** {sla['mileage_allowance']}")
                if sla.get("residual_value"):
                    summary_items.append(f"**Residual Value:** {sla['residual_value']}")
                
                if summary_items:
                    for item in summary_items:
                        st.markdown(item)
                else:
                    st.markdown("No SLA data extracted yet.")
            else:
                st.markdown("No contract data available.")
