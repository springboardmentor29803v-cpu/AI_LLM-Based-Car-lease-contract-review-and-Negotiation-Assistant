import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(page_title="ContractClarity AI", layout="wide", initial_sidebar_state="expanded")

# 2. Advanced CSS Injection (The "Look")
st.markdown("""
<style>

/* ===== GLOBAL APP STYLING ===== */
.stApp {
    background-color: #f4f6f9;
    font-family: 'Inter', sans-serif;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background-color: #0f172a;
    padding-top: 30px;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* Sidebar radio buttons */
div[role="radiogroup"] label {
    font-weight: 500;
    margin-bottom: 10px;
}

/* ===== HEADERS ===== */
h1, h2, h3 {
    color: #1e293b;
}

/* ===== CARD CONTAINER ===== */
.card {
    background: #ffffff;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

/* ===== METRIC STYLE ===== */
[data-testid="stMetric"] {
    background: #ffffff;
    padding: 15px;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}

/* ===== CHAT UI ===== */
.chat-container {
    max-width: 850px;
    margin: auto;
}

.chat-bubble-user {
    background: #fee2e2;
    padding: 14px;
    border-radius: 14px;
    margin-bottom: 10px;
    border-left: 5px solid #ef4444;
}

.chat-bubble-ai {
    background: #e0f2fe;
    padding: 14px;
    border-radius: 14px;
    margin-bottom: 10px;
    border-left: 5px solid #3b82f6;
}

</style>
""", unsafe_allow_html=True)


# 3. Sidebar Navigation (Matches Video Sample)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/950/950154.png", width=80) # Placeholder Logo
    st.title("ContractClarity")
    st.markdown("---")
    menu = st.radio("NAVIGATION", ["Dashboard", "Contract Analysis", "VIN Lookup", "Negotiate"])

# --- DASHBOARD / SUMMARY VIEW ---
if menu == "Dashboard":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("Deal Overview")

    if "active_contract" in st.session_state:
        data = st.session_state["active_contract"]
        sla = data.get("sla_data", {})

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Monthly Payment", f"₹{sla.get('monthly_payment', 'N/A')}")
        with col2: st.metric("Interest (APR)", f"{sla.get('interest_rate_apr', 'N/A')}%")
        with col3: st.metric("Total Term", f"{sla.get('lease_term_months', 'N/A')} Mo")
        with col4: st.metric("Down Payment", f"₹{sla.get('down_payment', 'N/A')}")
    else:
        st.info("Upload a contract to view analysis.")

    st.markdown("</div>", unsafe_allow_html=True)


# --- CONTRACT ANALYSIS (UPLOAD) ---
elif menu == "Contract Analysis":
    st.header("Upload Agreement")

    uploaded_file = st.file_uploader(
        "Drag and drop your PDF here",
        type=["pdf"]
    )

    if uploaded_file:
        st.success(f"File selected: {uploaded_file.name}")

        # BIG ANALYZE BUTTON
        if st.button("🚀 Analyze Contract", use_container_width=True):

            with st.spinner("Analyzing contract with AI..."):

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                response = requests.post(
                    "http://127.0.0.1:8001/upload",
                    files=files
                )

                if response.status_code == 200:
                    result = response.json()
                    st.session_state["active_contract"] = result
                    st.success("Analysis Complete!")
                else:
                    st.error("Backend error during analysis.")

    # ---- SHOW RESULTS AFTER ANALYSIS ----
    if "active_contract" in st.session_state:

        data = st.session_state["active_contract"]
        sla = data.get("sla_data", {})

        st.markdown("## 📊 Extracted SLA Fields")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("APR", f"{sla.get('interest_rate_apr', 'N/A')}%")
            st.metric("Lease Term", f"{sla.get('lease_term_months', 'N/A')} months")
            st.metric("Monthly Payment", f"₹{sla.get('monthly_payment', 'N/A')}")

        with col2:
            st.metric("Down Payment", f"₹{sla.get('down_payment', 'N/A')}")
            st.metric("Mileage Allowance", sla.get("mileage_allowance", "N/A"))
            st.metric("Buyout Price", f"₹{sla.get('buyout_price', 'N/A')}")


# --- NEGOTIATE (THE CHATBOT) ---
elif menu == "Negotiate":
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.header("AI Negotiation Coach")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-bubble-user'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-ai'>{msg['content']}</div>", unsafe_allow_html=True)

    prompt = st.chat_input("Ask a negotiation question...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        payload = {
            "contract_id": st.session_state["active_contract"]["contract_id"],
            "query": prompt
        }

        response = requests.post("http://127.0.0.1:8001/chat", json=payload)
        reply = response.json().get("response")

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "VIN Lookup":
    st.header("Vehicle Intelligence Report")

    if "active_contract" not in st.session_state:
        st.warning("Upload and analyze a contract first.")
    else:
        vin_data = st.session_state["active_contract"].get("vin_lookup")

        if not vin_data:
            st.warning("VIN data not available.")
        elif vin_data.get("message"):
            st.warning("VIN not found in contract.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.metric("VIN", vin_data.get("vin"))
                st.metric("Make", vin_data.get("make"))
                st.metric("Model", vin_data.get("model"))

            with col2:
                st.metric("Year", vin_data.get("year"))
                st.metric("Open Recalls", vin_data.get("recall_count"))

