import pandas as pd
df=pd.read_csv("Merged_Data.csv")
df["Order_Date"]=pd.to_datetime(df["Order_Date"])
return_df=df[df["Return_ID"].notna()]
reason_by_product= return_df.groupby(["Product_Name","Return_Reason"]).agg(
    Total_Items=("Order_Item_ID", "nunique"),
    Returned_Items=("Return_ID", "nunique"),
    Refund_Amount=("Refund_Amount", "sum")
).reset_index()

reason_by_product["Return_Percentage"] = reason_by_product["Returned_Items"]/reason_by_product["Total_Items"] * 100
reason_by_product["Reason_Share_Pct"]= reason_by_product.groupby("Product_Name")["Returned_Items"].transform(lambda x: x/x.sum()*100)
top10_products= (reason_by_product.groupby("Product_Name")["Returned_Items"].sum()).reset_index()
print(top10_products.sort_values(ascending=False,by="Returned_Items").head(10))
total_returns= return_df["Return_ID"].notna().sum()
top10_products.columns=["Product_Name","Total_Returns"]
top10_products["Return_Share_Pct"]= (top10_products["Total_Returns"]/total_returns * 100)
print(top10_products)

total_returns = return_df["Return_ID"].notna().sum()

top10_products = (
    reason_by_product.groupby("Product_Name")["Returned_Items"].sum()
    .sort_values(ascending=False)
    .head(10)                      # keep this — don't drop it before reset_index
    .reset_index()
)
top10_products.columns = ["Product_Name", "Total_Returns"]
top10_products["Return_Share_Pct"] = top10_products["Total_Returns"] / total_returns * 100

print(top10_products)