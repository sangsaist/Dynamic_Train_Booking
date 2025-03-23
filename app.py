from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# MongoDB Connection
client = MongoClient("mongodb+srv://train05:sangsai2005@cluster2.mm1xv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster2")
db = client["train_booking_system"]
trains_collection = db["trains"]

# Home Page Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/Add_Train')
def add_train_page():
    return render_template('index.html')

@app.route('/Normal_Booking')
def normal_booking_page():
    return render_template('normal.html')

@app.route('/Dynamic_Booking')
def dynamic_booking_page():
    return render_template('dynamic.html')

# Add Train API
@app.route('/add_train', methods=['POST'])
def add_train():
    data = request.json
    train_name = data.get('train_name')
    junctions = data.get('junctions')  # List of junctions
    seats_count = data.get('seats_count')

    if not train_name or not junctions or not seats_count:
        return jsonify({"message": "All fields are required!"}), 400

    seats = [f"S{i+1}" for i in range(seats_count)]
    train_data = {
        "train_name": train_name,
        "junctions": junctions,
        "seats": seats,
        "bookings": []
    }
    trains_collection.insert_one(train_data)
    return jsonify({"message": "Train added successfully!"}), 200

# Fetch trains for dropdown
@app.route('/get_trains')
def get_trains():
    trains = trains_collection.distinct("train_name")
    return jsonify({"trains": trains})

# Get Booking History
@app.route('/get_booking_history')
def get_booking_history():
    train_name = request.args.get('train_name')
    train = trains_collection.find_one({"train_name": train_name})
    if not train:
        return jsonify({"message": "Train not found!"}), 404
    return jsonify({"history": train['bookings']})

# Get all possible segments
@app.route('/get_segments')
def get_segments():
    train_name = request.args.get('train_name')
    train = trains_collection.find_one({"train_name": train_name})
    if not train:
        return jsonify({"message": "Train not found!"}), 404

    junctions = train['junctions']
    segments = []
    for i in range(len(junctions)):
        for j in range(i + 1, len(junctions)):
            segments.append(f"{junctions[i]}-{junctions[j]}")
    return jsonify({"segments": segments})

# Get seat status
@app.route('/get_seat_status')
def get_seat_status():
    train_name = request.args.get('train_name')
    segment = request.args.get('segment')  # Format: "A-B"
    train = trains_collection.find_one({'train_name': train_name})
    if not train:
        return jsonify([])

    junctions = train['junctions']
    start_junc, end_junc = segment.split('-')
    start_idx, end_idx = junctions.index(start_junc), junctions.index(end_junc)

    seat_status = []
    for seat in train['seats']:
        status = "available"
        for booking in train['bookings']:
            b_segment = booking['segment']
            # Ensure the segment is a list
            if isinstance(b_segment, str):
                b_segment = b_segment.split('-')
            b_start = junctions.index(b_segment[0])
            b_end = junctions.index(b_segment[1])
            if booking['seat'] == seat and not (end_idx <= b_start or start_idx >= b_end):
                status = "booked"
                break
        seat_status.append({"name": seat, "status": status})
    return jsonify({"seats": seat_status})

# ✅ Corrected Normal Booking API
@app.route('/book_normal', methods=['POST'])
def book_normal():
    data = request.json
    train_name = data['train_name']
    passenger = data['passenger']
    seat = data['seat']
    # Ensure segment is always a list [start, end]
    segment = data['segment'].split('-') if isinstance(data['segment'], str) else data['segment']

    train = trains_collection.find_one({"train_name": train_name})
    if not train:
        return jsonify({"message": "Train not found!"}), 404

    junctions = train['junctions']
    start_idx, end_idx = junctions.index(segment[0]), junctions.index(segment[1])

    # Debugging prints
    print("Existing bookings:", train['bookings'])

    # Check for overlapping bookings
    for booking in train['bookings']:
        if booking['seat'] == seat:
            b_segment = booking['segment']
            if isinstance(b_segment, str):
                b_segment = b_segment.split('-')
            b_start = junctions.index(b_segment[0])
            b_end = junctions.index(b_segment[1])
            if not (end_idx <= b_start or start_idx >= b_end):
                return jsonify({"message": "Seat already booked for overlapping segment"}), 400

    # Book the seat (store segment as list)
    trains_collection.update_one(
        {"train_name": train_name},
        {"$push": {"bookings": {"passenger": passenger, "segment": segment, "seat": seat}}}
    )
    return jsonify({"message": "Seat booked successfully!"}), 200

# Reset Bookings
@app.route('/reset', methods=['POST'])
def reset():
    train_name = request.json['train_name']
    trains_collection.update_one({"train_name": train_name}, {"$set": {"bookings": []}})
    return jsonify({"message": "Bookings reset successfully!"}), 200

# Dynamic Booking APIs
@app.route('/get_junctions')
def get_junctions():
    train_name = request.args.get('train_name')
    train = trains_collection.find_one({"train_name": train_name})
    if not train:
        return jsonify({"message": "Train not found!"}), 404
    return jsonify({"junctions": train['junctions']})

# Helper to check segment overlap
def is_overlap(seg1, seg2, junctions):
    s1, e1 = junctions.index(seg1[0]), junctions.index(seg1[1])
    s2, e2 = junctions.index(seg2[0]), junctions.index(seg2[1])
    return not (e1 <= s2 or e2 <= s1)

@app.route('/dynamic_book', methods=['POST'])
def dynamic_book():
    data = request.json
    train_name = data['train_name']
    passenger = data['passenger']
    source = data['source']
    destination = data['destination']

    train = trains_collection.find_one({"train_name": train_name})
    if not train:
        return jsonify({"message": "Train not found!"}), 404

    junctions, seats, bookings = train['junctions'], train['seats'], train['bookings']
    src_idx, dest_idx = junctions.index(source), junctions.index(destination)

    if src_idx >= dest_idx:
        return jsonify({"message": "Invalid source and destination."}), 400

    # Create journey segments
    journey_segments = [[junctions[i], junctions[i + 1]] for i in range(src_idx, dest_idx)]
    seat_allocation = {}
    updated_bookings = bookings.copy()

    for segment in journey_segments:
        allocated = False
        for seat in seats:
            if all(not is_overlap(segment, b['segment'] if isinstance(b['segment'], list) else b['segment'].split('-'), junctions) or b['seat'] != seat for b in updated_bookings):
                seat_allocation[f"{segment[0]}-{segment[1]}"] = seat
                updated_bookings.append({"passenger": passenger, "segment": segment, "seat": seat})
                allocated = True
                break
        if not allocated:
            return jsonify({"message": f"No available seat for segment {segment[0]}-{segment[1]}"}), 400

    # Update bookings only after successful allocation
    trains_collection.update_one({"train_name": train_name}, {"$set": {"bookings": updated_bookings}})
    return jsonify({"message": "Booking Successful!", "allocation": seat_allocation}), 200

if __name__ == '__main__':
    app.run(debug=True)
