"""Contract Analysis page for ContractCoach."""
import streamlit as st
from services.api_service import APIService
from components.cards import render_sla_card
from config import MAX_FILE_SIZE_MB, ALLOWED_FILE_TYPES


# SLA field definitions with display names - keys match backend response
SLA_FIELDS = [
    {"key": "apr", "name": "APR (Annual Percentage Rate)", "icon": "📈"},
    {"key": "lease_term_months", "name": "Lease Term", "icon": "📅"},
    {"key": "monthly_payment", "name": "Monthly Payment", "icon": "💵"},
    {"key": "down_payment", "name": "Down Payment", "icon": "💰"},
    {"key": "residual_value", "name": "Residual Value", "icon": "🏷️"},
    {"key": "mileage_allowance", "name": "Mileage Allowance", "icon": "🛣️"},
    {"key": "late_fees", "name": "Late Fees", "icon": "⏰"},
    {"key": "early_termination_clause", "name": "Early Termination", "icon": "🚪"},
    {"key": "purchase_option", "name": "Purchase Option", "icon": "🔑"},
]


def render_contract_analysis():
    """Render the Contract Analysis page."""
    
    st.markdown("## 📄 Contract Analysis")
    st.markdown("Upload your car lease agreement to extract and analyze key terms.")
    
    # File uploader section
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "Drag and drop your contract file here",
        type=ALLOWED_FILE_TYPES,
        help=f"Supported formats: PDF, PNG, JPG (max {MAX_FILE_SIZE_MB}MB)",
        key="contract_uploader"
    )
    
    if uploaded_file is not None:
        # Check file size
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE_MB}MB)")
            return
        
        # Display uploaded file info
        st.success(f"📎 Uploaded: **{uploaded_file.name}** ({file_size_mb:.2f} MB)")
        
        # Check if we need to process this file
        if (st.session_state.get("uploaded_file_name") != uploaded_file.name or
            st.session_state.get("contract_data") is None):
            
            with st.spinner("🔄 Analyzing your contract... This may take a moment."):
                # Call backend API
                result = APIService.upload_contract(uploaded_file)
                
                if result:
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.session_state.contract_data = result.get("data", {})
                    st.session_state.contract_id = result.get("document_id")  # Store contract ID for chat
                    st.session_state.vehicle_data = result.get("data", {}).get("vehicle", {})  # Store vehicle data
                    st.session_state.raw_response = result
                    # Clear chat history so it refreshes with new contract context
                    st.session_state.chat_history = []
                    st.success(f"✅ Contract analyzed successfully! (ID: #{result.get('document_id', 'N/A')})")
                else:
                    st.error("Failed to analyze contract. Please try again.")
                    return
    
    # Show previously uploaded file info if no new file
    elif st.session_state.get("uploaded_file_name"):
        st.info(f"📎 Previously analyzed: **{st.session_state.uploaded_file_name}**")
    
    # Display SLA fields in grid - show if contract_data exists (even without file uploader)
    if st.session_state.get("contract_data"):
            st.markdown("---")
            st.markdown("### 📊 Extracted Contract Terms")
            
            contract_data = st.session_state.contract_data
            sla_data = contract_data.get("sla", {})
            issues_list = contract_data.get("issues", [])  # Issues come as a list from backend
            
            # Convert issues list to dict by field for easier lookup
            issues = {}
            for issue in issues_list:
                field = issue.get("field")
                if field:
                    issues[field] = {
                        "severity": issue.get("severity", "low"),
                        "description": issue.get("issue", ""),
                        "reason": issue.get("reason", ""),
                        "negotiation_intent": issue.get("negotiation_intent", "")
                    }
            
            # Create grid layout (3 columns)
            cols_per_row = 3
            
            for i in range(0, len(SLA_FIELDS), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    if i + j < len(SLA_FIELDS):
                        field = SLA_FIELDS[i + j]
                        field_key = field["key"]
                        
                        # Get value from SLA data
                        value = sla_data.get(field_key, "Not found")
                        
                        # Get any issues for this field
                        field_issue = issues.get(field_key, {})
                        issue_text = field_issue.get("description") if isinstance(field_issue, dict) else None
                        severity = field_issue.get("severity") if isinstance(field_issue, dict) else None
                        
                        with col:
                            render_sla_card(
                                f"{field['icon']} {field['name']}",
                                str(value) if value else "N/A",
                                issue=issue_text,
                                severity=severity
                            )
            
            # Summary section
            st.markdown("---")
            st.markdown("### 📝 Analysis Summary")
            
            summary_col1, summary_col2 = st.columns(2)
            
            with summary_col1:
                # Count issues by severity
                high_issues = sum(1 for i in issues.values() if isinstance(i, dict) and i.get("severity") == "high")
                medium_issues = sum(1 for i in issues.values() if isinstance(i, dict) and i.get("severity") == "medium")
                low_issues = sum(1 for i in issues.values() if isinstance(i, dict) and i.get("severity") == "low")
                
                st.markdown(f"""
                <div style="
                    background-color: #f8f9fa;
                    padding: 1.5rem;
                    border-radius: 10px;
                    border-left: 4px solid #667eea;
                ">
                    <h4 style="margin: 0 0 1rem 0;">Issues Found</h4>
                    <p style="margin: 0.3rem 0;">🔴 High Priority: <strong>{high_issues}</strong></p>
                    <p style="margin: 0.3rem 0;">🟡 Medium Priority: <strong>{medium_issues}</strong></p>
                    <p style="margin: 0.3rem 0;">🟢 Low Priority: <strong>{low_issues}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            with summary_col2:
                st.markdown("""
                <div style="
                    background-color: #e8f5e9;
                    padding: 1.5rem;
                    border-radius: 10px;
                    border-left: 4px solid #4caf50;
                ">
                    <h4 style="margin: 0 0 1rem 0;">💡 Next Steps</h4>
                    <p style="margin: 0.3rem 0; font-size: 0.9rem;">
                        1. Review flagged issues above<br>
                        2. Use VIN Lookup for vehicle details<br>
                        3. Chat with AI for negotiation tips
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Action buttons
            st.markdown("")
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
            
            with btn_col1:
                if st.button("🔍 Lookup VIN", use_container_width=True):
                    st.session_state.current_page = "VIN Lookup"
                    st.rerun()
            
            with btn_col2:
                if st.button("💬 Get Negotiation Tips", use_container_width=True):
                    st.session_state.current_page = "AI Negotiation Assistant"
                    st.rerun()
    
    # Show placeholder when no contract data exists
    if not st.session_state.get("contract_data"):
        st.markdown("""
        <div style="
            border: 2px dashed #ccc;
            border-radius: 15px;
            padding: 3rem;
            text-align: center;
            background-color: #fafafa;
            margin-top: 1rem;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📤</div>
            <h3 style="color: #666; margin: 0;">Drop your contract here</h3>
            <p style="color: #999; margin: 0.5rem 0 0 0;">
                Supported: PDF, PNG, JPG (up to 10MB)
            </p>
        </div>
        """, unsafe_allow_html=True)
