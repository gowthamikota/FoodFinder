import json
import os
from supabase import create_client, Client

# Supabase Credentials (Replace with your actual values)
SUPABASE_URL = "https://lkhzioqqokpxuhchqunz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxraHppb3Fxb2tweHVoY2hxdW56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg0NzAzNzcsImV4cCI6MjA1NDA0NjM3N30.4e560s7bmSy1d_TGUv70CJm9KjwLB-ERdzbbgw9dxFk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Folder where JSON files are stored
folder_path = "C:\\Users\\GOWTHAMI\\Desktop\\webapp-gowthamikota\\archive (2)"
json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

merged_data = []

for file in json_files:
    with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
        data = json.load(f)

        # Extract total count (debugging purpose)
        total_found = data[0].get("results_found", 0)
        print(f"📄 Processing {file} - Total Found: {total_found}")

        # Extract actual restaurant data
        for entry in data:
            if "restaurants" in entry and isinstance(entry["restaurants"], list):
                for r in entry["restaurants"]:
                    restaurant = r["restaurant"]
                    
                    # Remove problematic key
                    if "R" in restaurant:
                        del restaurant["R"]

                    merged_data.append(restaurant)

print(f"✅ Total Merged Restaurants: {len(merged_data)}")

# Batch insert to avoid Supabase size limits
batch_size = 500
for i in range(0, len(merged_data), batch_size):
    batch = merged_data[i : i + batch_size]
    response = supabase.table("zomato_full_data").insert(batch).execute()
    print(f"Inserted batch {i} - {i + batch_size}")

print("🚀 Data upload complete!")