"""
ContractCoach - AI-Powered Car Lease Negotiation Assistant
Main Streamlit Application
"""
import streamlit as st
from config import APP_NAME, APP_ICON

# Import page renderers
from views import (
    render_dashboard,
    render_contract_analysis,
    render_vin_lookup,
    render_chat_assistant,
    render_market_analysis
)

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main container padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: white !important;
    }
    
    /* Navigation button styling */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        padding: 0.75rem 1rem;
        margin-bottom: 0.25rem;
        border: none;
        border-radius: 8px;
        background-color: transparent;
        color: white !important;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.1);
        transform: translateX(5px);
    }
    
    /* Active nav button */
    [data-testid="stSidebar"] .nav-active > button {
        background-color: rgba(102, 126, 234, 0.3) !important;
        border-left: 3px solid #667eea !important;
    }
    
    /* Card hover effects */
    .stContainer > div:hover {
        transform: translateY(-2px);
        transition: transform 0.2s ease;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        border-radius: 15px;
    }
    
    /* Chat message styling */
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        margin-bottom: 0.5rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide default Streamlit sidebar navigation */
    [data-testid="stSidebarNav"] {display: none !important;}
    [data-testid="stSidebarNavItems"] {display: none !important;}
    section[data-testid="stSidebar"] > div:first-child > div:first-child > div:nth-child(1) {
        display: none !important;
    }
    /* Hide the hamburger menu */
    button[kind="header"] {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if "contract_data" not in st.session_state:
        st.session_state.contract_data = None
    if "contract_id" not in st.session_state:
        st.session_state.contract_id = None
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = None
    if "vehicle_data" not in st.session_state:
        st.session_state.vehicle_data = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def render_sidebar():
    """Render the persistent sidebar navigation."""
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0 1.5rem 0;">
            <h1 style="margin: 0; font-size: 1.8rem; color: white;">ContractCoach</h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8; color: #a8dadc;">
                AI Negotiation Assistant
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation menu using buttons
        nav_items = [
            ("Dashboard", "Dashboard"),
            ("Contract Analysis", "Contract Analysis"),
            ("Market Analysis", "Market Analysis"),
            ("VIN Lookup", "VIN Lookup"),
            ("AI Assistant", "AI Negotiation Assistant")
        ]
        
        for label, page_name in nav_items:
            # Highlight active page
            is_active = st.session_state.current_page == page_name
            button_type = "primary" if is_active else "secondary"
            
            if st.button(label, key=f"nav_{page_name}", use_container_width=True, type=button_type):
                st.session_state.current_page = page_name
                st.rerun()
        
        st.markdown("---")
        
        # Session info
        st.markdown("### Session Info")
        
        if st.session_state.get("contract_id"):
            st.markdown(f"**Contract ID:** #{st.session_state.contract_id}")
        
        if st.session_state.get("uploaded_file_name"):
            fname = st.session_state.uploaded_file_name
            display_name = fname[:18] + "..." if len(fname) > 18 else fname
            st.markdown(f"**File:** {display_name}")
        else:
            st.markdown("No contract uploaded")
        
        if st.session_state.get("vehicle_data"):
            vehicle = st.session_state.vehicle_data
            make = vehicle.get("make", "")
            model = vehicle.get("model", "")
            year = vehicle.get("year", "")
            st.markdown(f"**Vehicle:** {year} {make} {model}")
        else:
            st.markdown("No vehicle info")
        
        chat_count = len(st.session_state.get("chat_history", []))
        st.markdown(f"**Chat messages:** {chat_count}")
        
        st.markdown("---")
        
        # Reset session button
        if st.button("Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != "current_page":
                    del st.session_state[key]
            st.rerun()


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render selected page
    page = st.session_state.current_page
    
    if page == "Dashboard":
        render_dashboard()
    elif page == "Contract Analysis":
        render_contract_analysis()
    elif page == "Market Analysis":
        render_market_analysis()
    elif page == "VIN Lookup":
        render_vin_lookup()
    elif page == "AI Negotiation Assistant":
        render_chat_assistant()


if __name__ == "__main__":
    main()
