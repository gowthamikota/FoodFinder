from flask import Flask, jsonify, request, render_template
from supabase import create_client,Client
import os
SUPABASE_URL = "https://lkhzioqqokpxuhchqunz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxraHppb3Fxb2tweHVoY2hxdW56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg0NzAzNzcsImV4cCI6MjA1NDA0NjM3N30.4e560s7bmSy1d_TGUv70CJm9KjwLB-ERdzbbgw9dxFk"
supabase:Client=create_client(SUPABASE_URL,SUPABASE_KEY)
app=Flask(__name__)

#to get restaurant by using its id
@app.route("/api/restaurant/<int:restaurant_id>", methods=["GET"])
def get_restaurant_by_id(restaurant_id):
    response = supabase.table("restaurants").select("*").eq("restaurant_id", restaurant_id).execute()
    if response.data:
        return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404

#to get list of restaurants with pagination
@app.route("/api/restaurants",methods=['GET'])
def get_restaurants():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit
    response = supabase.table("restaurants").select("*").range(offset, offset + limit - 1).execute()
    if response.data:
        return jsonify(response.data), 200
    else:
        return jsonify({"error": "No restaurants found"}), 404
@app.route("/")
def home():
    return "Welcome to Zomato API"
if __name__ == "__main__":
    app.run(debug=True)