import os
import json
from supabase import create_client, Client

# 🔹 Supabase Credentials
SUPABASE_URL = "https://lkhzioqqokpxuhchqunz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxraHppb3Fxb2tweHVoY2hxdW56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg0NzAzNzcsImV4cCI6MjA1NDA0NjM3N30.4e560s7bmSy1d_TGUv70CJm9KjwLB-ERdzbbgw9dxFk"
# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Directory where JSON files are stored
JSON_DIR = "C:\\Users\\GOWTHAMI\\Desktop\\webapp-gowthamikota\\archive (2)"  # Update this if needed
MERGED_FILE = "merged.json"

# 🔹 Step 1: Merge All JSON Files into One
merged_data = []

for filename in os.listdir(JSON_DIR):
    if filename.endswith(".json"):  # Only process JSON files
        file_path = os.path.join(JSON_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if isinstance(data, dict) and "restaurants" in data:
                    merged_data.extend(data["restaurants"])  # Extract restaurant data
                elif isinstance(data, list):  # Direct list of restaurants
                    merged_data.extend(data)
            except json.JSONDecodeError as e:
                print(f"Error reading {filename}: {e}")

# Save merged data to a new JSON file
with open(MERGED_FILE, "w", encoding="utf-8") as outfile:
    json.dump(merged_data, outfile, indent=4)

print(f"✅ Merged {len(merged_data)} restaurants into {MERGED_FILE}")

# 🔹 Step 2: Insert Data into Supabase
with open(MERGED_FILE, "r", encoding="utf-8") as file:
    restaurants = json.load(file)

for restaurant_entry in restaurants:
    restaurant = restaurant_entry.get("restaurant")  # Extract the inner "restaurant" object
    if not restaurant:
        continue  # Skip if "restaurant" key is missing

    data = {
        "name": restaurant.get("name"),
        "cuisines": restaurant.get("cuisines"),
        "price_range": restaurant.get("price_range"),
        "has_online_delivery": bool(restaurant.get("has_online_delivery", 0)),
        "is_delivering_now": bool(restaurant.get("is_delivering_now", 0)),
        "user_rating": restaurant.get("user_rating"),
        "location": restaurant.get("location"),
        "menu_url": restaurant.get("menu_url"),
        "featured_image": restaurant.get("featured_image"),
        "zomato_events": restaurant.get("zomato_events", [])
    }

    response = supabase.table("restaurants").insert(data).execute()
    print(response)  # Debugging output

print("✅ Data successfully inserted into Supabase!")
