"""Market Analysis page for ContractCoach."""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from services.api_service import APIService


# Color palette
COLORS = {
    'primary': '#1E3A5F',
    'secondary': '#3B82F6',
    'accent': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'background': '#F8FAFC',
    'card': '#FFFFFF',
    'text': '#1F2937',
    'text_muted': '#6B7280',
    'border': '#E5E7EB',
    'chart_colors': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
}


def fetch_market_analysis_api(contract_id: int):
    """Fetch market analysis data from backend API."""
    result = APIService.get_market_analysis(contract_id)
    return result


def get_market_data_cached(contract_id: int, force_refresh: bool = False):
    """
    Get market analysis data with session-based caching.
    Data persists for the entire session unless manually refreshed.
    """
    cache_key = f"market_analysis_{contract_id}"
    
    # Return cached data if available and refresh not requested
    if not force_refresh and cache_key in st.session_state:
        return st.session_state[cache_key]
    
    # Fetch from API
    result = fetch_market_analysis_api(contract_id)
    
    # Store in session state for persistence
    st.session_state[cache_key] = result
    
    # Log currency info for debugging
    print(f"[Market Analysis] Currency: {result.get('currency', 'N/A')}, Symbol: {result.get('currency_symbol', 'N/A')}")
    
    return result


def format_currency(value: float, symbol: str = "$", decimals: int = 0) -> str:
    """Format currency with proper symbol and formatting."""
    if decimals == 0:
        return f"{symbol}{value:,.0f}"
    return f"{symbol}{value:,.{decimals}f}"


def render_price_comparison_chart(data: dict, currency_symbol: str = "$"):
    """Render bar chart comparing Dealer Price vs Market Average."""
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor(COLORS['card'])
    ax.set_facecolor(COLORS['card'])
    
    market_price_data = data.get('market_price_data', {})
    
    # Only show Dealer Price and Market Average
    labels = ['Dealer Price', 'Market Average']
    values = [
        data.get('contract_price', 0),
        market_price_data.get('market_average', 0)
    ]
    
    x = np.arange(len(labels))
    colors = [COLORS['primary'], COLORS['accent']]
    bars = ax.bar(x, values, color=colors, width=0.5, edgecolor='white', linewidth=1)
    
    ax.set_ylabel(f'Price ({currency_symbol})', fontsize=11, fontweight='bold', color=COLORS['text'])
    ax.set_title('Dealer Price vs Market Average', fontsize=14, fontweight='bold', color=COLORS['text'], pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11, color=COLORS['text'])
    ax.tick_params(axis='y', colors=COLORS['text_muted'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['bottom'].set_color(COLORS['border'])
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(format_currency(val, currency_symbol),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold', color=COLORS['text'])
    
    plt.tight_layout()
    return fig


def render_monthly_payment_chart(data: dict, currency_symbol: str = "$"):
    """Render bar chart comparing monthly payments."""
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor(COLORS['card'])
    ax.set_facecolor(COLORS['card'])
    
    labels = ['Contract Payment', 'Expected Payment']
    values = [
        data.get('contract_monthly_payment', 0),
        data.get('expected_monthly_payment', 0)
    ]
    
    x = np.arange(len(labels))
    colors = [COLORS['primary'], COLORS['accent']]
    bars = ax.bar(x, values, color=colors, width=0.5, edgecolor='white', linewidth=1)
    
    ax.set_ylabel(f'Monthly Payment ({currency_symbol})', fontsize=11, fontweight='bold', color=COLORS['text'])
    ax.set_title('Monthly Payment Comparison', fontsize=14, fontweight='bold', color=COLORS['text'], pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, color=COLORS['text'])
    ax.tick_params(axis='y', colors=COLORS['text_muted'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['bottom'].set_color(COLORS['border'])
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(format_currency(val, currency_symbol, 2),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color=COLORS['text'])
    
    plt.tight_layout()
    return fig


def render_cost_breakdown_chart(data: dict, currency_symbol: str = "$"):
    """Render bar chart showing cost breakdown."""
    cost_breakdown = data.get('cost_breakdown', {})
    
    fig, ax = plt.subplots(figsize=(7, 3.5))
    fig.patch.set_facecolor(COLORS['card'])
    ax.set_facecolor(COLORS['card'])
    
    labels = ['Vehicle Price', 'Interest Cost', 'Fees', 'Down Payment']
    values = [
        cost_breakdown.get('vehicle_price', 0),
        cost_breakdown.get('interest_cost', 0),
        cost_breakdown.get('fees', 0),
        cost_breakdown.get('down_payment', 0)
    ]
    
    x = np.arange(len(labels))
    colors = [COLORS['secondary'], COLORS['warning'], COLORS['danger'], COLORS['accent']]
    bars = ax.bar(x, values, color=colors, width=0.5, edgecolor='white', linewidth=1)
    
    ax.set_ylabel(f'Amount ({currency_symbol})', fontsize=11, fontweight='bold', color=COLORS['text'])
    ax.set_title('Lease Cost Breakdown', fontsize=14, fontweight='bold', color=COLORS['text'], pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, color=COLORS['text'])
    ax.tick_params(axis='y', colors=COLORS['text_muted'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['bottom'].set_color(COLORS['border'])
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(format_currency(val, currency_symbol, 2),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color=COLORS['text'])
    
    plt.tight_layout()
    return fig


def render_fairness_factors_chart(data: dict):
    """Render horizontal bar chart showing fairness factor scores."""
    fairness_factors = data.get('fairness_factors', {})
    
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor(COLORS['card'])
    ax.set_facecolor(COLORS['card'])
    
    labels = ['Price Score', 'APR Score', 'Fees Score', 'Term Score']
    values = [
        fairness_factors.get('price_score', 0),
        fairness_factors.get('apr_score', 0),
        fairness_factors.get('fees_score', 0),
        fairness_factors.get('term_score', 0)
    ]
    
    y = np.arange(len(labels))
    colors = [COLORS['secondary'] if v >= 70 else COLORS['warning'] if v >= 50 else COLORS['danger'] for v in values]
    bars = ax.barh(y, values, color=colors, height=0.5, edgecolor='white', linewidth=1)
    
    ax.set_xlabel('Score (out of 100)', fontsize=11, fontweight='bold', color=COLORS['text'])
    ax.set_title('Fairness Factor Breakdown', fontsize=14, fontweight='bold', color=COLORS['text'], pad=15)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10, color=COLORS['text'])
    ax.set_xlim(0, 110)
    ax.tick_params(axis='x', colors=COLORS['text_muted'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['bottom'].set_color(COLORS['border'])
    ax.xaxis.grid(True, linestyle='--', alpha=0.3)
    
    for bar, val in zip(bars, values):
        width = bar.get_width()
        ax.annotate(f'{val:.0f}',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0),
                    textcoords="offset points",
                    ha='left', va='center', fontsize=10, fontweight='bold', color=COLORS['text'])
    
    plt.tight_layout()
    return fig


def render_market_analysis():
    """Render the Market Analysis page."""
    
    # Custom CSS for professional styling
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; }
        .metric-card {
            background: white;
            padding: 1.25rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #E5E7EB;
            margin-bottom: 1rem;
            min-height: 120px;
        }
        .metric-label { color: #6B7280; font-size: 0.9rem; font-weight: 600; margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric-value { color: #1F2937; font-size: 1.75rem; font-weight: 700; margin: 0.5rem 0; }
        .metric-sub { color: #9CA3AF; font-size: 0.8rem; margin: 0; }
        .section-card {
            background: white;
            padding: 1rem 1.25rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #E5E7EB;
            margin-bottom: 1rem;
        }
        .section-title { color: #1F2937; font-size: 1.1rem; font-weight: 600; margin: 0 0 0.25rem 0; }
        .section-desc { color: #6B7280; font-size: 0.85rem; margin: 0; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1E3A5F 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
    ">
        <h1 style="color: white; margin: 0; font-size: 2rem;">Market Analysis</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Compare your contract against current market data
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for contract
    contract_id = st.session_state.get("contract_id")
    
    if not contract_id:
        st.warning("No contract uploaded. Please upload a contract first.")
        return
    
    # Refresh button - clears cache and refetches data
    col_refresh, col_spacer = st.columns([1, 5])
    with col_refresh:
        if st.button("Refresh Data"):
            # Clear session cache for this contract
            cache_key = f"market_analysis_{contract_id}"
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()
    
    # Check if data is already cached (no spinner needed)
    cache_key = f"market_analysis_{contract_id}"
    if cache_key in st.session_state:
        market_data = st.session_state[cache_key]
    else:
        # Silently fetch data - no spinner to avoid UI disruption
        market_data = get_market_data_cached(contract_id)
    
    if "error" in market_data:
        st.error("Market data temporarily unavailable.")
        st.info(f"Details: {market_data.get('error', 'Unknown error')}")
        return
    
    # Get currency symbol from API response
    currency_symbol = market_data.get('currency_symbol', '$')
    currency_code = market_data.get('currency', 'USD')
    
    # Key metrics row
    market_price_data = market_data.get('market_price_data', {})
    contract_price = market_data.get('contract_price', 0)
    market_avg = market_price_data.get('market_average', 0)
    fairness_score = market_data.get('fairness_score', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">Dealer Price</p>
            <p class="metric-value">{format_currency(contract_price, currency_symbol)}</p>
            <p class="metric-sub">From contract</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">Market Average</p>
            <p class="metric-value">{format_currency(market_avg, currency_symbol)}</p>
            <p class="metric-sub">Market estimate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        diff_pct = ((contract_price - market_avg) / market_avg * 100) if market_avg > 0 else 0
        diff_color = "#EF4444" if diff_pct > 0 else "#10B981"
        diff_sign = "+" if diff_pct > 0 else ""
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">Price Difference</p>
            <p class="metric-value" style="color: {diff_color};">{diff_sign}{diff_pct:.1f}%</p>
            <p class="metric-sub">vs market average</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        score_color = "#10B981" if fairness_score >= 75 else "#F59E0B" if fairness_score >= 60 else "#EF4444"
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">Fairness Score</p>
            <p class="metric-value" style="color: {score_color};">{fairness_score:.0f}/100</p>
            <p class="metric-sub">Overall rating</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Section 1: Price Comparison
    st.markdown("""
    <div class="section-card">
        <p class="section-title">Price Comparison</p>
        <p class="section-desc">Your contract price compared to current market listings</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        fig_price = render_price_comparison_chart(market_data, currency_symbol)
        st.pyplot(fig_price, use_container_width=True)
        plt.close(fig_price)
    
    with col_right:
        range_low = market_price_data.get('typical_range_low', 0)
        range_high = market_price_data.get('typical_range_high', 0)
        
        st.markdown(f"""
        <div style="background: #F0FDF4; padding: 1rem; border-radius: 8px; border-left: 4px solid #10B981;">
            <p style="margin: 0; font-weight: 600; color: #166534;">Market Range</p>
            <p style="margin: 0.5rem 0; color: #166534;">
                {format_currency(range_low, currency_symbol)} - {format_currency(range_high, currency_symbol)}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # Data sources
        data_sources = market_data.get('data_sources', [])
        if data_sources:
            st.markdown("**Data Sources**")
            for source in data_sources:
                st.markdown(f"- {source}")
    
    # Section 2: Monthly Payment
    st.markdown("""
    <div class="section-card">
        <p class="section-title">Monthly Payment Analysis</p>
        <p class="section-desc">Compare your monthly payment with expected market-based payment</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        fig_payment = render_monthly_payment_chart(market_data, currency_symbol)
        st.pyplot(fig_payment, use_container_width=True)
        plt.close(fig_payment)
    
    with col2:
        contract_pmt = market_data.get('contract_monthly_payment', 0)
        expected_pmt = market_data.get('expected_monthly_payment', 0)
        
        st.markdown(f"""
        <div style="background: #F8FAFC; padding: 1rem; border-radius: 8px;">
            <p style="margin: 0; color: #6B7280; font-size: 0.875rem;">Contract Payment</p>
            <p style="margin: 0; font-size: 1.5rem; font-weight: 700; color: #1E3A5F;">
                {format_currency(contract_pmt, currency_symbol, 2)}/mo
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        st.markdown(f"""
        <div style="background: #F8FAFC; padding: 1rem; border-radius: 8px;">
            <p style="margin: 0; color: #6B7280; font-size: 0.875rem;">Expected Payment</p>
            <p style="margin: 0; font-size: 1.5rem; font-weight: 700; color: #10B981;">
                {format_currency(expected_pmt, currency_symbol, 2)}/mo
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if expected_pmt > 0:
            diff = contract_pmt - expected_pmt
            if diff > 0:
                st.warning(f"You pay {format_currency(diff, currency_symbol, 2)} more per month")
            else:
                st.success(f"You save {format_currency(abs(diff), currency_symbol, 2)} per month")
    
    # Section 3: Cost Breakdown
    st.markdown("""
    <div class="section-card">
        <p class="section-title">Cost Breakdown</p>
        <p class="section-desc">Detailed breakdown of your total lease costs</p>
    </div>
    """, unsafe_allow_html=True)
    
    fig_cost = render_cost_breakdown_chart(market_data, currency_symbol)
    st.pyplot(fig_cost, use_container_width=True)
    plt.close(fig_cost)
    
    # Cost summary
    cost_breakdown = market_data.get('cost_breakdown', {})
    total_cost = sum([
        cost_breakdown.get('vehicle_price', 0),
        cost_breakdown.get('interest_cost', 0),
        cost_breakdown.get('fees', 0)
    ])
    
    st.info(f"Total financing cost (excluding down payment): {format_currency(total_cost, currency_symbol, 2)}")
    
    # Section 4: Fairness Score
    st.markdown("""
    <div class="section-card">
        <p class="section-title">Fairness Assessment</p>
        <p class="section-desc">Detailed breakdown of contract fairness factors</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get fairness factors for interpretation
    fairness_factors = market_data.get('fairness_factors', {})
    price_score_val = fairness_factors.get('price_score', 0)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # Adjust thresholds: Good >= 75, Fair >= 60, else Review Needed
        score_color = "#10B981" if fairness_score >= 75 else "#F59E0B" if fairness_score >= 60 else "#EF4444"
        score_bg = "#F0FDF4" if fairness_score >= 75 else "#FFFBEB" if fairness_score >= 60 else "#FEF2F2"
        score_label = "Good Deal" if fairness_score >= 75 else "Fair Deal" if fairness_score >= 60 else "Review Needed"
        
        st.markdown(f"""
        <div style="
            background: {score_bg};
            padding: 1.5rem;
            border-radius: 16px;
            text-align: center;
            border: 2px solid {score_color};
        ">
            <p style="margin: 0; font-size: 0.8rem; color: #6B7280;">Overall Score</p>
            <p style="margin: 0.25rem 0; font-size: 3rem; font-weight: 700; color: {score_color};">{fairness_score:.0f}</p>
            <p style="margin: 0; font-size: 0.95rem; font-weight: 600; color: {score_color};">{score_label}</p>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.7rem; color: #9CA3AF;">out of 100</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add interpretation below score card
        st.markdown("")
        if price_score_val == 0:
            st.error("Price is significantly above market value")
        elif price_score_val < 50:
            st.warning("Price is above market average")
        elif price_score_val >= 90:
            st.success("Price is at or below market value")
    
    with col2:
        fig_factors = render_fairness_factors_chart(market_data)
        st.pyplot(fig_factors, use_container_width=True)
        plt.close(fig_factors)
    
    # Vehicle Info
    vehicle_info = market_data.get('vehicle_info', {})
    if vehicle_info:
        make = vehicle_info.get('make', 'N/A')
        model = vehicle_info.get('model', 'N/A')
        year = vehicle_info.get('year', 'N/A')
        
        st.markdown(f"""
        <div style="
            background: #F8FAFC;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            display: flex;
            align-items: center;
        ">
            <span style="color: #6B7280; margin-right: 0.5rem;">Vehicle:</span>
            <span style="font-weight: 600; color: #1F2937;">{year} {make} {model}</span>
            <span style="margin-left: auto; background: #E5E7EB; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; color: #6B7280;">
                Currency: {currency_code}
            </span>
        </div>
        """, unsafe_allow_html=True)
