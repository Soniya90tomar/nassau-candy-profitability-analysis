import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Page Configuration Setup
st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title & Description
st.title("🍬 Nassau Candy Distributor - Margin Performance & Profitability App")
st.markdown("This interactive web application provides strategic diagnostics into product-line margins, cost structures, and profit concentration risks.")

# 2. DATA LOADING & CLEANING LAYER (WITH CACHING)
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("Nassau Candy Distributor.csv")
    
    # Cleaning rows with invalid sales/units
    df = df[df['Sales'] > 0]
    df = df[df['Units'] > 0]
    df = df.dropna(subset=['Gross Profit'])
    
    # Strip spaces
    df['Division'] = df['Division'].str.strip()
    df['Product Name'] = df['Product Name'].str.strip()
    
    # Parse Date format securely
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d-%m-%Y', errors='coerce')
    
    # Base Metric Calculations
    df['Gross_Margin'] = df['Gross Profit'] / df['Sales']
    df['Profit_per_Unit'] = df['Gross Profit'] / df['Units']
    
    return df

# Initialize Data Safely
try:
    df = load_and_clean_data()
except Exception as e:
    st.error(f"Error loading CSV file: {e}. Please ensure 'Nassau_Candy_Distributor.csv' is in the same directory.")
    st.stop()

# 3. USER CAPABILITIES & INTERACTIVE SIDEBAR FILTERS
st.sidebar.header("🕹️ User Controls & Filters")

# Product Search Feature
search_query = st.sidebar.text_input("🔍 Product Search", "", help="Type product name to filter data")

# Division Multi-select Filter
all_divisions = sorted(list(df['Division'].unique()))
selected_divisions = st.sidebar.multiselect("📁 Select Division(s)", options=all_divisions, default=all_divisions)

# Date Range Selector
min_date = df['Order Date'].min().date() if not df['Order Date'].isnull().all() else pd.Timestamp('2024-01-01').date()
max_date = df['Order Date'].max().date() if not df['Order Date'].isnull().all() else pd.Timestamp('2026-12-31').date()

start_date, end_date = st.sidebar.date_input(
    "📅 Select Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Dynamic Margin Threshold Slider
margin_threshold_pct = st.sidebar.slider(
    "⚠️ Margin Risk Threshold (%)", 
    min_value=0, 
    max_value=100, 
    value=int(df['Gross_Margin'].mean() * 100),
    help="Set the below-average threshold to flag high-volume margin risks dynamically."
)
margin_threshold = margin_threshold_pct / 100.0

# Apply Interactive Filtering Logic
filtered_df = df.copy()

if selected_divisions:
    filtered_df = filtered_df[filtered_df['Division'].isin(selected_divisions)]

filtered_df = filtered_df[(filtered_df['Order Date'].dt.date >= start_date) & (filtered_df['Order Date'].dt.date <= end_date)]

if search_query:
    filtered_df = filtered_df[filtered_df['Product Name'].str.contains(search_query, case=False)]

if filtered_df.empty:
    st.warning("⚠️ No data matches your filter criteria. Please adjust your sidebar settings.")
    st.stop()

# Build Product Aggregations on Filtered Data
product_summary = filtered_df.groupby('Product Name')[['Sales', 'Units', 'Cost', 'Gross Profit']].sum()
product_summary['Gross_Margin'] = product_summary['Gross Profit'] / product_summary['Sales']
product_summary['Profit_per_Unit'] = product_summary['Gross Profit'] / product_summary['Units']

# 4. APPLICATION MODULES LAYOUT (TABS)
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Product Profitability", 
    "🏢 Division Performance", 
    "🎯 Cost-Margin Diagnostics", 
    "📊 Profit Concentration (Pareto)"
])

# ==========================================
# MODULE 1: PRODUCT PROFITABILITY OVERVIEW
# ==========================================
with tab1:
    st.header("📈 Product Profitability Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Product-Level Margin Leaderboard")
        leaderboard = product_summary.sort_values(by='Gross_Margin', ascending=False)[['Sales', 'Gross Profit', 'Gross_Margin']].head(10)
        leaderboard['Gross_Margin (%)'] = (leaderboard['Gross_Margin'] * 100).round(2)
        st.dataframe(leaderboard[['Sales', 'Gross Profit', 'Gross_Margin (%)']].style.format({"Sales": "${:,.2f}", "Gross Profit": "${:,.2f}"}))
        
    with col2:
        st.subheader("🥧 Profit Contribution Share")
        top_profit_contrib = product_summary.sort_values(by='Gross Profit', ascending=False).head(5)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(top_profit_contrib['Gross Profit'], labels=top_profit_contrib.index, autopct='%1.1f%%', 
               colors=sns.color_palette("muted"), startangle=140, textprops={'fontsize': 8})
        ax.axis('equal')
        plt.title("Top 5 Products Gross Profit Contribution Share", fontsize=10, fontweight='bold')
        st.pyplot(fig)

# ==========================================
# MODULE 2: DIVISION PERFORMANCE DASHBOARD
# ==========================================
with tab2:
    st.header("🏢 Division Performance Dashboard")
    
    division_summary = filtered_df.groupby('Division')[['Sales', 'Gross Profit']].sum()
    division_summary['Gross_Margin_%'] = (division_summary['Gross Profit'] / division_summary['Sales'] * 100).round(2)
    division_summary['Sales_Share_%'] = (division_summary['Sales'] / division_summary['Sales'].sum() * 100).round(2)
    division_summary['Profit_Share_%'] = (division_summary['Gross Profit'] / division_summary['Gross Profit'].sum() * 100).round(2)
    
    st.subheader("💡 Strategic Share Imbalance Reference Table")
    st.dataframe(division_summary[['Sales_Share_%', 'Profit_Share_%', 'Gross_Margin_%']].style.format("{:.2f}%"))
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Revenue vs Gross Profit Comparison")
        fig, ax = plt.subplots(figsize=(8, 5))
        division_summary[['Sales', 'Gross Profit']].plot(kind='bar', ax=ax, color=['#4C72B0', '#55A868'])
        plt.title("Total Sales vs. Gross Profit by Corporate Division")
        plt.ylabel("Amount ($)")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        
    with col2:
        st.subheader("🎯 Margin Distribution by Corporate Division")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=filtered_df, x='Division', y='Gross_Margin', palette="Set2", ax=ax)
        plt.title("Gross Margin Distribution Across Order Profiles")
        plt.ylabel("Gross Margin Ratio")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)

# ==========================================
# MODULE 3: COST VS MARGIN DIAGNOSTICS
# ==========================================
with tab3:
    st.header("🎯 Cost vs. Margin Diagnostics Matrix")
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📉 Cost-Sales Scatter Matrix")
        fig, ax = plt.subplots(figsize=(10, 6))
        scatter = ax.scatter(
            product_summary['Sales'], 
            product_summary['Cost'], 
            c=product_summary['Gross_Margin'] * 100, 
            cmap='RdYlGn', 
            alpha=0.8, 
            edgecolors='k', 
            s=100
        )
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label('Gross Margin (%)', fontweight='bold')
        ax.set_title('Cost Structure Diagnostics: Cost vs. Total Sales Matrix', fontsize=12, fontweight='bold')
        ax.set_xlabel('Total Product Sales ($)', fontweight='bold')
        ax.set_ylabel('Total Product Cost ($)', fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)
        
    with col2:
        st.subheader("⚠️ Interactive Margin Risk Flags")
        st.markdown(f"Products with high sales (Top 30% Volumetric Percentile) operating **Below {margin_threshold_pct}% Margin**:")
        
        sales_quantile_threshold = product_summary['Sales'].quantile(0.70)
        risk_condition = (product_summary['Sales'] >= sales_quantile_threshold) & (product_summary['Gross_Margin'] < margin_threshold)
        flagged_products = product_summary[risk_condition].sort_values(by='Sales', ascending=False)
        
        if not flagged_products.empty:
            flagged_display = flagged_products[['Sales', 'Gross_Margin']].copy()
            flagged_display['Gross_Margin (%)'] = (flagged_display['Gross_Margin'] * 100).round(2)
            st.warning(f"🚨 Found {len(flagged_display)} high-volume product(s) posing Margin Risk!")
            st.dataframe(flagged_display[['Sales', 'Gross_Margin (%)']].style.format({"Sales": "${:,.2f}"}))
        else:
            st.success("🎉 Excellent! No high-volume products fall under the current Margin Risk criteria.")

# ==========================================
# MODULE 4: PROFIT CONCENTRATION ANALYSIS
# ==========================================
with tab4:
    st.header("📊 Profit & Revenue Concentration Analysis (Pareto 80/20)")
    
    product_sorted_profit = product_summary.sort_values(by='Gross Profit', ascending=False)
    product_sorted_profit['Cum_Profit_Pct'] = product_sorted_profit['Gross Profit'].cumsum() / product_sorted_profit['Gross Profit'].sum()
    top_80_profit = product_sorted_profit[product_sorted_profit['Cum_Profit_Pct'] <= 0.80]
    pct_products_profit = (len(top_80_profit) / len(product_summary)) * 100 if len(product_summary) > 0 else 0
    
    product_sorted_sales = product_summary.sort_values(by='Sales', ascending=False)
    product_sorted_sales['Cum_Sales_Pct'] = product_sorted_sales['Sales'].cumsum() / product_sorted_sales['Sales'].sum()
    top_80_sales = product_sorted_sales[product_sorted_sales['Cum_Sales_Pct'] <= 0.80]
    pct_products_sales = (len(top_80_sales) / len(product_summary)) * 100 if len(product_summary) > 0 else 0

    st.subheader("🛡️ Strategic Portfolio Dependency Indicators")
    kpi_col1, kpi_col2 = st.columns(2)
    
    with kpi_col1:
        st.metric(
            label="💼 Unique Products Generating 80% Profit", 
            value=f"{pct_products_profit:.2f}%",
            delta="High Concentration Risk" if pct_products_profit < 30 else "Balanced Portfolio",
            delta_color="inverse"
        )
    with kpi_col2:
        st.metric(
            label="💰 Unique Products Generating 80% Revenue", 
            value=f"{pct_products_sales:.2f}%",
            delta="High Dependence" if pct_products_sales < 30 else "Balanced Revenue Stream",
            delta_color="inverse"
        )
        
    st.markdown("---")
    st.subheader("📉 Pareto Rule Dual Distribution Chart")
    
    fig, ax1 = plt.subplots(figsize=(10, 5))
    top_items_display = product_sorted_profit.head(15)
    ax1.bar(top_items_display.index, top_items_display['Gross Profit'], color='#4C72B0', alpha=0.7, label='Product Gross Profit ($)')
    ax1.set_ylabel('Gross Profit ($)', color='#4C72B0', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#4C72B0')
    plt.xticks(rotation=70, fontsize=8)
    
    ax2 = ax1.twinx()
    ax2.plot(top_items_display.index, top_items_display['Cum_Profit_Pct'] * 100, color='#C44E52', marker='D', ms=5, linewidth=2, label='Cumulative Profit %')
    ax2.axhline(80, color='red', linestyle='--', alpha=0.6, label='80% Pareto Threshold')
    ax2.set_ylabel('Cumulative Profit Percentage (%)', color='#C44E52', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#C44E52')
    
    plt.title('Pareto 80/20 Profit Concentration & Dependency Diagnostics Curve', fontsize=12, fontweight='bold')
    fig.tight_layout()
    st.pyplot(fig)
