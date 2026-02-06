import streamlit as st
import pandas as pd
from src.data_extraction import fetch_multiple_companies
from src.data_processing import FinancialMetricsCalculator, create_comparison_dataframe
from src.visualizations import (
    plot_revenue_trend, plot_margin_comparison, plot_fcf_trend,
    plot_financial_health_score, plot_metrics_over_time,
    create_financial_summary_table
)
from src.utils import cache_data, load_cached_data
import config

# Page configuration
st.set_page_config(
    page_title="Financial Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("📊 Financial Performance Dashboard")
st.markdown("### Comprehensive Analysis of Public Companies")

# Sidebar
st.sidebar.header("⚙️ Configuration")

# Company selection
default_companies = list(config.COMPANIES.keys())
selected_tickers = st.sidebar.multiselect(
    "Select Companies to Analyze",
    options=list(config.COMPANIES.keys()),
    default=default_companies,
    format_func=lambda x: f"{x} - {config.COMPANIES[x]}"
)

# Time period selection
quarterly_data = st.sidebar.checkbox("Use Quarterly Data", value=False)

# Refresh data button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.success("Cache cleared! Data will be refreshed.")

st.sidebar.markdown("---")
st.sidebar.info(
    "**About this Dashboard**\n\n"
    "This dashboard analyzes financial performance of public companies using "
    "real-time data from Yahoo Finance.\n\n"
    "📈 Metrics include revenue growth, margins, cash flow, and more."
)

# Main content
if not selected_tickers:
    st.warning("Please select at least one company from the sidebar.")
    st.stop()

# Load data with caching
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_financial_data(tickers, quarterly):
    """Load financial data with caching"""
    cache_file = f"financial_data_{'_'.join(tickers)}_{'Q' if quarterly else 'A'}.pkl"
    
    # Try to load from cache
    cached_data = load_cached_data(cache_file, cache_duration_hours=24)
    
    if cached_data is not None:
        return cached_data
    
    # Fetch fresh data
    data = fetch_multiple_companies(tickers, quarterly)
    
    # Cache the data
    cache_data(data, cache_file)
    
    return data

# Load data
with st.spinner("Loading financial data..."):
    try:
        companies_data = load_financial_data(selected_tickers, quarterly_data)
        st.success(f"✅ Data loaded for {len(selected_tickers)} companies")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "📈 Revenue Analysis", 
    "💰 Profitability", 
    "💵 Cash Flow",
    "🏢 Company Details"
])

# TAB 1: Overview
with tab1:
    st.header("Financial Overview")
    
    # Create comparison metrics
    try:
        comparison_df = create_comparison_dataframe(companies_data)
        
        # Display key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        for idx, row in comparison_df.iterrows():
            with col1:
                st.metric(
                    label=f"{row['Company']} Revenue Growth",
                    value=f"{row['Revenue Growth (%)']:.2f}%" if pd.notna(row['Revenue Growth (%)']) else "N/A"
                )
            with col2:
                st.metric(
                    label=f"{row['Company']} Gross Margin",
                    value=f"{row['Gross Margin (%)']:.2f}%" if pd.notna(row['Gross Margin (%)']) else "N/A"
                )
            with col3:
                st.metric(
                    label=f"{row['Company']} Operating Margin",
                    value=f"{row['Operating Margin (%)']:.2f}%" if pd.notna(row['Operating Margin (%)']) else "N/A"
                )
            with col4:
                st.metric(
                    label=f"{row['Company']} ROE",
                    value=f"{row['ROE (%)']:.2f}%" if pd.notna(row['ROE (%)']) else "N/A"
                )
        
        st.markdown("---")
        
        # Comparison table
        st.subheader("📋 Detailed Metrics Comparison")
        
        # Format the dataframe for display
        display_df = comparison_df.copy()
        
        # Round numeric columns
        numeric_cols = display_df.select_dtypes(include=['float64', 'int64']).columns
        display_df[numeric_cols] = display_df[numeric_cols].round(2)
        
        st.dataframe(display_df, use_container_width=True)
        
        # Financial Health Radar Chart
        st.subheader("🎯 Financial Health Score")
        fig_health = plot_financial_health_score(comparison_df)
        st.plotly_chart(fig_health, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating overview: {e}")

# TAB 2: Revenue Analysis
with tab2:
    st.header("Revenue Analysis")
    
    try:
        # Revenue trend chart
        fig_revenue = plot_revenue_trend(companies_data, selected_tickers)
        st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Revenue growth details
        st.subheader("Revenue Growth Details")
        
        col1, col2 = st.columns(2)
        
        for idx, ticker in enumerate(selected_tickers):
            calculator = FinancialMetricsCalculator(
                companies_data[ticker]['income_statement'],
                companies_data[ticker]['balance_sheet'],
                companies_data[ticker]['cash_flow']
            )
            
            revenue_growth = calculator.calculate_revenue_growth()
            
            with col1 if idx % 2 == 0 else col2:
                st.markdown(f"**{ticker} - {config.COMPANIES[ticker]}**")
                
                if not revenue_growth.empty:
                    growth_df = pd.DataFrame({
                        'Year': revenue_growth.index,
                        'Growth (%)': revenue_growth.values
                    }).round(2)
                    
                    st.dataframe(growth_df, use_container_width=True)
                else:
                    st.warning(f"No revenue growth data available for {ticker}")
        
    except Exception as e:
        st.error(f"Error in revenue analysis: {e}")

# TAB 3: Profitability
with tab3:
    st.header("Profitability Analysis")
    
    try:
        # Margin comparison
        comparison_df = create_comparison_dataframe(companies_data)
        fig_margins = plot_margin_comparison(comparison_df)
        st.plotly_chart(fig_margins, use_container_width=True)
        
        # Margin trends over time
        st.subheader("Margin Trends Over Time")
        
        selected_company = st.selectbox(
            "Select Company",
            selected_tickers,
            format_func=lambda x: f"{x} - {config.COMPANIES[x]}"
        )
        
        if selected_company:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_gross = plot_metrics_over_time(
                    companies_data, selected_company, 'Gross Margin (%)'
                )
                if fig_gross:
                    st.plotly_chart(fig_gross, use_container_width=True)
            
            with col2:
                fig_operating = plot_metrics_over_time(
                    companies_data, selected_company, 'Operating Margin (%)'
                )
                if fig_operating:
                    st.plotly_chart(fig_operating, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in profitability analysis: {e}")

# TAB 4: Cash Flow
with tab4:
    st.header("Cash Flow Analysis")
    
    try:
        # FCF trend
        fig_fcf = plot_fcf_trend(companies_data, selected_tickers)
        st.plotly_chart(fig_fcf, use_container_width=True)
        
        # Cash flow details
        st.subheader("Free Cash Flow Details")
        
        for ticker in selected_tickers:
            with st.expander(f"{ticker} - {config.COMPANIES[ticker]}"):
                calculator = FinancialMetricsCalculator(
                    companies_data[ticker]['income_statement'],
                    companies_data[ticker]['balance_sheet'],
                    companies_data[ticker]['cash_flow']
                )
                
                fcf = calculator.calculate_free_cash_flow()
                
                if not fcf.empty:
                    fcf_df = pd.DataFrame({
                        'Year': fcf.index,
                        'Free Cash Flow': fcf.values
                    })
                    
                    fcf_df['Free Cash Flow'] = fcf_df['Free Cash Flow'].apply(
                        lambda x: f"${x:,.0f}"
                    )
                    
                    st.dataframe(fcf_df, use_container_width=True)
                else:
                    st.warning(f"No FCF data available for {ticker}")
        
    except Exception as e:
        st.error(f"Error in cash flow analysis: {e}")

# TAB 5: Company Details
with tab5:
    st.header("Company Details")
    
    selected_company_detail = st.selectbox(
        "Select Company for Details",
        selected_tickers,
        format_func=lambda x: f"{x} - {config.COMPANIES[x]}",
        key="company_detail_select"
    )
    
    if selected_company_detail:
        try:
            company_info = companies_data[selected_company_detail]['company_info']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Company Information")
                st.write(f"**Name:** {company_info.get('longName', 'N/A')}")
                st.write(f"**Sector:** {company_info.get('sector', 'N/A')}")
                st.write(f"**Industry:** {company_info.get('industry', 'N/A')}")
                st.write(f"**Country:** {company_info.get('country', 'N/A')}")
                st.write(f"**Website:** {company_info.get('website', 'N/A')}")
                st.write(f"**Employees:** {company_info.get('fullTimeEmployees', 'N/A'):,}")
            
            with col2:
                st.subheader("Market Data")
                st.write(f"**Market Cap:** ${company_info.get('marketCap', 0):,.0f}")
                st.write(f"**Enterprise Value:** ${company_info.get('enterpriseValue', 0):,.0f}")
                st.write(f"**P/E Ratio:** {company_info.get('trailingPE', 'N/A')}")
                st.write(f"**Forward P/E:** {company_info.get('forwardPE', 'N/A')}")
                st.write(f"**Beta:** {company_info.get('beta', 'N/A')}")
            
            st.markdown("---")
            
            # Financial summary table
            st.subheader("Financial Metrics Summary")
            summary_table = create_financial_summary_table(companies_data, selected_company_detail)
            st.dataframe(summary_table, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading company details: {e}")

# Footer
st.markdown("---")
st.markdown(
    "**Data Source:** Yahoo Finance via yfinance | "
    "**Refresh Rate:** Data cached for 1 hour | "
    "**Developer:** Archit Kiran Kumar"
)