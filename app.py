# app.py
from flask import Flask, jsonify, request, render_template
from supabase import create_client, Client
import os
from PIL import Image
import numpy as np
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet import preprocess_input
from tensorflow.keras.preprocessing import image
import math

SUPABASE_URL = "https://lkhzioqqokpxuhchqunz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxraHppb3Fxb2tweHVoY2hxdW56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg0NzAzNzcsImV4cCI6MjA1NDA0NjM3N30.4e560s7bmSy1d_TGUv70CJm9KjwLB-ERdzbbgw9dxFk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# ResNet model for image recognition
model = ResNet50(weights='imagenet')

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    return distance

#to get restaurant by using its id
@app.route("/api/restaurant/<int:restaurant_id>", methods=["GET"])
def get_restaurant_by_id(restaurant_id):
    response = supabase.table("restaurants").select("*").eq("restaurant_id", restaurant_id).execute()
    if response.data:
        return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404
    
#to get list of restaurants with pagination
@app.route("/api/restaurants", methods=['GET'])
def get_restaurants():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit
    response = supabase.table("restaurants").select("*").range(offset, offset + limit - 1).execute()
    if response.data:
        return jsonify(response.data), 200
    else:
        return jsonify({"error": "No restaurants found"}), 404
    
#to get nearby restaurants
@app.route("/api/restaurants/nearby", methods=['GET'])
def get_nearby_restaurants():
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
        radius = float(request.args.get("radius", 3)) 
        response = supabase.table("restaurants").select("*").execute() 
        nearby_restaurants = []
        for restaurant in response.data:
            rest_lat = float(restaurant.get("latitude", 0))
            rest_lon = float(restaurant.get("longitude", 0))  
            distance = calculate_distance(lat, lon, rest_lat, rest_lon) 
            if distance <= radius:
                restaurant["distance"] = round(distance, 2)
                nearby_restaurants.append(restaurant)
        return jsonify(nearby_restaurants), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
#to search restaurants by image of food
@app.route("/api/restaurants/search-by-image", methods=['POST'])
def search_restaurants_by_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400 
        file = request.files['image']
        img = Image.open(file)
        img = img.resize((224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        predictions = model.predict(img_array)
        from tensorflow.keras.applications.resnet50 import decode_predictions
        decoded_predictions = decode_predictions(predictions, top=3)[0]
        food_categories = [pred[1].lower() for pred in decoded_predictions]
        response = supabase.table("restaurants").select("*").execute()
        matching_restaurants = []
        for restaurant in response.data:
            cuisines = restaurant.get("cuisines", "").lower()
            if any(category in cuisines for category in food_categories):
                matching_restaurants.append(restaurant)
        
        return jsonify(matching_restaurants), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    return render_template("restaurant_detail.html", restaurant_id=restaurant_id)

if __name__ == "__main__":
    app.run(debug=True)




