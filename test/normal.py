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
    return render_template('normal.html')

@app.route('/get_trains')
def get_trains():
    trains = trains_collection.distinct("train_name")
    return jsonify({"trains": trains})

@app.route('/get_segments')
def get_segments():
    train_name = request.args.get('train_name')
    train = trains_collection.find_one({"train_name": train_name})
    return jsonify({"segments": train['segments']})

@app.route('/get_seat_status')
def get_seat_status():
    train_name = request.args.get('train_name')
    segment = request.args.get('segment').split('-')
    train = trains_collection.find_one({"train_name": train_name})

    seat_status = []
    for seat in train['seats']:
        status = "available"
        for booking in train['bookings']:
            if booking['seat'] == seat:
                if booking['segment'] == segment:
                    status = "booked"
                    break
                # Check overlap logic
                if not (segment[1] <= booking['segment'][0] or segment[0] >= booking['segment'][1]):
                    status = "booked"
                    break
        seat_status.append({"name": seat, "status": status})
    return jsonify({"seats": seat_status})

@app.route('/book_normal', methods=['POST'])
def book_normal():
    data = request.json
    train_name = data['train_name']
    passenger = data['passenger']
    segment = data['segment'].split('-')
    seat = data['seat']

    train = trains_collection.find_one({"train_name": train_name})

    # Check seat is available for this segment
    for booking in train['bookings']:
        if booking['seat'] == seat:
            # Check for overlap
            if not (segment[1] <= booking['segment'][0] or segment[0] >= booking['segment'][1]):
                return jsonify({"message": "Seat already booked for overlapping segment"}), 400

    # Insert booking
    trains_collection.update_one({"train_name": train_name},
        {"$push": {"bookings": {"passenger": passenger, "segment": segment, "seat": seat}}})

    return jsonify({"message": "Seat booked successfully!"})

@app.route('/reset', methods=['POST'])
def reset():
    train_name = request.json['train_name']
    trains_collection.update_one({"train_name": train_name}, {"$set": {"bookings": []}})
    return jsonify({"message": "Bookings reset successfully!"})

@app.route('/get_booking_history')
def get_booking_history():
    train_name = request.args.get('train_name')
    train = trains_collection.find_one({"train_name": train_name})
    return jsonify({"history": train['bookings']})



if __name__ == '__main__':
    app.run(debug=True)
