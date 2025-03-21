from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from itertools import combinations

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

client = MongoClient("mongodb+srv://train05:sangsai2005@cluster2.mm1xv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster2")
db = client["train_booking_system"]
trains_collection = db["trains"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_train', methods=['POST'])
def add_train():
    data = request.json
    train_name = data.get('train_name')
    junctions = data.get('junctions')
    seats_count = data.get('seats_count')

    if not train_name or not junctions or not seats_count:
        return jsonify({"message": "All fields are required!"}), 400

    segments = [list(combo) for combo in combinations(junctions, 2)]
    seats = [f"S{i+1}" for i in range(seats_count)]

    train_data = {
        "train_name": train_name,
        "junctions": junctions,
        "segments": segments,
        "seats": seats,
        "bookings": []
    }

    # ✅ Use your defined collection here
    trains_collection.insert_one(train_data)

    return jsonify({"message": "Train added successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
