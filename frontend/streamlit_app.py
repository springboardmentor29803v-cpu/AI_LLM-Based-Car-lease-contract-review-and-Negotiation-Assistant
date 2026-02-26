import streamlit as st
import requests
import uuid
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="ContractClarity", 
    page_icon="📑", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Metric cards - gradient purple/pink */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #ff6b9d;
        margin-bottom: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        color: white;
    }
    
    .metric-card h4 {
        color: #fff;
        margin-bottom: 10px;
    }
    
    .metric-card p {
        color: rgba(255,255,255,0.95);
    }
    
    /* Upload area - vibrant cyan/blue */
    .upload-area {
        border: 3px dashed #00d4ff;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        margin: 20px 0;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .upload-area h3 {
        color: white;
    }
    
    .upload-area p {
        color: rgba(255,255,255,0.9);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Main content area */
    .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "contract_id" not in st.session_state:
    st.session_state.contract_id = None
if "contract_profile" not in st.session_state:
    st.session_state.contract_profile = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "sla_id" not in st.session_state:
    st.session_state.sla_id = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None

# --- HELPER FUNCTION ---
def generate_demo_response(prompt):
    """Generate demo responses when backend is unavailable"""
    prompt_lower = prompt.lower()
    
    # Get actual contract data if available
    sla = {}
    if st.session_state.contract_profile:
        sla = st.session_state.contract_profile.get('sla', {})
    
    # Use actual values from contract or "Not specified"
    apr = sla.get('apr_percent', 'Not specified')
    monthly = sla.get('monthly_payment', 'Not specified')
    mileage = sla.get('mileage_allowance_yr', 'Not specified')
    
    if "apr" in prompt_lower or "interest" in prompt_lower:
        return f"Your contract shows an APR of **{apr}**. Ask the dealer for the money factor calculation and mention you've received lower quotes from other lenders. Getting pre-approved from a credit union gives you strong leverage."
    elif "mileage" in prompt_lower:
        return f"Your contract has **{mileage}** miles/year. Buying extra miles upfront is 30-50% cheaper than paying overages later. Ask about the per-mile overage charge now."
    elif "monthly" in prompt_lower or "payment" in prompt_lower:
        return f"Your monthly payment is **{monthly}**. Ask for a full breakdown: cap cost, money factor, residual value, and all fees. Negotiate the vehicle price first before discussing payments."
    elif "hello" in prompt_lower or "hi" in prompt_lower:
        return "Hello! I'm your AI negotiation assistant. Ask me about APR, monthly payments, mileage, or any other lease terms you'd like help negotiating."
    else:
        return "For effective negotiation: research market prices on Edmunds and KBB, get multiple offers, know your credit score, and focus on the vehicle price before discussing monthly payments."

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #3B82F6;">📑 ContractClarity</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📄 Contract Analysis",  "📊 Market Intelligence","🆔 VIN Details", "💬 Negotiation Assistant"],
        index=0
    )
    
    st.markdown("---")
    
    if st.session_state.sla_id:
        st.success("✅ Contract Analyzed")
        st.caption(f"SLA: {str(st.session_state.sla_id)[:8]}...")

    else:
        st.warning("📄 No Contract")
    
    if st.session_state.analysis:
        st.success("✅ Market Data Ready")
    st.caption(f"User: {st.session_state.user_id[:8]}")
    st.caption(f"Date: {datetime.now().strftime('%d.%m.%Y')}")
# ==================== DASHBOARD ====================#
if menu == "🏠 Dashboard":
    st.markdown('<div style="text-align:center;padding:20px 0;"><h1>ContractClarity</h1><h3 style="color:#666;font-weight:normal;">AI-Powered Car Lease Analysis & Negotiation</h3></div>', unsafe_allow_html=True)

    col1, col2, col3,col4 = st.columns(4)
    with col1:
        st.markdown("""<div class="metric-card"><h4>📄 Step 1</h4><p><strong>Contract Analysis</strong><br>Upload your lease PDF to extract all SLA terms automatically.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="metric-card"><h4>📊 Step 2</h4><p><strong>Market Intelligence</strong><br>See dealer vs market price comparison and your fairness score.</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="metric-card"><h4>🆔 Step 3</h4><p><strong>VIN Details</strong><br>Look up vehicle details and recalls from NHTSA.</p></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""<div class="metric-card"><h4>💬 Step 4</h4><p><strong>Negotiation Assistant</strong><br>Get AI-powered talking points to secure the best deal.</p></div>""", unsafe_allow_html=True)

    st.markdown("---")
    if not st.session_state.sla_id:
        st.info("📁 No contract uploaded yet. Go to **Contract Analysis** to begin.")
    else:
        st.success("✅ Contract analyzed! Go to **Market Intelligence** to see price comparison.")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card"><h4>Document Status</h4><h2 style="color:#10B981;">✅ Analyzed</h2></div>', unsafe_allow_html=True)
        with col2:
            market_status = "✅ Ready" if st.session_state.analysis else "⏳ Pending"
            st.markdown(f'<div class="metric-card"><h4>Market Data</h4><h2>{market_status}</h2></div>', unsafe_allow_html=True)
        with col3:
            sla_count = sum(1 for v in st.session_state.contract_profile.get('sla', {}).values() if v not in (None, "", "N/A")) if st.session_state.contract_profile else 0
            st.markdown(f'<div class="metric-card"><h4>SLA Fields</h4><h2>{sla_count} extracted</h2></div>', unsafe_allow_html=True)

# ==================== CONTRACT ANALYSIS ====================#
elif menu == "📄 Contract Analysis":
    st.title("Contract Analysis")
    
    st.markdown("### Upload your car lease or loan contract")
    
    st.markdown("""
    <div class="upload-area">
        <h3 style="color: #3B82F6;">📁 Choose a file</h3>
        <p style="color: #666;">PDF, PNG, JPG up to 10MB</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drag and drop or click to browse",
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        file_size = uploaded_file.size / (1024 * 1024)
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #10B981;">
            <h4>📄 Selected File</h4>
            <p><strong>File Name:</strong> {uploaded_file.name}</p>
            <p><strong>File Size:</strong> {file_size:.2f} MB</p>
            <p><strong>Type:</strong> {uploaded_file.type.split('/')[-1].upper()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    
    if st.button("🚀 Analyze Contract", type="primary", disabled=not uploaded_file):
        with st.spinner("Analyzing contract terms..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                upload_response = requests.post(f"{BASE_URL}/negotiation/upload", files=files, timeout=30)
                
                if upload_response.status_code == 200:
                    upload_data = upload_response.json()
                    
                    st.session_state.sla_id = upload_data.get("sla_id")
                    
                    st.session_state.contract_profile = {
                        "sla": upload_data.get("sla_display", {})
                    }
                    st.session_state.thread_id = None
                    st.session_state.analysis = None
                    st.success("✅ Contract analyzed!")

                
                    # AUTO-FETCH market comparison
                    sla_id = st.session_state.sla_id
                    
                    if sla_id:
                        with st.spinner("Fetching market intelligence..."):
                            try:
                                resp = requests.post(
                                    f"{BASE_URL}/sla/{sla_id}/market-analysis",
                                    timeout=30
                                )
                                if resp.status_code == 200:
                                    st.session_state.analysis = resp.json()
                                    st.success("✅ Market data ready! Go to **📊 Market Intelligence** tab.")
                                else:
                                    st.warning(f"Market fetch failed: {resp.status_code} — {resp.text[:200]}")
                            except Exception as e:
                                st.warning(f"Market fetch error: {str(e)}")
                    
                    st.rerun()

                else:
                    st.error(f"Upload failed: {upload_response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if st.session_state.contract_profile and st.session_state.contract_profile.get('sla'):
        st.markdown("---")
        st.subheader("📋 Extracted Lease Terms")
        
        sla = st.session_state.contract_profile.get("sla", {})
        
        # Define EXACT SLA fields to show (from your requirements)
        sla_field_display = {
            
            "apr_percent": "APR (%)",
            "term_months": "Lease Term (months)",
            "monthly_payment": "Monthly Payment",
            "down_payment": "Down Payment", 
            "residual_value": "Residual Value",
            "mileage_allowance_yr": "Mileage/Year",
            "early_termination_fee": "Early Termination",
            "purchase_option_price": "Purchase Option",
            "late_fee_policy": "Late Fees",
        }

        cols = st.columns(3)
        
        field_count = 0
        
        for field_key, display_name in sla_field_display.items():
            # Get value from SLA data, or "N/A" if not found
            value = sla.get(field_key, "N/A")
            
            # Only show field if it has a value (not "N/A")
            if value not in ("N/A", None, ""):
                with cols[field_count % 3]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #666; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px;">
                            {display_name.upper()}
                        </div>
                        <div style="font-size: 1.2rem; font-weight: 700; color: #1F2937;">
                            {value}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                field_count += 1
        
        if field_count == 0:
            st.info("No SLA terms were extracted from the contract.")
    
        if st.session_state.analysis:
            st.success("✅ Market data is ready — go to **📊 Market Intelligence** tab to see price comparison and fairness score!")
        else:
            st.info("Market data not yet available.")
            if st.button("⚡ Fetch Market Data Now", type="secondary"):
                sla_id = st.session_state.sla_id
                if sla_id:
                    with st.spinner("Fetching..."):
                        try:
                            resp = requests.post(f"{BASE_URL}/sla/{sla_id}/market-analysis", timeout=30)
                            if resp.status_code == 200:
                                st.session_state.analysis = resp.json()
                                st.success("✅ Done! Go to 📊 Market Intelligence tab.")
                                st.rerun()
                            else:
                                st.error(f"Failed: {resp.status_code} — {resp.text[:200]}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

elif menu == "📊 Market Intelligence":
    st.title("📊 Market Intelligence & Fairness Score")

    if not st.session_state.sla_id:
        st.warning("⚠️ No contract uploaded yet. Go to **Contract Analysis** first.")
        st.stop()

    # Fetch if not already fetched
    if not st.session_state.analysis:
        st.info("Market data not loaded yet. Fetching now...")
        with st.spinner("Fetching market comparison..."):
            try:
                resp = requests.post(f"{BASE_URL}/sla/{st.session_state.sla_id}/market-analysis", timeout=30)
                if resp.status_code == 200:
                    st.session_state.analysis = resp.json()
                    st.rerun()
                else:
                    st.error(f"Failed to fetch market data: {resp.status_code} — {resp.text[:300]}")
                    st.stop()
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.stop()

    analysis = st.session_state.analysis

    def parse_price(val):
        return float(str(val).replace('₹', '').replace(',', '').replace(' ', '').strip())

    dealer_price = parse_price(analysis['dealer_price'])
    market_price = parse_price(analysis['market_price'])
    score_raw = analysis.get('fairness_score', '0/100')
    score = int(str(score_raw).split('/')[0])
    insight = analysis.get('insight', '')
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:#EFF6FF;border-radius:12px;padding:20px;text-align:center;border-top:4px solid #3B82F6;">
            <div style="font-size:0.85rem;color:#6B7280;margin-bottom:8px;">DEALER PRICE</div>
            <div style="font-size:1.8rem;font-weight:800;color:#3B82F6;">₹{dealer_price:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:#F0FDF4;border-radius:12px;padding:20px;text-align:center;border-top:4px solid #10B981;">
            <div style="font-size:0.85rem;color:#6B7280;margin-bottom:8px;">MARKET PRICE</div>
            <div style="font-size:1.8rem;font-weight:800;color:#10B981;">₹{market_price:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("💰 Dealer Price vs Market Price")
        chart_data = pd.DataFrame({
            'Price Type': ['Dealer Price', 'Market price'],
            'Amount': [dealer_price, market_price]
        })
        fig1 = px.bar(
            chart_data, x='Price Type', y='Amount',
            color='Price Type',
            color_discrete_map={'Dealer Price': '#EF4444', 'Market price': '#10B981'},
            text='Amount',
            height=420
        )
        fig1.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside', textfont_size=14)
        fig1.update_layout(
            showlegend=False,
            yaxis_tickformat=',.0f',
            yaxis_title='Price (₹)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📈 Fairness Score")

        bar_color = '#10B981' if score >= 70 else '#F59E0B' if score >= 40 else '#EF4444'
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Fairness Score", 'font': {'size': 18}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2},
                'bar': {'color': bar_color},
                'steps': [
                    {'range': [0, 40], 'color': '#FEE2E2'},
                    {'range': [40, 70], 'color': '#FEF3C7'},
                    {'range': [70, 100], 'color': '#D1FAE5'},
                ],
                'threshold': {
                    'line': {'color': bar_color, 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        fig_gauge.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font=dict(size=14))
        st.plotly_chart(fig_gauge, use_container_width=True)

        label = "🟢 Great Deal!" if score >= 70 else "🟡 Room to Negotiate" if score >= 40 else "🔴 Overpriced"
        st.markdown(f"<h2 style='text-align:center;margin-top:0;'>{label}</h2>", unsafe_allow_html=True)

        diff = market_price - dealer_price
        diff_color = '#10B981' if diff > 0 else '#EF4444'
        diff_label = 'BELOW market 🎉' if diff > 0 else 'ABOVE market ⚠️'
        st.markdown(f"""
        <div style="text-align:center;background:#F8FAFC;border-radius:12px;padding:16px;margin-top:10px;border:2px solid {diff_color};">
            <div style="font-size:0.9rem;color:#6B7280;">You are paying</div>
            <div style="font-size:1.8rem;font-weight:800;color:{diff_color};">₹{abs(diff):,.0f}</div>
            <div style="font-size:0.95rem;color:{diff_color};font-weight:600;">{diff_label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📊 Market Price Ranges vs Your Deal")

    range_data = pd.DataFrame({
        'Category': ['Market Low\n(-15%)', 'Market price', 'Market High\n(+15%)', 'Your Dealer Price'],
        'Price': [market_price * 0.85, market_price, market_price * 1.15, dealer_price],
        'Color': ['#F59E0B', '#10B981', '#EF4444', '#8B5CF6']
    })

    fig2 = px.bar(
        range_data, x='Category', y='Price',
        color='Category',
        color_discrete_map={
            'Market Low\n(-15%)': '#F59E0B',
            'Market price': '#10B981',
            'Market High\n(+15%)': '#EF4444',
            'Your Dealer Price': '#8B5CF6'
        },
        text='Price',
        height=480
    )
    fig2.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside', textfont_size=13)
    fig2.update_layout(
        showlegend=False,
        yaxis_tickformat=',.0f',
        yaxis_title='Price (₹)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14)
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Insight banner ──
    st.markdown("---")
    insight_color = '#D1FAE5' if diff > 0 else '#FEE2E2'
    border_color = '#10B981' if diff > 0 else '#EF4444'
    st.markdown(f"""
    <div style="background:{insight_color};border-left:6px solid {border_color};border-radius:8px;padding:20px;font-size:1.1rem;font-weight:600;">
        💡 {insight}
    </div>
    """, unsafe_allow_html=True)

    if diff > 0:
        st.balloons()
    st.markdown("---")
    st.subheader("📊 Score Breakdown")
    
    breakdown = analysis.get('score_breakdown', {})
    
    if breakdown:
        # Create data for bar chart
        components = ['Price (40%)', 'APR (25%)', 'Fees (15%)', 'Term (20%)']
        scores = [
            breakdown.get('price_score', 0),
            breakdown.get('apr_score', 0),
            breakdown.get('fees_score', 0),
            breakdown.get('term_score', 0)
        ]
        colors = ['#3B82F6', '#F59E0B', '#10B981', '#8B5CF6']
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        for i, (comp, score, color) in enumerate(zip(components, scores, colors)):
            fig.add_trace(go.Bar(
                y=[comp],
                x=[score],
                name=comp,
                orientation='h',
                marker=dict(color=color),
                text=[f"{score}%"],
                textposition='outside',
                textfont=dict(size=14)
            ))
        
        fig.update_layout(
            title="Component Scores",
            xaxis=dict(
                title="Score (%)",
                range=[0, 100],
                gridcolor='#E5E7EB',
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title="",
                tickfont=dict(size=14)
            ),
            barmode='group',
            height=300,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=150, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        # Insight box based on lowest score
        lowest_score = min(scores)
        lowest_component = components[scores.index(lowest_score)]

        if lowest_score < 85:
            st.markdown(f"""
            <div style="background:#FEF3C7;border-left:6px solid #F59E0B;border-radius:8px;padding:16px;margin-top:10px;">
            <strong>💡 Negotiation Tip:</strong> Your weakest area is <strong>{lowest_component}</strong> 
            with a score of <strong>{lowest_score}</strong>. 
            Focus your negotiation on improving this term for the best outcome.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#D1FAE5;border-left:6px solid #10B981;border-radius:8px;padding:16px;margin-top:10px;">
            <strong>✅ All Good!</strong> All components score above 85. Your contract terms are fair across the board.
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Refresh Market Data", type="secondary"):
        with st.spinner("Refreshing..."):
            try:
                resp = requests.post(f"{BASE_URL}/sla/{st.session_state.sla_id}/market-analysis", timeout=30)
                if resp.status_code == 200:
                    st.session_state.analysis = resp.json()
                    st.rerun()
                else:
                    st.error(f"Failed: {resp.text[:200]}")
            except Exception as e:
                st.error(f"Error: {str(e)}")


# ==================== VIN DETAILS ====================
elif menu == "🆔 VIN Details":
    st.title("Vehicle Intelligence")
    
    if not st.session_state.contract_profile:
        st.warning("Please upload a contract first in the Contract Analysis tab.")
    else:
        p = st.session_state.contract_profile
        
        # Manual VIN lookup
        st.markdown("### Enter VIN Number")
        vin = st.text_input("17-digit VIN", placeholder="1HGCM82633A123456")
        
        if st.button("🔍 Lookup VIN", type="primary") and vin:
            if len(vin) != 17:
                st.error("VIN must be exactly 17 characters")
            elif not vin.isalnum():
                st.error("VIN must contain only letters and numbers")
            else:
                with st.spinner("Checking NHTSA database..."):
                    try:
                        response = requests.get(
                            f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json",
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            results = data.get("Results", [])
                            
                            if results:
                                # Get values - will be empty string if not found
                                make = next((r["Value"] for r in results if r["Variable"] == "Make"), "")
                                model = next((r["Value"] for r in results if r["Variable"] == "Model"), "")
                                year = next((r["Value"] for r in results if r["Variable"] == "Model Year"), "")

                                vehicle_type = next((r["Value"] for r in results if r["Variable"] == "Vehicle Type"), "")
                                fuel_type = next((r["Value"] for r in results if r["Variable"] == "Fuel Type - Primary"), "")
                                engine = next((r["Value"] for r in results if r["Variable"] == "Displacement (L)"), "")
                                
                                doors = next((r["Value"] for r in results if r["Variable"] == "Doors"), "")
                                plant_country = next((r["Value"] for r in results if r["Variable"] == "Plant Country"), "")
                                
                                # Show N/A if value is empty (dummy VIN)
                                col1, col2, col3 = st.columns(3)
                                col1.metric("Make", make or "N/A")
                                col2.metric("Model", model or "N/A")
                                col3.metric("Year", year or "N/A")

                                col1, col2, col3 = st.columns(3)
                                col1.metric("Type", vehicle_type or "N/A")
                                col2.metric("Fuel Type", fuel_type or "N/A")
                                col3.metric("Engine (L)", engine or "N/A")

                                col1, col2 = st.columns(2)
                                col1.metric("Doors", doors or "N/A")
                                col2.metric("Made In", plant_country or "N/A")
                                
                                # Show warning for dummy VIN
                                if not make and not model:
                                    st.warning("⚠️ This appears to be a dummy or invalid VIN")
                            else:
                                st.error("❌ No data returned for this VIN")
                                st.info("This VIN may be invalid or dummy.")
                        else:
                            st.error("Failed to connect to NHTSA database")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to NHTSA database. Please check your internet connection.")
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except Exception as e:
                        st.error(f"Failed to lookup VIN: {str(e)}")

# ==================== NEGOTIATION ASSISTANT ====================
elif menu == "💬 Negotiation Assistant":
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #1F2937; margin-bottom: 10px;">AI Negotiation Assistant</h1>
        <h3 style="color: #6B7280; font-weight: normal; margin-bottom: 20px;">
            Get real-time suggestions and talking points to secure the best deal.
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Check if contract uploaded
    if not st.session_state.sla_id:
        st.warning("⚠️ **No contract uploaded yet!**")
        st.info("Please upload your lease agreement in the **Contract Analysis** tab first.")
    else:
        st.markdown('<div style="text-align:center;color:#666;padding:15px;font-style:italic;background:#F8FAFC;border-radius:8px;margin:20px 0;">Based on your lease contract and market data.</div>', unsafe_allow_html=True)
        st.markdown("---")

        if not st.session_state.chat_history:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "I'm your negotiation assistant. Ask me for talking points, questions to ask the dealer, or how to respond to common dealer tactics."
            })

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""<div style="background:#F3F4F6;padding:20px;border-radius:10px;margin:10px 0;border-left:4px solid #10B981;"><p style="font-size:1rem;color:#1F2937;margin:0;">{msg["content"]}</p></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style="background:#F0F9FF;padding:20px;border-radius:10px;margin:10px 0;border-left:4px solid #3B82F6;"><p style="font-size:1rem;color:#1F2937;margin:0;">{msg["content"]}</p></div>""", unsafe_allow_html=True)

        st.markdown("---")

        if prompt := st.chat_input("Ask for negotiation tips..."):
            if st.session_state.thread_id is None:
                with st.spinner("Running negotiation analysis..."):
                    try:
                        negotiate_response = requests.post(
                            f"{BASE_URL}/negotiate/sla/{st.session_state.sla_id}", timeout=30
                        )
                        if negotiate_response.status_code == 200:
                            data = negotiate_response.json()
                            st.session_state.thread_id = data.get("thread_id")
                        else:
                            st.error("Failed to run negotiation analysis")
                            st.stop()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.stop()

            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.spinner("Getting response..."):
                try:
                    chat_response = requests.post(
                        f"{BASE_URL}/chat/{st.session_state.thread_id}",
                        json={"message": prompt},
                        timeout=30
                    )
                    if chat_response.status_code == 200:
                        ai_response = chat_response.json().get("response", "I couldn't generate a response.")
                    else:
                        ai_response = generate_demo_response(prompt)
                except Exception:
                    ai_response = generate_demo_response(prompt)

            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()

        if st.session_state.thread_id and len(st.session_state.chat_history) > 1:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🗑️ Clear Chat History", use_container_width=True):
                    st.session_state.chat_history = []
                    st.session_state.thread_id = None
                    st.rerun()
        

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>📑 <strong>ContractClarity</strong> • AI-Powered Lease Analysis</p>
</div>
""", unsafe_allow_html=True)

