import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(page_title="Retail Returns Dashboard",layout="wide")
st.title("Retail and Supply Chain Analysis Dashboard")

df=pd.read_csv("Merged_Data.csv")
df["Order_Date"]=pd.to_datetime(df["Order_Date"])
return_df=df[df["Return_ID"].notna()]

st.sidebar.header("Filters")
Regions=st.sidebar.multiselect(
    "Region",
    options=df["Region_x"].unique(),
    default=df["Region_x"].unique()
)

categories=st.sidebar.multiselect(
    "Categories",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

min_date=df["Order_Date"].min()
max_date=df["Order_Date"].max()
date_range=st.sidebar.date_input(
    "Order_Date_Range",
    value=(min_date,max_date),
    min_value=min_date,
    max_value=max_date)

df_filtered=df[(df["Region_x"].isin(Regions))&(df["Category"].isin(categories))&
               (df["Order_Date"]>=pd.to_datetime(date_range[0]))&(df["Order_Date"]<=pd.to_datetime(date_range[1]))]
total_sales=df_filtered["Sales"].sum()
total_cost=df_filtered["Cost"].sum()
gross_profit=df_filtered["Profit"].sum()
total_items=df_filtered["Order_Item_ID"].count()
total_returns=df_filtered["Return_ID"].notna().sum()
return_rate=(total_returns/total_items)*100
total_refund=df_filtered["Refund_Amount"].sum()
real_profit=gross_profit-total_refund

col1,col2,col3,col4,col5=st.columns(5)
col1.metric("Total_Sales", f"₹{total_sales/1e7:,.2f} Cr")
col2.metric("Gross_Profit",f"₹{gross_profit/1e7:,.2f} Cr")
col3.metric("real_profit", f"₹{real_profit/1e7:,.2f} Cr")
col4.metric("Return_Rate" ,f"{return_rate:,.2f}%")
col5.metric("Total_Refund", f"₹{total_refund/1e7:,.2f} Cr")


tab1, tab2, tab3 = st.tabs(["Returns Overview", "Trends Over Time", "Product Deep Dive"])

with tab1:
    
        st.subheader("Return Reason by Product")
        return_filtered=df_filtered[df_filtered["Return_ID"].notna()]
        top_products=return_filtered.groupby("Product_Name").agg(
        Return_items=("Return_ID","count")
        ).sort_values(by="Return_items",ascending=False).head(10).reset_index()
        reason_by_product=return_filtered.groupby(["Product_Name","Return_Reason"]).agg(
        Return_items=("Return_ID","count")
        ).reset_index()
        reason_by_product=reason_by_product[reason_by_product["Product_Name"].isin(top_products["Product_Name"])]

        fig=px.bar(
        reason_by_product,
        x="Product_Name",
        y="Return_items",
        color="Return_Reason",
        barmode="stack",
        title="Return Reason by Product"
    )
        st.plotly_chart(fig,use_container_width=True)

    
    
        st.subheader("Return Reason by Region")
        region_totals=df_filtered.groupby("Region_x")["Order_Item_ID"].count()
        reason_by_region=df_filtered.groupby(["Region_x","Return_Reason"]).agg(
        Return_items=("Return_ID",lambda x: x.notna().sum())
        ).reset_index()
        reason_by_region["Return_Rate"]=reason_by_region.apply(
        lambda x: (x["Return_items"]/region_totals[x["Region_x"]])*100,axis=1
        )
        fig2=px.bar(
        reason_by_region,
        x="Region_x",
        y="Return_Rate",
        color="Return_Reason",
        title="Return Reason by Region",
        barmode="stack")
        st.plotly_chart(fig2,use_container_width=True)

        

with tab2:
    st.subheader("Sales and Profit Trend")

    df_filtered["Order_Month"]=df_filtered["Order_Date"].dt.to_period("M").astype(str)

    trend=df_filtered.groupby("Order_Month").agg(
    Total_Sales=("Sales","sum"),
    Total_Profit=("Profit","sum")
    ).reset_index()
    monthly_trend_long=trend.melt(
    id_vars="Order_Month",
    value_vars=["Total_Sales","Total_Profit"],
    var_name="Metric",
    value_name="Value"

    )
    fig3=px.line(
    monthly_trend_long,
    x="Order_Month",
    y="Value",
    color="Metric",
    title="Monthly Sales and Profit Trend",
    markers=True

    )
    st.plotly_chart(fig3,use_container_width=True)

    st.subheader("Refund Share of Profit Over Time")
    monthly_refund=df_filtered.groupby("Order_Month").agg(
    GrossProfit=("Profit","sum"),
    TotalRefund=("Refund_Amount","sum")
    ).reset_index()
    monthly_refund["Refund_Share"]=(monthly_refund["TotalRefund"]/monthly_refund["GrossProfit"])*100
    fig4=px.line(
    monthly_refund,
    x="Order_Month",
    y="Refund_Share",
    title="Refund Share of Profit Over Time"
    )
    st.plotly_chart(fig4,use_container_width=True)
    st.info("Refunds are consistently eating over more than half of monthly profit.")


with tab3:
    
        st.subheader("Average Delivery Delay by Return Reason")
        return_filtered=df_filtered[df_filtered["Return_ID"].notna()].copy()
        return_filtered["Delivery_Date"]=pd.to_datetime(return_filtered["Delivery_Date"])
        return_filtered["Ship_Date"]=pd.to_datetime(return_filtered["Ship_Date"])
        return_filtered["Order_Date"]=pd.to_datetime(return_filtered["Order_Date"])
        return_filtered["Delivery_Delay"]=(return_filtered["Delivery_Date"]-return_filtered["Ship_Date"]).dt.days
        return_filtered["Shipping_Delay"]=(return_filtered["Ship_Date"]-return_filtered["Order_Date"]).dt.days

        delay_by_reason=return_filtered.groupby("Return_Reason").agg(
        Avg_Delivery_Delay=("Delivery_Delay","mean"),
        Avg_Shipping_Delay=("Shipping_Delay","mean")
        ).reset_index()
        delay_long=delay_by_reason.melt(
        id_vars="Return_Reason",
        value_vars=["Avg_Delivery_Delay","Avg_Shipping_Delay"],
        var_name="Delay_Type",
        value_name="Average_Delay"
        )
        fig5=px.bar(
        delay_long,
        x="Return_Reason",
        y="Average_Delay",
        color="Delay_Type",
        barmode="group",
        title="Average Delivery and Shipping Delay by Return Reason"
        )
        st.plotly_chart(fig5,use_container_width=True)

    
        st.subheader("Product Profitability vs Return Rate")
        product_stats=df_filtered.groupby("Product_Name").agg(
        Total_Sales=("Sales","sum"),
        Total_Profit=("Profit","sum"),
        Total_Items=("Order_Item_ID","count"),
        Total_Returns=("Return_ID",lambda x: x.notna().sum()),
        ).reset_index()
        product_stats["Return_Rate"]=(product_stats["Total_Returns"]/product_stats["Total_Items"])*100
        fig6=px.scatter(product_stats,
                x="Total_Profit",
                y="Return_Rate",
                size="Total_Sales",
                hover_name="Product_Name",
                title="Product Profitability vs Return Rate"
)
        st.plotly_chart(fig6,use_container_width=True)
        st.warning("Product in the top right quadrant are high profit and high return rate products. Consider reviewing these products at first")

        











