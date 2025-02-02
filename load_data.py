import pandas as pd
from supabase import create_client, Client
import numpy as np
SUPABASE_URL = "https://lkhzioqqokpxuhchqunz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxraHppb3Fxb2tweHVoY2hxdW56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg0NzAzNzcsImV4cCI6MjA1NDA0NjM3N30.4e560s7bmSy1d_TGUv70CJm9KjwLB-ERdzbbgw9dxFk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
file_path = "C:\\Users\\GOWTHAMI\\Desktop\\webapp-gowthamikota\\load_data.py"  
df = pd.read_csv(file_path, encoding="ISO-8859-1")
df = df.rename(columns={
    "Restaurant ID": "restaurant_id",
    "Restaurant Name": "name",
    "Country Code": "country",
    "City": "city",
    "Address": "address",
    "Locality": "locality",
    "Locality Verbose": "locality_verbose",
    "Longitude": "longitude",
    "Latitude": "latitude",
    "Cuisines": "cuisines",
    "Average Cost for two": "average_cost_for_two",
    "Currency": "currency",
    "Has Table booking": "has_table_booking",
    "Has Online delivery": "has_online_delivery",
    "Is delivering now": "is_delivering_now",
    "Price range": "price_range",
    "Aggregate rating": "rating",
    "Rating color": "rating_color",
    "Rating text": "rating_text",
    "Votes": "votes",
    "Switch to order menu": "switch_to_order_menu"})
df["has_table_booking"] = df["has_table_booking"].apply(lambda x: True if x == "Yes" else False)
df["has_online_delivery"] = df["has_online_delivery"].apply(lambda x: True if x == "Yes" else False)
df["is_delivering_now"] = df["is_delivering_now"].apply(lambda x: True if x == "Yes" else False)
df["switch_to_order_menu"] = df["switch_to_order_menu"].apply(lambda x: True if x == "Yes" else False)
df.replace([np.nan, np.inf, -np.inf], None, inplace=True)
batch_size = 500
for i in range(0, len(df), batch_size):
    batch = df.iloc[i : i + batch_size].to_dict(orient="records")
    response = supabase.table("restaurants").insert(batch).execute()
    print(f"Inserted {i + len(batch)} records, Response: {response}")
print("Data successfully uploaded to Supabase!")
