import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(layout="wide")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    data_path = Path("data") / "synthetic_mobile_sales_2025.csv"
    return pd.read_csv(data_path)

df = load_data()

st.title("📱 Mobile Sales Analytics Dashboard 2025")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

# ----- Brand Filter -----
all_brands = sorted(df["Brand"].unique())
select_all_brands = st.sidebar.checkbox("Select All Brands", value=True)

if select_all_brands:
    brand_filter = st.sidebar.multiselect(
        "Select Brand",
        options=all_brands,
        default=all_brands
    )
else:
    brand_filter = st.sidebar.multiselect(
        "Select Brand",
        options=all_brands
    )

# ----- Country Filter -----
all_countries = sorted(df["Country"].unique())
select_all_countries = st.sidebar.checkbox("Select All Countries", value=True)

if select_all_countries:
    country_filter = st.sidebar.multiselect(
        "Select Country",
        options=all_countries,
        default=all_countries
    )
else:
    country_filter = st.sidebar.multiselect(
        "Select Country",
        options=all_countries
    )

# ----- Price Range -----
price_range = st.sidebar.slider(
    "Price Range (USD)",
    int(df["Price_USD"].min()),
    int(df["Price_USD"].max()),
    (int(df["Price_USD"].min()), int(df["Price_USD"].max()))
)

# Apply Filters
filtered_df = df[
    (df["Brand"].isin(brand_filter)) &
    (df["Country"].isin(country_filter)) &
    (df["Price_USD"].between(price_range[0], price_range[1]))
]

# -----------------------------
# KPI SECTION
# -----------------------------
st.subheader("Key Performance Indicators")

total_revenue = filtered_df["Revenue_USD"].sum()
total_units = filtered_df["Units_Sold"].sum()
avg_price = filtered_df["Price_USD"].mean()
avg_rating = filtered_df["Customer_Rating"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue (USD)", f"${total_revenue:,.0f}")
col2.metric("Total Units Sold", f"{total_units:,}")
col3.metric("Average Price (USD)", f"${avg_price:,.2f}")
col4.metric("Average Rating", f"{avg_rating:.2f}")

# -----------------------------
# DESCRIPTIVE STATISTICS
# -----------------------------
st.subheader("Descriptive Statistics")

numeric_cols = ["Price_USD", "Units_Sold", "Revenue_USD", "Customer_Rating"]

stats = filtered_df[numeric_cols].describe().T
stats["Variance"] = filtered_df[numeric_cols].var()
stats["Skewness"] = filtered_df[numeric_cols].skew()
stats["Kurtosis"] = filtered_df[numeric_cols].kurt()

st.dataframe(stats)

# -----------------------------
# Revenue by Brand
# -----------------------------
st.subheader("Revenue by Brand")

brand_rev = (
    filtered_df.groupby("Brand")
    .agg(
        Total_Revenue=("Revenue_USD", "sum"),
        Total_Units=("Units_Sold", "sum"),
        Avg_Price=("Price_USD", "mean"),
        Avg_Rating=("Customer_Rating", "mean")
    )
    .reset_index()
    .sort_values(by="Total_Revenue", ascending=False)
)

fig_brand = px.bar(
    brand_rev,
    x="Brand",
    y="Total_Revenue",
    text_auto=True
)

st.plotly_chart(fig_brand, use_container_width=True)
st.dataframe(brand_rev)

# -----------------------------
# Country Performance
# -----------------------------
st.subheader("Country Performance")

country_rev = (
    filtered_df.groupby("Country")
    .agg(
        Revenue=("Revenue_USD", "sum"),
        Units=("Units_Sold", "sum"),
        Avg_Rating=("Customer_Rating", "mean")
    )
    .reset_index()
)

fig_country = px.pie(
    country_rev,
    names="Country",
    values="Revenue"
)

st.plotly_chart(fig_country, use_container_width=True)
st.dataframe(country_rev)

# -----------------------------
# Monthly Trend
# -----------------------------
st.subheader("Monthly Sales Trend")

monthly = (
    filtered_df.groupby("Sale_Month")
    .agg(
        Revenue=("Revenue_USD", "sum"),
        Units=("Units_Sold", "sum")
    )
    .reset_index()
)

fig_month = px.line(
    monthly,
    x="Sale_Month",
    y=["Revenue", "Units"],
    markers=True
)

st.plotly_chart(fig_month, use_container_width=True)
st.dataframe(monthly)

# -----------------------------
# Price Distribution
# -----------------------------
st.subheader("Price Distribution")

fig_hist = px.histogram(
    filtered_df,
    x="Price_USD",
    nbins=30,
    marginal="box"
)

st.plotly_chart(fig_hist, use_container_width=True)

# -----------------------------
# Correlation Matrix
# -----------------------------
st.subheader("Correlation Matrix")

corr = filtered_df[numeric_cols].corr()

fig_corr = px.imshow(
    corr,
    text_auto=True,
    aspect="auto"
)

st.plotly_chart(fig_corr, use_container_width=True)

# -----------------------------
# Price vs Customer Rating
# -----------------------------
st.subheader("Price vs Customer Rating")

fig_scatter = px.scatter(
    filtered_df,
    x="Price_USD",
    y="Customer_Rating",
    size="Units_Sold",
    color="Brand",
    hover_data=["Model"]
)

st.plotly_chart(fig_scatter, use_container_width=True)

# -----------------------------
# Payment Method Analysis
# -----------------------------
st.subheader("Payment Method Analysis")

payment_stats = (
    filtered_df.groupby("Payment_Method")
    .agg(
        Revenue=("Revenue_USD", "sum"),
        Units=("Units_Sold", "sum")
    )
    .reset_index()
)

fig_payment = px.bar(
    payment_stats,
    x="Payment_Method",
    y="Revenue",
    text_auto=True
)

st.plotly_chart(fig_payment, use_container_width=True)
st.dataframe(payment_stats)

# -----------------------------
# Advanced Insights
# -----------------------------
st.subheader("Advanced Statistical Insights")

revenue_share = brand_rev.copy()
revenue_share["Revenue_%"] = (
    revenue_share["Total_Revenue"] / revenue_share["Total_Revenue"].sum()
) * 100

st.write("### Revenue Share by Brand (%)")
st.dataframe(revenue_share)

st.write("### Top 10 High Revenue Models")

top_models = (
    filtered_df.groupby("Model")
    .agg(
        Revenue=("Revenue_USD", "sum"),
        Units=("Units_Sold", "sum"),
        Avg_Rating=("Customer_Rating", "mean")
    )
    .sort_values(by="Revenue", ascending=False)
    .head(10)
)

st.dataframe(top_models)