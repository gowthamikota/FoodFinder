import json
import os

# Folder where JSON files are stored
folder_path = r"C:\Users\GOWTHAMI\Desktop\webapp-gowthamikota\archive (2)"
json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

merged_data = []

# ✅ Read and merge JSON files
for file in json_files:
    with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
        data = json.load(f)

        # Extract restaurant records
        file_records = sum(len(entry["restaurants"]) for entry in data if "restaurants" in entry)
        print(f"📄 {file}: {file_records} records found.")

        # Add to merged data
        for entry in data:
            if "restaurants" in entry:
                merged_data.extend([r["restaurant"] for r in entry["restaurants"]])

# ✅ Save merged data to merged.json
output_file = os.path.join(folder_path, "merged.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=4)

print(f"\n✅ Total records stored in merged.json: {len(merged_data)}")
print(f"🚀 Merged file saved at: {output_file}")
