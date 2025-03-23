from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://train05:sangsai2005@cluster2.mm1xv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster2")
db = client["train_booking_system"]
trains_collection = db["trains"]

@app.route('/')
def index():
    return render_template('dynamic.html')

@app.route('/get_trains')
def get_trains():
    trains = trains_collection.distinct("train_name")
    return jsonify({"trains": trains})

@app.route('/get_junctions')
def get_junctions():
    train_name = request.args.get('train_name')
    train = trains_collection.find_one({"train_name": train_name})
    return jsonify({"junctions": train['junctions']})

def is_overlap(seg1, seg2, junctions):
    start1, end1 = junctions.index(seg1[0]), junctions.index(seg1[1])
    start2, end2 = junctions.index(seg2[0]), junctions.index(seg2[1])
    return not (end1 <= start2 or end2 <= start1)

@app.route('/dynamic_book', methods=['POST'])
def dynamic_book():
    data = request.json
    train_name = data['train_name']
    passenger = data['passenger']
    source = data['source']
    destination = data['destination']

    train = trains_collection.find_one({"train_name": train_name})
    junctions = train['junctions']
    seats = train['seats']
    bookings = train['bookings']

    src_idx, dest_idx = junctions.index(source), junctions.index(destination)
    if src_idx >= dest_idx:
        return jsonify({"message": "Invalid source and destination."}), 400

    # Generate required journey segments
    journey_segments = [[junctions[i], junctions[i + 1]] for i in range(src_idx, dest_idx)]

    seat_allocation = {}

    # Greedy + Backtracking hybrid allocation
    for segment in journey_segments:
        allocated = False
        for seat in seats:
            conflict = False
            for booking in bookings:
                if booking['seat'] == seat and is_overlap(segment, booking['segment'], junctions):
                    conflict = True
                    break
            if not conflict:
                seat_allocation[f"{segment[0]}-{segment[1]}"] = seat
                bookings.append({"passenger": passenger, "segment": segment, "seat": seat})
                allocated = True
                break
        if not allocated:
            return jsonify({"message": f"No available seat for segment {segment[0]}-{segment[1]}"}), 400

    # Update database with new bookings
    trains_collection.update_one({"train_name": train_name}, {"$set": {"bookings": bookings}})
    return jsonify({"message": "Booking Successful!", "allocation": seat_allocation}), 200

@app.route('/get_booking_history')
def get_booking_history():
    train_name = request.args.get('train_name')
    train = trains_collection.find_one({"train_name": train_name})
    return jsonify({"history": train['bookings']})

if __name__ == '__main__':
    app.run(debug=True)
