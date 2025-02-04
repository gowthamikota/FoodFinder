from flask import Flask, jsonify, request, render_template
from supabase import create_client, Client
from dotenv import load_dotenv
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import os, math, traceback

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# Load MobileNetV2 for image classification 
model = tf.keras.applications.MobileNetV2(weights="imagenet")

# Food to Cuisine Mapping
cusineMapping = {
    'pizza': ['Italian', 'American'],
    'hamburger': ['American', 'Fast Food'],
    'ice cream': ['Desserts', 'Ice Cream'],
    'pasta': ['Italian', 'Continental'],
    'sushi': ['Japanese', 'Asian'],
    'curry': ['Indian', 'Thai', 'Asian'],
    'noodles': ['Chinese', 'Asian', 'Thai'],
    'sandwich': ['American', 'Fast Food'],
    'cake': ['Desserts', 'Bakery'],
    'salad': ['Healthy Food', 'Continental']
}

# Country Code to Country Name mapping
country_mapping = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zealand",
    162: "Phillipines",
    166: "Qatar",
    184: "Singapore",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "UAE",
    215: "United Kingdom",
    216: "United States"
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_image_classification_model():
    return model

def process_image(image_path):
    try:
        model_instance = load_image_classification_model()
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        predictions = model_instance.predict(img_array)
        decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions)
        food_items = []
        for pred in decoded_predictions[0]:
            class_name = pred[1].lower().replace('_', ' ')
            confidence = float(pred[2])
            for food_key in cusineMapping.keys():
                if food_key in class_name:
                    food_items.append({
                        'name': food_key,
                        'confidence': confidence,
                        'cuisines': cusineMapping[food_key]
                    })
                    break
        return food_items
    except Exception as e:
        print("Error in process_image:")
        traceback.print_exc()
        return []

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in km
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# HTML templates
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/nearby-search")
def nearby_search():
    return render_template("nearby_search.html")
@app.route("/image-search")
def image_search():
    return render_template("image_search.html")
@app.route("/restaurant-list")
def restaurant_list():
    return render_template("restaurant_list.html")
@app.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    return render_template("restaurant_detail.html", restaurant_id=restaurant_id)

# API Endpoints
@app.route("/api/restaurant/<int:restaurant_id>", methods=["GET"])
def get_restaurant_by_id(restaurant_id):
    response = supabase.table("restaurants").select("*").eq("restaurant_id", restaurant_id).execute()
    if response.data:
        return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404



@app.route("/api/restaurants", methods=['GET'])
def get_restaurants():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 9))
        offset = (page - 1) * limit
        country_code = request.args.get("country_code", type=int)
        cuisines = request.args.get("cuisines")
        search_query = request.args.get("search", '').strip()
        avg_cost_raw = request.args.get("avg_cost")
        try:
            avg_cost = int(float(avg_cost_raw)) if avg_cost_raw else None
        except ValueError:
            return jsonify({"error": "Invalid average cost value"}), 400
        query = supabase.table("restaurants").select("*")
        count_query = supabase.table("restaurants").select("restaurant_id")
        if country_code:
            query = query.eq("country", country_code)
            count_query = count_query.eq("country", country_code)

        if search_query:
            search_term = f"%{search_query}%"
            query = query.ilike("name", search_term)
            count_query = count_query.ilike("name", search_term)

        if avg_cost is not None:
            query = query.lte("average_cost_for_two", avg_cost)
            count_query = count_query.lte("average_cost_for_two", avg_cost)

        if cuisines:
            cuisines_list = [cuisine.strip().lower() for cuisine in cuisines.split(',')]
            for cuisine in cuisines_list:
                query = query.ilike("cuisines", f"%{cuisine}%")
                count_query = count_query.ilike("cuisines", f"%{cuisine}%")
        count_response = count_query.execute()
        total_count = len(count_response.data)
        total_pages = max(1, -(-total_count // limit))  
        query = query.range(offset, offset + limit - 1)
        response = query.execute()

        print(f"[DEBUG] Search query: {search_query}")
        print(f"[DEBUG] Query response: {response.data}")

        if response.data:
            return jsonify({
                "restaurants": response.data,
                "page": page,
                "total_pages": total_pages,
                "total_count": total_count
            }), 200
        else:
            return jsonify({
                "restaurants": [],
                "page": page,
                "total_pages": 0,
                "total_count": 0,
                "message": "No restaurants found"
            }), 200

    except Exception as e:
        print("[ERROR] API Failure:", str(e))
        print(traceback.format_exc())
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/restaurants/nearby", methods=['GET'])
def get_nearby_restaurants():
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
        radius = float(request.args.get("radius", 3))
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 9))
        offset = (page - 1) * limit

        response = supabase.table("restaurants").select("*").execute()

        nearby_restaurants = []
        for restaurant in response.data:
            rest_lat = float(restaurant.get("latitude", 0))
            rest_lon = float(restaurant.get("longitude", 0))
            distance = calculate_distance(lat, lon, rest_lat, rest_lon)
            if distance <= radius:
                restaurant["distance"] = round(distance, 2)
                nearby_restaurants.append(restaurant)

        total_count = len(nearby_restaurants)
        total_pages = math.ceil(total_count / limit)
        paginated_restaurants = nearby_restaurants[offset:offset + limit]

        return jsonify({
            "restaurants": paginated_restaurants,
            "total_pages": total_pages
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/restaurants/search-by-image", methods=['POST'])
def search_restaurants_by_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        file = request.files['image']
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        img_path = "temp_image.jpg"
        file.save(img_path)
        food_items = process_image(img_path)
        if not food_items:
            return jsonify({"error": "Could not determine cuisine from image"}), 404
        detected_cuisines = set()
        for item in food_items:
            for cuisine in item.get('cuisines', []):
                detected_cuisines.add(cuisine.lower().strip())
        response = supabase.table("restaurants").select("*").execute()
        if not response.data:
            return jsonify({"error": "No restaurants found in the database"}), 404
        matching_restaurants = []
        for restaurant in response.data:
            cuisines_str = restaurant.get("cuisines") or ""
            restaurant_cuisines = [c.strip().lower() for c in cuisines_str.split(",") if c.strip()]
            if any(c in restaurant_cuisines for c in detected_cuisines):
                matching_restaurants.append(restaurant)
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 9))
        offset = (page - 1) * limit
        total_matches = len(matching_restaurants)
        total_pages = math.ceil(total_matches / limit)
        paginated_restaurants = matching_restaurants[offset:offset + limit]

        return jsonify({
            "status": "success",
            "detected_cuisines": list(detected_cuisines),
            "restaurants": paginated_restaurants,
            "page": page,
            "total_pages": total_pages
        }), 200

    except Exception as e:
        print("Exception in search_restaurants_by_image:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)


