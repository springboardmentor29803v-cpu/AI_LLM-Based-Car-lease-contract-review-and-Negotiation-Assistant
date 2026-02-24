import streamlit as st
import requests

st.set_page_config(layout="wide")

st.markdown("""
<style>

.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
}


[data-testid="stSidebar"] {
    background-color: #0f172a;
}

[data-testid="stSidebar"] * {
    color: white !important;
}


.card {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}


.hero {
    padding: 40px;
    border-radius: 18px;
    background: linear-gradient(90deg, #1e3a8a, #2563eb);
    color: white;
    margin-bottom: 30px;
}

.metric-title {
    font-size: 14px;
    color: #6b7280;
    font-weight: 600;
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #111827;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    margin-bottom: 15px;
}
.card-title {
    font-size: 14px;
    color: #64748b;
}
.card-value {
    font-size: 22px;
    font-weight: bold;
    margin-top: 5px;
}
.card-red { border-left: 6px solid #ef4444; }
.card-yellow { border-left: 6px solid #f59e0b; }
.card-green { border-left: 6px solid #10b981; }
.card-blue { border-left: 6px solid #3b82f6; }

.hero {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    padding: 50px 30px;
    border-radius: 16px;
    color: white;
    margin-bottom: 30px;
}
.hero h1 {
    font-size: 36px;
    margin-bottom: 10px;
}
.hero p {
    font-size: 18px;
    opacity: 0.9;
}

.feature-card {
    background-color: white;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    text-align: center;
    margin-bottom: 20px;
}
.feature-title {
    font-size: 18px;
    font-weight: 600;
    margin-top: 10px;
}
.feature-desc {
    font-size: 14px;
    color: #64748b;
    margin-top: 5px;
}
[data-testid="stSidebar"] button[kind="secondary"] {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: white !important;
    border-radius: 10px;
    border: none;
    padding: 10px 14px;
    font-weight: 600;
    width: 100%;
    transition: all 0.25s ease;
    background: #ef4444;
    border-left: 4px solid #991b1b;
}

[data-testid="stSidebar"] button[kind="secondary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(239,68,68,0.35);
    background: linear-gradient(135deg, #dc2626, #b91c1c);
}

[data-testid="stSidebar"] button[kind="secondary"]:active {
    transform: scale(0.98);
}

.market-card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    text-align: center;
    transition: all 0.25s ease;
}

.market-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.10);
}

.market-title {
    font-size: 14px;
    color: #64748b;
    font-weight: 600;
}

.market-value {
    font-size: 28px;
    font-weight: 700;
    margin-top: 8px;
    color: #111827;
}

.market-green { border-top: 5px solid #10b981; }
.market-blue { border-top: 5px solid #3b82f6; }
.market-red { border-top: 5px solid #ef4444; }


.page-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    padding: 35px;
    border-radius: 18px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.06);
    margin-bottom: 30px;
    border-left: 6px solid #2563eb;
    transition: all 0.25s ease;
}

.page-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 18px 40px rgba(0,0,0,0.08);
}


.page-title {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #0f172a;
}


.page-subtitle {
    color: #64748b;
    margin-bottom: 25px;
    font-size: 15px;
}

.card-blue { border-left-color: #2563eb; }
.card-green { border-left-color: #10b981; }
.card-purple { border-left-color: #7c3aed; }
.card-orange { border-left-color: #f59e0b; }
.card-red { border-left-color: #ef4444; }
            


.hero-card {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    padding: 45px 35px;
    border-radius: 18px;
    color: white;
    margin-bottom: 30px;
    box-shadow: 0 15px 35px rgba(37,99,235,0.25);
}

.hero-title {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 17px;
    opacity: 0.9;
}

/* COLOR VARIANTS */

.hero-blue {
    background: linear-gradient(135deg,#2563eb, #4f46e5);
}

.hero-blue {
    background: linear-gradient(135deg, #059669, #10b981);
}

.hero-blue {
    background: linear-gradient(135deg, #6d28d9, #7c3aed);
}

.hero-blue {
    background: linear-gradient(135deg, #ea580c, #f59e0b);
            
}
.hero {
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    padding: 45px 35px;
    border-radius: 18px;
    color: white;
    margin-bottom: 30px;
    box-shadow: 0 15px 35px rgba(37, 99, 235, 0.25);
}

.hero h1 {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 8px;
}

.hero p {
    font-size: 17px;
    opacity: 0.92;
}
</style>
""", unsafe_allow_html=True)


if "active_contract" not in st.session_state:
    st.session_state.active_contract = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

if "messages" not in st.session_state:
    st.session_state.messages = []

def hero_page(title, subtitle="", color="blue"):
    st.markdown(f"""
        <div class="hero-card hero-{color}">
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def market_card(title, value, color="blue"):

    st.markdown(f"""
    <div class="market-card market-{color}">
        <div class="market-title">{title}</div>
        <div class="market-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def close_page_card():
    st.markdown("</div>", unsafe_allow_html=True)


st.sidebar.title("🚗 ContractCoach")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Contract Analysis", "Market Data", "VIN Lookup", "AI Assistant"]
)


if menu == "Dashboard":
    st.title("AI Lease & Loan Contract Analyzer")
    st.info("Upload and analyze a contract to begin.")
    st.markdown("""
    <div class="hero">
        <h1>🚗 ContractCoach AI</h1>
        <p>Smart Lease & Loan Analysis with Market Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🚀 Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            🔍
            <div class="feature-title">Contract Analysis</div>
            <div class="feature-desc">
            Extract 11 structured SLA fields instantly.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            💰
            <div class="feature-title">Market Comparison</div>
            <div class="feature-desc">
            Compare dealer price with real-time market valuation.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            ⚠️
            <div class="feature-title">Risk Detection</div>
            <div class="feature-desc">
            Identify high-risk clauses and negotiation points.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            🤖
            <div class="feature-title">AI Negotiation Assistant</div>
            <div class="feature-desc">
            Get India-focused negotiation strategies instantly.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("🛠 How It Works")

    step1, step2, step3 = st.columns(3)

    with step1:
        st.info("1️⃣ Upload your lease or loan contract PDF.")

    with step2:
        st.info("2️⃣ AI extracts terms, validates VIN & checks market value.")

    with step3:
        st.info("3️⃣ Get fairness score & negotiation guidance instantly.")


elif menu == "Contract Analysis":
    st.markdown(
    f"""
    <div class="hero">
        <h1>📄 Contract Analysis</h1>
        <p>Upload and analyze your lease or loan contract</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload your car lease or loan contract (PDF)",
        type=["pdf"]
    )

    if uploaded_file is not None:
        st.session_state.uploaded_filename = uploaded_file.name

    if st.session_state.uploaded_filename:
        st.success(f"📄 Uploaded File: {st.session_state.uploaded_filename}")

    # 🔍 ANALYZE BUTTON
    if uploaded_file is not None:
        if st.button("Analyze Contract", key="analyze_btn"):

            files = {"file": uploaded_file}
            response = requests.post("http://127.0.0.1:8001/upload", files=files)

            data = response.json()

            # Debug (remove later if you want)
            # st.write("DEBUG RESPONSE:", data)

            st.session_state.active_contract = data
            st.success("Analysis Complete!")
            st.rerun()

    if st.session_state.active_contract:

        active = st.session_state.active_contract
        sla = active.get("sla_data", {})


        st.header("Extracted SLA Fields")

        def safe_currency(value):
            return f"${value:,.0f}" if isinstance(value, (int, float)) else "None"

        def safe_percent(value):
            return f"{value:.2f}%" if isinstance(value, (int, float)) else "None"

        def card(title, value, color="blue"):
            st.markdown(f"""
            <div class="card card-{color}">
                <div class="card-title">{title}</div>
                <div class="card-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            card("Monthly Payment", safe_currency(sla.get("monthly_payment")), "blue")
            card("Down Payment", safe_currency(sla.get("down_payment")), "blue")
            card("APR", safe_percent(sla.get("interest_rate_apr")),
                 "red" if (sla.get("interest_rate_apr") or 0) > 10 else "green")
            card("Lease Term", sla.get("lease_term_months") or "None", "blue")
            card("Residual Value", safe_currency(sla.get("residual_value")), "blue")

        with col2:
            card("Buyout Price", safe_currency(sla.get("buyout_price")), "blue")
            card("Mileage Allowance", sla.get("mileage_allowance") or "None", "blue")
            card("Warranty", sla.get("warranty_coverage") or "None", "blue")
            card("Early Termination", sla.get("early_termination_fee") or "None", "yellow")

        with col3:
            card("VIN", sla.get("vin_number") or "None", "blue")
            card("Vehicle Make", sla.get("vehicle_make") or "None", "blue")
            card("Vehicle Model", sla.get("vehicle_model") or "None", "blue")
            card("Vehicle Year", sla.get("vehicle_year") or "None", "blue")

        st.markdown("---")


elif menu == "Market Data":
    hero_page(
        "💰 Market Analysis",
        "Compare dealer pricing against real market valuation",
        "green"
    )

    if not st.session_state.active_contract:
        st.warning("Upload and analyze a contract first.")
    else:

        active = st.session_state.active_contract
        sla = active.get("sla_data", {})

        dealer_price = active.get("dealer_market_price")
        market_price = active.get("market_average_price")
        fairness_score = active.get("fairness_score")
        difference = active.get("price_difference")
        verdict = active.get("verdict")


        st.header("Market Comparison")

        colA, colB, colC = st.columns(3)

        dealer_text = f"₹{dealer_price:,.0f}" if dealer_price else "None"
        market_text = f"₹{market_price:,.0f}" if market_price else "None"
        diff_text = f"₹{difference:,.0f}" if difference else "None"

        with colA:
            market_card("Dealer Price", dealer_text, "blue")

        with colB:
            market_card("Market Average", market_text, "green")

        with colC:
            color = "green" if difference and difference < 0 else "red"
            market_card("Price Difference", diff_text, color)


        st.markdown("### 🎯 Fairness Score")

        if fairness_score is not None:

            st.metric("Score", f"{fairness_score:.2f}%")
            st.progress(int(fairness_score))

            if verdict == "Excellent":
                st.success("🟢 Excellent Deal")
            elif verdict == "Fair":
                st.warning("🟡 Fair Deal")
            else:
                st.error("🔴 Overpriced")

        else:
            st.info("Market comparison not available.")

        st.markdown("---")

        if dealer_price and market_price:

            import plotly.graph_objects as go

            st.markdown("### 📊 Price Comparison Chart")

            fig = go.Figure()

            fig.add_bar(
                x=["Dealer Price"],
                y=[dealer_price],
                name="Dealer Price"
            )

            fig.add_bar(
                x=["Market Average"],
                y=[market_price],
                name="Market Average"
            )

            fig.update_layout(
                barmode="group",
                height=400,
                yaxis_title="Amount (₹)"
            )

            st.plotly_chart(fig, use_container_width=True)


elif menu == "VIN Lookup":

    hero_page(
        "🔎 VIN Lookup Report",
        "Decoded vehicle specifications & manufacturing data",
        "purple"
    )

    if not st.session_state.active_contract:
        st.warning("Analyze a contract first.")
    else:

        active = st.session_state.active_contract
        vin_data = active.get("vin_lookup", {})

        if not vin_data:
            st.info("No VIN information available.")
        else:

            st.header("Vehicle Identification Details")

         
            def vin_card(title, value):
                st.markdown(f"""
                <div class="card card-blue">
                    <div class="card-title">{title}</div>
                    <div class="card-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                vin_card("VIN", vin_data.get("vin") or "N/A")
                vin_card("Make", vin_data.get("make") or "N/A")
                vin_card("Model", vin_data.get("model") or "N/A")

            with col2:
                vin_card("Year", vin_data.get("year") or "N/A")
                vin_card("Body Class", vin_data.get("body_class") or "N/A")
                vin_card("Fuel Type", vin_data.get("fuel_type") or "N/A")

            with col3:
                vin_card("Engine", vin_data.get("engine") or "N/A")
                vin_card("Manufacturer", vin_data.get("manufacturer") or "N/A")
                vin_card("Plant Country", vin_data.get("plant_country") or "N/A")

            st.markdown("---")

            
            with st.expander("📄 Full VIN JSON"):
                st.json(vin_data)

elif menu == "AI Assistant":

    hero_page(
    "🤖 AI Negotiation Assistant",
    "Ask negotiation strategies tailored to your contract",
    "orange"
)

    if not st.session_state.active_contract:
        st.warning("Please analyze a contract first.")
    else:

        if len(st.session_state.messages) == 0:
            with st.chat_message("assistant"):
                st.write("I'm your negotiation assistant. Ask me about uploaded contract.")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input("Ask negotiation strategy...")

        if user_input:

            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })

            payload = {
                "contract_id": st.session_state.active_contract["contract_id"],
                "query": user_input
            }

            response = requests.post(
                "http://127.0.0.1:8001/chat",
                json=payload
            )

            result = response.json()
            reply = result.get("response", "No response")

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })

            st.rerun()



st.sidebar.markdown("---")

if st.session_state.active_contract:

    active = st.session_state.active_contract
    sla = active.get("sla_data", {})

    contract_id = active.get("contract_id", "N/A")
    filename = active.get("filename", "Uploaded Contract")

    vehicle = f"{sla.get('vehicle_year','')} {sla.get('vehicle_make','')} {sla.get('vehicle_model','')}"

    st.sidebar.markdown("### 🧾 Session Info")

    st.sidebar.markdown(f"""
    **Contract ID:** {contract_id}  

    **File:**  
    {filename}

    **Vehicle:**  
    {vehicle if vehicle.strip() else "Unknown"}

    **Chat messages:** {len(st.session_state.messages)}
    """)


    if st.sidebar.button("🔄 Reset Session",type="secondary"):
        st.session_state.active_contract = None
        st.session_state.messages = []
        st.rerun()

else:
    st.sidebar.info("No active session")
