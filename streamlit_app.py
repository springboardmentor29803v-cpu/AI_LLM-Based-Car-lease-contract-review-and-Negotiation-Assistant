# streamlit_app.py
import streamlit as st
import requests
import plotly.graph_objects as go

API = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="ContractCoach",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 🎨 GLOBAL CSS (CLEAN & CONSISTENT)
# =====================================================
st.markdown("""
<style>

.hero {
    background: linear-gradient(135deg,#0f1f3d,#1f4ed8);
    padding: 40px;
    border-radius: 18px;
    color: white;
}

.card {
    height: 130px;
    border-radius: 16px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    font-weight: 600;
}

.pink { background:#ffe6ea; color:black; }
.yellow { background:#fff3cd; color:black; }
.blue { background:#1f5edb; color:white; }

.big { font-size:22px; font-weight:700; }
.small { font-size:13px; opacity:0.9; }

[data-testid="stSidebar"] {
    background:#0f1f3d;
}
[data-testid="stSidebar"] * {
    color:white !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# 🌙 SIDEBAR
# =====================================================
st.sidebar.title("🚗 ContractCoach")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Contract Analysis",
        "VIN Lookup",
        "Market Analysis",
        "AI Assistant"
    ]
)

# =====================================================
# 🏠 DASHBOARD
# =====================================================
if page == "Dashboard":

    st.markdown("""
    <div class="hero">
    <h1>🚗 ContractCoach</h1>
    <h3>Your AI-Powered Car Contract Negotiation Assistant</h3>
    <p>Analyze contracts, compare market prices,
    detect risks, and negotiate smarter deals.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.subheader("🧐 What Can ContractCoach Do For You?")
    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    features = [
        "📄 Contract Analysis",
        "🔍 VIN Lookup",
        "💰 Market Price Checker",
        "🤖 AI Negotiation Assistant"
    ]

    for col, text in zip([c1, c2, c3, c4], features):
        col.markdown(f"""
        <div class="card pink">
            <div class="big">{text}</div>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# 📄 CONTRACT ANALYSIS
# =====================================================
elif page == "Contract Analysis":

    st.title("📄 Contract Analysis")

    file = st.file_uploader("Upload Lease / Loan Agreement", type=["pdf"])

    if file:

        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        r = requests.post(f"{API}/upload", files=files)

        result = r.json()
        data = result["contract_data"]
        cid = result["contract_id"]

        st.session_state["contract_id"] = cid
        st.success("Contract processed successfully")

        st.subheader("📑 Extracted Terms")
        st.write("")

        terms = [
            ("VIN", data.get("vin")),
            ("Make", data.get("vehicle_make")),
            ("Model", data.get("vehicle_model")),
            ("Year", data.get("vehicle_year")),
            ("APR", f"{data.get('apr')}%"),
            ("Monthly Payment", data.get("monthly_payment")),
            ("Down Payment", data.get("down_payment")),
            ("Lease Term", data.get("lease_term_months")),
            ("Mileage Allowance", data.get("mileage_allowance")),
            ("Dealer Price", data.get("dealer_price"))
        ]

        cols = st.columns(3)

        for i, (title, value) in enumerate(terms):
            cols[i % 3].markdown(f"""
            <div class="card pink">
                <div class="big">{value}</div>
                <div class="small">{title}</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.subheader("⭐ Analysis Summary")
        st.info("The financing structure appears moderate. APR and payment terms may be negotiable.")

        st.subheader("⭐ Next Steps")
        st.write("""
        • Verify vehicle details using VIN Lookup  
        • Compare dealer price with market average  
        • Use AI assistant to prepare negotiation strategy  
        """)

# =====================================================
# 🔍 VIN LOOKUP
# =====================================================
elif page == "VIN Lookup":

    st.title("🔍 VIN Lookup")

    vin = st.text_input("Enter VIN Number")

    if st.button("Get Vehicle Details"):

        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"
        r = requests.get(url)

        result = r.json()["Results"][0]

        details = [
            ("Year", result.get("ModelYear")),
            ("Make", result.get("Make")),
            ("Model", result.get("Model")),
            ("Body Type", result.get("BodyClass")),
            ("Fuel Type", result.get("FuelTypePrimary"))
        ]

        cols = st.columns(5)

        for col, (title, value) in zip(cols, details):
            col.markdown(f"""
            <div class="card yellow">
                <div class="big">{value}</div>
                <div class="small">{title}</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.info("You can use this vehicle information to negotiate better with our AI Assistant 🚘")

# =====================================================
# 💰 MARKET ANALYSIS (UNCHANGED — PERFECT)
# =====================================================
elif page == "Market Analysis":

    st.title("💰 Market Analysis")

    if "contract_id" not in st.session_state:
        st.warning("Upload contract first")
        st.stop()

    cid = st.session_state["contract_id"]

    market = requests.get(f"{API}/{cid}/market-price").json()
    contract = requests.get(f"{API}/{cid}").json()["contract_data"]

    dealer = market["contract_price_inr"]
    market_avg = market["market_price_inr"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=market["fairness_score"],
        title={'text': "Fairness Score"},
        gauge={'axis': {'range': [0, 100]}}
    ))

    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)

    price_cards = [
        ("Dealer Price", dealer),
        ("Market Avg", market_avg),
        ("Price Range",
         f"{market['min_price_inr']} - {market['max_price_inr']}")
    ]

    for col, (title, value) in zip([c1, c2, c3], price_cards):
        col.markdown(f"""
        <div class="card blue">
            <div class="big">{value}</div>
            <div class="small">{title}</div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("💳 Financial Structure")

    f1, f2, f3, f4 = st.columns(4)

    finance = [
        ("APR", f"{contract.get('apr')}%"),
        ("Monthly Payment", contract.get("monthly_payment")),
        ("Down Payment", contract.get("down_payment")),
        ("Vehicle Price", dealer)
    ]

    for col, (title, value) in zip([f1,f2,f3,f4], finance):
        col.markdown(f"""
        <div class="card blue">
            <div class="big">{value}</div>
            <div class="small">{title}</div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("📊 Dealer vs Market Price")

    fig2 = go.Figure()
    fig2.add_bar(name="Dealer", x=["Price"], y=[dealer])
    fig2.add_bar(name="Market", x=["Price"], y=[market_avg])
    fig2.update_layout(barmode='group')
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# 🤖 AI ASSISTANT (UNCHANGED)
# =====================================================
elif page == "AI Assistant":

    st.title("🤖 AI Negotiation Assistant")

    if "contract_id" not in st.session_state:
        st.warning("Upload contract first")
        st.stop()

    cid = st.session_state["contract_id"]

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask negotiation advice...")

    if prompt:

        st.session_state.chat.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        r = requests.get(f"{API}/{cid}/negotiate")
        ai_text = r.json()["ai_negotiation_advice"]

        st.session_state.chat.append(
            {"role": "assistant", "content": ai_text}
        )

        with st.chat_message("assistant"):
            st.markdown(ai_text)