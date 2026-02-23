"""Dashboard (Home) page for ContractCoach."""
import streamlit as st
from components.cards import render_action_card
from config import COPYRIGHT_YEAR


def render_dashboard():
    """Render the Dashboard/Home page."""
    
    # Hero Section
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    ">
        <h1 style="
            color: white;
            font-size: 3rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">
            🚗 ContractCoach
        </h1>
        <p style="
            color: #a8dadc;
            font-size: 1.3rem;
            margin: 0;
            font-weight: 300;
        ">
            Your AI-Powered Car Lease Negotiation Assistant
        </p>
        <p style="
            color: #e0e0e0;
            font-size: 1rem;
            margin-top: 1rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        ">
            Analyze contracts, understand terms, and negotiate with confidence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Action Cards
    st.markdown("### 🎯 What Can ContractCoach Do For You?")
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_action_card(
            "📄 Contract Analysis",
            "Upload your lease agreement and get instant insights on key terms and potential issues",
            "📄"
        )
        st.markdown("")
        render_action_card(
            "🔍 VIN Lookup",
            "Enter any VIN to get detailed vehicle specifications and history",
            "🔍"
        )
    
    with col2:
        render_action_card(
            "💬 AI Negotiation Coach",
            "Get personalized talking points and strategies for your dealer conversation",
            "💬"
        )
        st.markdown("")
        render_action_card(
            "⚠️ Risk Detection",
            "Identify unfavorable clauses and understand what's negotiable",
            "⚠️"
        )
    
    st.markdown("")
    st.markdown("---")
    
    # How It Works Section
    st.markdown("### 📋 How It Works")
    
    steps_col1, steps_col2, steps_col3 = st.columns(3)
    
    with steps_col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="
                background-color: #667eea;
                color: white;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem auto;
                font-size: 1.5rem;
                font-weight: bold;
            ">1</div>
            <h4 style="margin: 0;">Upload Contract</h4>
            <p style="color: #666; font-size: 0.9rem;">
                Upload your lease agreement in PDF, PNG, or JPG format
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with steps_col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="
                background-color: #667eea;
                color: white;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem auto;
                font-size: 1.5rem;
                font-weight: bold;
            ">2</div>
            <h4 style="margin: 0;">Review Analysis</h4>
            <p style="color: #666; font-size: 0.9rem;">
                See extracted terms, identify issues, and understand the fine print
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with steps_col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="
                background-color: #667eea;
                color: white;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem auto;
                font-size: 1.5rem;
                font-weight: bold;
            ">3</div>
            <h4 style="margin: 0;">Get Coaching</h4>
            <p style="color: #666; font-size: 0.9rem;">
                Chat with our AI to prepare talking points and negotiation strategies
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2rem 0;
        color: #888;
        font-size: 0.9rem;
    ">
        <p style="margin: 0;">ContractCoach © {COPYRIGHT_YEAR}</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem;">
            Empowering consumers with AI-driven contract intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)
