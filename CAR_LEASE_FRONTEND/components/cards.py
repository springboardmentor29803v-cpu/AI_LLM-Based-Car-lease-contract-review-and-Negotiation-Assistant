"""Card components for displaying data."""
import streamlit as st
import re
from typing import Optional


def sanitize_html(text: str) -> str:
    """Remove HTML tags from text to prevent display issues."""
    if not text:
        return text
    # Remove HTML tags like </div>, <p>, etc.
    cleaned = re.sub(r'<[^>]+>', '', str(text))
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def render_sla_card(field_name: str, value: str, issue: Optional[str] = None, severity: Optional[str] = None):
    """
    Render a card for an SLA field.
    
    Args:
        field_name: Name of the SLA field
        value: Extracted value
        issue: Optional issue description
        severity: Optional severity level (low, medium, high)
    """
    # Determine card styling based on severity
    severity_colors = {
        "high": "#ffebee",
        "medium": "#fff3e0", 
        "low": "#e8f5e9",
        None: "#f5f5f5"
    }
    
    severity_icons = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
        None: "⚪"
    }
    
    bg_color = severity_colors.get(severity, "#f5f5f5")
    icon = severity_icons.get(severity, "⚪")
    
    # Sanitize value to remove any HTML tags from extraction
    clean_value = sanitize_html(value) if value else "N/A"
    
    with st.container():
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: #333; font-size: 0.9rem;">{field_name}</h4>
                <span>{icon}</span>
            </div>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: 600; color: #1a1a1a;">
                {clean_value}
            </p>
            {"<p style='margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #666;'>" + issue + "</p>" if issue else ""}
        </div>
        """, unsafe_allow_html=True)


def render_vehicle_card(field_name: str, value: str):
    """
    Render a card for vehicle information.
    
    Args:
        field_name: Name of the vehicle field
        value: Field value
    """
    with st.container():
        st.markdown(f"""
        <div style="
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #bbdefb;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        ">
            <h4 style="margin: 0; color: #1565c0; font-size: 0.85rem; text-transform: uppercase;">
                {field_name}
            </h4>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: 600; color: #0d47a1;">
                {value if value else "N/A"}
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_action_card(title: str, description: str, icon: str):
    """
    Render an action card for the dashboard.
    
    Args:
        title: Card title
        description: Card description
        icon: Emoji icon
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s ease;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <h3 style="margin: 0; font-size: 1.2rem; font-weight: 600;">{title}</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
