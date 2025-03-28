
**1. @app.route('/') — Home Page**

Purpose:
Acts as the home/landing page of the application.
Technical Breakdown:
When a user accesses the root URL (http://localhost:5000/), the home() function gets executed.
render_template('home.html') tells Flask to look for an HTML file named home.html inside the templates directory and render it.
No data is passed — it’s just a static HTML page loaded to the browser.
---
**2. @app.route('/Add_Train') — Add Train Page**
Purpose:
Loads the page where the admin can input new train details.
Technical Breakdown:
URL: http://localhost:5000/Add_Train
Executes the add_train_page() function.
render_template('index.html') loads the index.html file for the front end.
Typically, the index.html would contain a form to input train_name, junctions, and seats_count.
---
**3. @app.route('/Normal_Booking') — Normal Booking Page**
Purpose:
Opens the normal booking interface where users manually select the seat and segment.
Technical Breakdown:
URL: http://localhost:5000/Normal_Booking
Executes normal_booking_page() and renders normal.html.
This page would contain form fields to select:
Train
Source station
Destination station
Preferred Seat
Passenger Name
---
**4. @app.route('/Dynamic_Booking') — Dynamic Booking Page**
Purpose:
Opens the dynamic booking interface where the system auto-allocates seats.
Technical Breakdown:
URL: http://localhost:5000/Dynamic_Booking
Runs dynamic_booking_page().
Renders dynamic.html, where the user selects:
Train
Source
Destination
Passenger Name
No seat selection is done by the user; the system does that automatically.
---
**5. @app.route('/add_train', methods=['POST']) — Add Train API**
Purpose:
Backend API to insert a new train into the MongoDB database.
Technical Breakdown:
Called via AJAX or API call (POST request with JSON data).
Reads JSON from the request:
{
  "train_name": "Express1",
  "junctions": ["A", "B", "C", "D"],
  "seats_count": 5
}
Input Validation: If any field is missing, it returns an error.
Generates seats dynamically:
seats = ["S1", "S2", "S3", "S4", "S5"]
Creates the initial train document with empty bookings.
Stores it in MongoDB using:
trains_collection.insert_one(train_data)
Sends a success response.
---
**6. @app.route('/get_trains') — Get All Train Names**
Purpose:
Fetches the distinct train names for populating dropdowns in the UI.
Technical Breakdown:
Executes trains_collection.distinct("train_name").
Returns a JSON object:
{ "trains": ["Express1", "Express2"] }
---
**7. @app.route('/get_booking_history') — Get Booking History**
Purpose:
Retrieves all bookings made on a specific train.
Technical Breakdown:
URL contains query parameter: /get_booking_history?train_name=Express1
Fetches the train document with:
trains_collection.find_one({"train_name": train_name})
Returns all records from the bookings array of that train.
Example Output:
{
  "history": [
    {"passenger": "John", "segment": ["A", "C"], "seat": "S1"},
    {"passenger": "Alice", "segment": ["B", "D"], "seat": "S2"}
  ]
}
---
**8. @app.route('/get_segments') — Get All Possible Segments**
Purpose:
Computes all possible valid journey segments like A-B, A-C, B-D.
Technical Breakdown:
Accepts train_name as a query param.
Pulls the train’s junctions from the database.
Uses nested loops to build pairs:
Example: For ["A", "B", "C", "D"], segments are A-B, A-C, A-D, B-C, B-D, C-D.
Sends back a JSON list of these segments.
---
**9. @app.route('/get_seat_status') — Seat Availability Check**
Purpose:
Checks each seat’s status (Available/Booked) for a specific segment.
Technical Breakdown:
Inputs: train_name, segment (like A-B)
Fetches train data and junctions.
For every seat, checks if it is overlapping with an existing booking on that segment.
If overlapping, status = "booked"; otherwise, "available".
Returns data like:
{
  "seats": [
    {"name": "S1", "status": "available"},
    {"name": "S2", "status": "booked"}
  ]
}
---
**10. @app.route('/book_normal', methods=['POST']) — Manual Booking API**
Purpose:
Books a specific seat for a specific segment chosen by the user.
Technical Breakdown:
Reads POST data:
{
  "train_name": "Express1",
  "passenger": "John",
  "seat": "S1",
  "segment": "A-C"
}
Validates that the selected seat is not already booked for any overlapping journey.
If valid, updates the train’s booking array in MongoDB:
"$push": {"bookings": {"passenger": passenger, "segment": segment, "seat": seat}}
---
**11. @app.route('/reset', methods=['POST']) — Reset All Bookings**
Purpose:
Clears all bookings for a train — resets the train.
Technical Breakdown:
Reads POST data:
{ "train_name": "Express1" }
MongoDB $set operation clears the bookings array:
trains_collection.update_one({"train_name": train_name}, {"$set": {"bookings": []}})
---
**12. @app.route('/get_junctions') — Get All Junctions of a Train**
Purpose:
Fetches the list of junctions (stations) for a specific train.
Technical Breakdown:
Pulls from the database the junctions field:
{ "junctions": ["A", "B", "C", "D"] }
---
**13. @app.route('/dynamic_book', methods=['POST']) — Dynamic Booking API**
Purpose:
Auto-assigns seats dynamically by splitting the journey into segments.
Ensures efficient seat usage and no overlaps.
Technical Breakdown:
Reads POST data:
{
  "train_name": "Express1",
  "passenger": "John",
  "source": "A",
  "destination": "C"
}
Converts A-C into two segments: A-B, B-C.
For each mini-segment, finds an available seat that’s free for that part.
Allocates the same or different seat as needed per segment (if designed for that).
After successful allocation, updates the train’s bookings.
Example success response:
{
  "message": "Booking Successful!",
  "allocation": {
    "A-B": "S1",
    "B-C": "S1"
  }
}
---