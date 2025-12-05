import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('src/data/Superstore.csv', encoding='utf-8')
    except:
        df = pd.read_csv('src/data/Superstore.csv', encoding='latin-1')
    
    # Convert date columns
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d/%m/%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%d/%m/%Y')
    
    # Add derived columns
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Month-Year'] = df['Order Date'].dt.to_period('M')
    df['Profit Margin'] = (df['Profit'] / df['Sales']) * 100
    
    return df

# Load the data
df = load_data()

# Header
st.markdown('<h1 class="main-header">📊 Superstore Sales Dashboard</h1>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Order Date'].min(), df['Order Date'].max()),
    min_value=df['Order Date'].min(),
    max_value=df['Order Date'].max()
)

# Region filter
regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Category filter
categories = st.sidebar.multiselect(
    "Select Category(ies)",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Segment filter
segments = st.sidebar.multiselect(
    "Select Segment(s)",
    options=df['Segment'].unique(),
    default=df['Segment'].unique()
)

# State filter
states = st.sidebar.multiselect(
    "Select State(s)",
    options=sorted(df['State'].unique()),
    default=[]
)

# Apply filters
filtered_df = df[
    (df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (df['Order Date'] <= pd.to_datetime(date_range[1])) &
    (df['Region'].isin(regions)) &
    (df['Category'].isin(categories)) &
    (df['Segment'].isin(segments))
]

if states:
    filtered_df = filtered_df[filtered_df['State'].isin(states)]

# Main dashboard
if not filtered_df.empty:
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = filtered_df['Sales'].sum()
        st.metric("💰 Total Sales", f"${total_sales:,.2f}")
    
    with col2:
        total_profit = filtered_df['Profit'].sum()
        st.metric("📈 Total Profit", f"${total_profit:,.2f}")
    
    with col3:
        total_orders = filtered_df['Order ID'].nunique()
        st.metric("📦 Total Orders", f"{total_orders:,}")
    
    with col4:
        avg_profit_margin = filtered_df['Profit Margin'].mean()
        st.metric("📊 Avg Profit Margin", f"{avg_profit_margin:.2f}%")

    st.markdown("---")

    # Sales trends
    st.subheader("📈 Sales Trends Over Time")
    
    # Monthly sales trend
    monthly_sales = filtered_df.groupby('Month-Year').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    monthly_sales['Month-Year'] = monthly_sales['Month-Year'].astype(str)
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly_sales['Month-Year'],
        y=monthly_sales['Sales'],
        mode='lines+markers',
        name='Sales',
        line=dict(color='#1f77b4', width=3)
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly_sales['Month-Year'],
        y=monthly_sales['Profit'],
        mode='lines+markers',
        name='Profit',
        yaxis='y2',
        line=dict(color='#ff7f0e', width=3)
    ))
    
    fig_trend.update_layout(
        title="Sales and Profit Trends",
        xaxis_title="Month-Year",
        yaxis=dict(title="Sales ($)", side="left"),
        yaxis2=dict(title="Profit ($)", side="right", overlaying="y"),
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales by Category
        st.subheader("🏷️ Sales by Category")
        category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
        fig_cat = px.pie(
            category_sales, 
            values='Sales', 
            names='Category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_cat.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        # Sales by Region
        st.subheader("🌍 Sales by Region")
        region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index()
        fig_region = px.bar(
            region_sales, 
            x='Region', 
            y='Sales',
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig_region.update_layout(showlegend=False)
        st.plotly_chart(fig_region, use_container_width=True)

    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 States by Sales
        st.subheader("🏛️ Top 10 States by Sales")
        state_sales = filtered_df.groupby('State')['Sales'].sum().reset_index()
        top_states = state_sales.nlargest(10, 'Sales')
        fig_states = px.bar(
            top_states, 
            x='Sales', 
            y='State',
            orientation='h',
            color='Sales',
            color_continuous_scale='Viridis'
        )
        fig_states.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_states, use_container_width=True)
    
    with col2:
        # Segment Analysis
        st.subheader("👥 Customer Segment Analysis")
        segment_data = filtered_df.groupby('Segment').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order ID': 'nunique'
        }).reset_index()
        
        fig_segment = go.Figure()
        fig_segment.add_trace(go.Bar(
            name='Sales',
            x=segment_data['Segment'],
            y=segment_data['Sales'],
            marker_color='lightblue'
        ))
        fig_segment.add_trace(go.Bar(
            name='Profit',
            x=segment_data['Segment'],
            y=segment_data['Profit'],
            marker_color='orange'
        ))
        fig_segment.update_layout(barmode='group', height=400)
        st.plotly_chart(fig_segment, use_container_width=True)

    # Product Performance
    st.subheader("📦 Product Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 Products by Sales
        st.write("**Top 10 Products by Sales**")
        top_products = filtered_df.groupby('Product Name')['Sales'].sum().nlargest(10).reset_index()
        fig_top_products = px.bar(
            top_products, 
            x='Sales', 
            y='Product Name',
            orientation='h',
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig_top_products.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_top_products, use_container_width=True)
    
    with col2:
        # Sub-Category Performance
        st.write("**Sub-Category Performance**")
        subcat_data = filtered_df.groupby('Sub-Category').agg({
            'Sales': 'sum',
            'Profit': 'sum'
        }).reset_index()
        subcat_data['Profit Margin'] = (subcat_data['Profit'] / subcat_data['Sales']) * 100
        
        fig_subcat = px.scatter(
            subcat_data, 
            x='Sales', 
            y='Profit',
            size='Sales',
            color='Profit Margin',
            hover_name='Sub-Category',
            color_continuous_scale='RdYlBu'
        )
        fig_subcat.update_layout(height=400)
        st.plotly_chart(fig_subcat, use_container_width=True)

    # Shipping Analysis
    st.subheader("🚚 Shipping Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ship Mode Distribution
        ship_mode_data = filtered_df.groupby('Ship Mode').agg({
            'Order ID': 'nunique',
            'Sales': 'sum'
        }).reset_index()
        
        fig_ship = px.pie(
            ship_mode_data, 
            values='Order ID', 
            names='Ship Mode',
            title="Orders by Ship Mode"
        )
        st.plotly_chart(fig_ship, use_container_width=True)
    
    with col2:
        # Shipping Time Analysis
        filtered_df['Shipping Days'] = (filtered_df['Ship Date'] - filtered_df['Order Date']).dt.days
        ship_time = filtered_df.groupby('Ship Mode')['Shipping Days'].mean().reset_index()
        
        fig_ship_time = px.bar(
            ship_time, 
            x='Ship Mode', 
            y='Shipping Days',
            color='Shipping Days',
            color_continuous_scale='Reds',
            title="Average Shipping Days by Mode"
        )
        st.plotly_chart(fig_ship_time, use_container_width=True)

    # Customer Insights
    st.subheader("👤 Customer Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 Customers by Sales
        customer_sales = filtered_df.groupby('Customer Name')['Sales'].sum().nlargest(10).reset_index()
        fig_customers = px.bar(
            customer_sales, 
            x='Sales', 
            y='Customer Name',
            orientation='h',
            color='Sales',
            color_continuous_scale='Greens',
            title="Top 10 Customers by Sales"
        )
        fig_customers.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_customers, use_container_width=True)
    
    with col2:
        # Customer Distribution by Segment and Region
        customer_dist = filtered_df.groupby(['Segment', 'Region'])['Customer ID'].nunique().reset_index()
        fig_cust_dist = px.sunburst(
            customer_dist, 
            path=['Segment', 'Region'], 
            values='Customer ID',
            title="Customer Distribution"
        )
        st.plotly_chart(fig_cust_dist, use_container_width=True)

    # Location Analysis
    st.subheader("📍 Location Analysis")
    
    # City-wise analysis
    city_data = filtered_df.groupby(['State', 'City']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    
    # Top cities by sales
    top_cities = city_data.nlargest(15, 'Sales')
    top_cities['Location'] = top_cities['City'] + ', ' + top_cities['State']
    
    fig_cities = px.bar(
        top_cities, 
        x='Sales', 
        y='Location',
        orientation='h',
        color='Profit',
        color_continuous_scale='RdYlGn',
        title="Top 15 Cities by Sales"
    )
    fig_cities.update_layout(height=500)
    st.plotly_chart(fig_cities, use_container_width=True)

    # Export Data Section
    st.subheader("📥 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export filtered data as CSV
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📄 Download Filtered Data as CSV",
            data=csv,
            file_name=f'superstore_filtered_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )
    
    with col2:
        # Export summary statistics
        summary_stats = filtered_df.describe()
        summary_csv = summary_stats.to_csv()
        st.download_button(
            label="📊 Download Summary Statistics",
            data=summary_csv,
            file_name=f'superstore_summary_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )
    
    with col3:
        # Export aggregated data
        agg_data = filtered_df.groupby(['Category', 'Sub-Category', 'Region']).agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Quantity': 'sum',
            'Order ID': 'nunique'
        }).reset_index()
        agg_csv = agg_data.to_csv(index=False)
        st.download_button(
            label="📈 Download Aggregated Data",
            data=agg_csv,
            file_name=f'superstore_aggregated_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )

    # Data Table
    st.subheader("📋 Filtered Data Preview")
    st.dataframe(
        filtered_df.head(100),
        use_container_width=True,
        height=400
    )
    
    # Show total records
    st.info(f"Showing first 100 rows of {len(filtered_df):,} total filtered records")

else:
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>📊 Superstore Sales Dashboard | Built with Streamlit & Plotly</p>
        <p>Data Source: Superstore Dataset</p>
    </div>
    """, 
    unsafe_allow_html=True
)