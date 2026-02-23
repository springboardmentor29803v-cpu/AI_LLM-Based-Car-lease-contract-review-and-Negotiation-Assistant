"""Chat components for the AI Negotiation Assistant."""
import streamlit as st
from typing import List, Callable


def render_chat_message(role: str, content: str):
    """
    Render a chat message bubble.
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
    """
    if role == "user":
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1rem;
        ">
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 0.8rem 1.2rem;
                border-radius: 18px 18px 4px 18px;
                max-width: 80%;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
            ">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: flex-start;
            margin-bottom: 1rem;
        ">
            <div style="
                background-color: #f0f2f6;
                color: #1a1a1a;
                padding: 0.8rem 1.2rem;
                border-radius: 18px 18px 18px 4px;
                max-width: 80%;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            ">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_suggestion_chips(suggestions: List[str], on_click: Callable[[str], None]):
    """
    Render suggestion chips for quick prompts.
    
    Args:
        suggestions: List of suggestion texts
        on_click: Callback function when a chip is clicked
    """
    cols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        with cols[i]:
            if st.button(suggestion, key=f"chip_{i}", use_container_width=True):
                on_click(suggestion)
