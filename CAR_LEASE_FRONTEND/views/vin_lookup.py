"""VIN Lookup page for ContractCoach."""
import streamlit as st
import re
from services.api_service import APIService
from components.cards import render_vehicle_card


def validate_vin(vin: str) -> bool:
    """Validate VIN format (17 alphanumeric characters, no I, O, Q)."""
    if len(vin) != 17:
        return False
    # VIN cannot contain I, O, or Q
    pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
    return bool(re.match(pattern, vin.upper()))


def render_vin_lookup():
    """Render the VIN Lookup page."""
    
    st.markdown("## 🔍 VIN Lookup")
    st.markdown("Enter a Vehicle Identification Number to get detailed vehicle specifications.")
    
    # Load vehicle data from contract on first visit to this page
    if "vin_page_initialized" not in st.session_state:
        st.session_state.vin_page_initialized = True
        contract_data = st.session_state.get("contract_data") or {}
        contract_vehicle = contract_data.get("vehicle", {})
        if contract_vehicle and not st.session_state.get("vehicle_data"):
            st.session_state.vehicle_data = contract_vehicle
            st.info("📄 Vehicle data loaded from your uploaded contract.")
    
    st.markdown("---")
    
    # VIN input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        vin_input = st.text_input(
            "Enter 17-digit VIN",
            max_chars=17,
            placeholder="e.g., 1HGBH41JXMN109186",
            help="A VIN is a unique 17-character code that identifies your vehicle",
            key="vin_input"
        ).upper()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        lookup_clicked = st.button("🔍 Lookup", use_container_width=True, type="primary")
    
    # Validation and lookup - only when button is clicked
    if lookup_clicked and vin_input:
        if len(vin_input) < 17:
            st.warning(f"VIN must be 17 characters. Current: {len(vin_input)} characters")
        elif not validate_vin(vin_input):
            st.warning("Invalid VIN format. VIN must be 17 alphanumeric characters (no I, O, or Q).")
        else:
            # Perform lookup
            with st.spinner("🔄 Looking up vehicle information..."):
                result = APIService.lookup_vin(vin_input)
                
                if result:
                    st.session_state.last_vin = vin_input
                    st.session_state.vehicle_data = result.get("combined_data", {}).get("vehicle", {})
                    
                    # Also store in contract context
                    if not st.session_state.get("contract_data"):
                        st.session_state.contract_data = result.get("combined_data", {})
                    else:
                        st.session_state.contract_data["vehicle"] = st.session_state.vehicle_data
                    st.success("✅ Vehicle data loaded successfully!")
    elif vin_input and len(vin_input) < 17:
        st.info(f"VIN must be 17 characters. Current: {len(vin_input)} characters")
    
    # Display vehicle information
    if st.session_state.get("vehicle_data"):
        st.markdown("---")
        st.markdown("### 🚗 Vehicle Information")
        
        vehicle_data = st.session_state.vehicle_data
        
        # Display ALL vehicle data dynamically as cards
        # Create nice display names from keys
        def format_key(key: str) -> str:
            """Convert snake_case key to Title Case display name."""
            return key.replace("_", " ").title()
        
        # Filter out None/null values and error fields
        display_items = [
            (key, value) for key, value in vehicle_data.items()
            if value is not None and value != "" and key not in ["error_code", "error_text", "recalls"]
        ]
        
        # Create grid layout (3 columns)
        cols_per_row = 3
        
        for i in range(0, len(display_items), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(display_items):
                    key, value = display_items[i + j]
                    display_name = format_key(key)
                    
                    with col:
                        render_vehicle_card(display_name, str(value))
        
        # Additional info section
        st.markdown("---")
        st.markdown("### 📋 Additional Details")
        
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.markdown("""
            <div style="
                background-color: #fff3e0;
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #ff9800;
            ">
                <h4 style="margin: 0 0 0.5rem 0;">⚠️ VIN Decoded</h4>
                <p style="margin: 0; font-size: 0.9rem; color: #666;">
                    This information was decoded from the VIN. 
                    Always verify with official documentation.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with detail_col2:
            recall_info = vehicle_data.get("recalls", [])
            if recall_info:
                st.markdown(f"""
                <div style="
                    background-color: #ffebee;
                    padding: 1.5rem;
                    border-radius: 10px;
                    border-left: 4px solid #f44336;
                ">
                    <h4 style="margin: 0 0 0.5rem 0;">🔴 Recall Notice</h4>
                    <p style="margin: 0; font-size: 0.9rem; color: #666;">
                        {len(recall_info)} recall(s) found for this vehicle.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background-color: #e8f5e9;
                    padding: 1.5rem;
                    border-radius: 10px;
                    border-left: 4px solid #4caf50;
                ">
                    <h4 style="margin: 0 0 0.5rem 0;">✅ No Recalls</h4>
                    <p style="margin: 0; font-size: 0.9rem; color: #666;">
                        No active recalls found for this vehicle.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Action buttons
        st.markdown("")
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
        
        with btn_col1:
            if st.button("📄 Analyze Contract", use_container_width=True):
                st.session_state.current_page = "Contract Analysis"
                st.rerun()
        
        with btn_col2:
            if st.button("💬 Get Negotiation Tips", use_container_width=True):
                st.session_state.current_page = "AI Negotiation Assistant"
                st.rerun()
    
    else:
        # Show placeholder
        st.markdown("""
        <div style="
            border: 2px dashed #bbdefb;
            border-radius: 15px;
            padding: 3rem;
            text-align: center;
            background-color: #e3f2fd;
            margin-top: 2rem;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🚗</div>
            <h3 style="color: #1565c0; margin: 0;">Enter a VIN to get started</h3>
            <p style="color: #64b5f6; margin: 0.5rem 0 0 0;">
                The VIN can be found on your dashboard, door jamb, or vehicle documents
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # VIN location tips
        st.markdown("")
        with st.expander("📍 Where to find your VIN"):
            st.markdown("""
            **Common VIN locations:**
            1. **Dashboard** - Driver's side, visible through windshield
            2. **Door jamb** - Driver's side door frame
            3. **Vehicle title** - Listed on your registration documents
            4. **Insurance card** - Usually printed on your policy
            5. **Owner's manual** - Often recorded inside
            """)
