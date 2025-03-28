
# 🚆 Train Seat Allocation and Dynamic Booking System

## 📝 Project Overview
A full-stack web application for train seat allocation with **Normal Booking** and **Dynamic Booking** functionalities. The system ensures **route-based segment checks** and **dynamic seat switching** to maximize seat utilization.

### ✅ Core Features
- MongoDB-backed data storage
- Segment-wise seat locking
- Smart dynamic seat reallocation with switching
- Real-time seat status visualization (Green, Red, Blue)
- Reset functionality for individual trains
- Booking history tracking
- API-driven, modular, and scalable design

## 💻 Technology Stack
| Layer       | Technology           |
|------------ |----------------------|
| Frontend    | HTML, CSS3, JavaScript (Embedded) |
| Backend     | Python Flask (REST APIs) |
| Database    | MongoDB (NoSQL) |

## 🗂 File Structure
```
├── app.py                 # Main Flask App
├── 
├── templates/
│   ├── index.html         # Add Train Page
│   ├── normal.html        # Normal Booking Page
│   ├── dynamic.html       # Dynamic Booking Page
├── static/
│   ├── style.css          # Styling File
└── README.md              # Project Documentation
```

## 🔧 Modules Breakdown

### 1️⃣ Add Train Module (index.html & addtrain.py)
#### ✅ Purpose:
Capture new train details dynamically and store them in MongoDB.

#### ✅ Inputs:
- **Train Name**
- **Junctions:** Dynamic input (e.g., A=1, B=2, C=3…)
- **Seats:** Max 20 (S1, S2, ..., S20)

#### ✅ Process:
- Auto-generate all possible segments between junction pairs
- Format for MongoDB:
```json
{
  "train_name": "Express 101",
  "junctions": ["A", "B", "C"],
  "segments": [["A", "B"], ["B", "C"], ["A", "C"]],
  "seats": ["S1", "S2"],
  "bookings": []
}
```
- Store data in the **trains** collection

### 2️⃣ Normal Booking Module (normal.html & normal.py)
#### ✅ Purpose:
Passenger books a specific seat for a specific segment.

#### ✅ Inputs:
- **Passenger Names:** A, B, C, D (predefined)
- **Train Selection**
- **Segment Selection**
- **Seat Selection** (Parallel seat layout with seat names inside boxes)

#### ✅ Booking Logic:
1. **Check segment overlaps** (Only lock the seat if no overlap)
2. **Color-coded real-time UI updates:**
   - 🟢 **Green:** Available
   - 🔴 **Red:** Booked
   - 🔵 **Blue:** Selected
3. **Booking History Table:** Shows passenger, segment, and seat

#### ✅ Example Booking:
| Passenger | Segment | Seat | Result |
|---------- |-------- |----- |------- |
| A         | A-B     | S1   | ✅ Booked |
| B         | B-C     | S1   | ✅ Booked (No overlap) |
| C         | A-C     | S1   | ❌ Rejected (Overlaps A-B) |
| C         | A-C     | S2   | ✅ Booked |

#### ✅ Reset Button: Clears only the selected train's bookings.

### 3️⃣ Dynamic Booking Module (dynamic.html & dynamic.py)
#### ✅ Purpose:
Smart allocation for long routes using **dynamic seat switching**.

#### ✅ Algorithm Used:
**Greedy + Backtracking Hybrid Algorithm**

#### ✅ Process:
1. Analyze journey (source → destination)
2. Attempt continuous seat assignment (Greedy)
3. If blocked, backtrack and try switching seats mid-journey
4. Allocate free seats segment-wise
5. If no valid path, return "Train Full"

#### ✅ Example Scenario:
| Passenger | Segment | Seat Assignment |
|---------- |-------- |--------------- |
| A         | A-B     | S1             |
| B         | B-C     | S2             |
| C         | A-C     | S2 (A-B), S1 (B-C) |

#### ✅ Rules:
- Seat locks apply per segment
- Unlimited seat switches allowed until journey completes
- Reset clears only the selected train's bookings

## 🗃 MongoDB Database Design
**Collection:** `trains`
```json
{
  "train_name": "Train XYZ",
  "junctions": ["A", "B", "C", "D"],
  "segments": [["A", "B"], ["B", "C"], ["A", "C"], ["C", "D"], ["A", "D"], ["B", "D"]],
  "seats": ["S1", "S2", "S3", "S4"],
  "bookings": [
    {"passenger": "A", "segment": ["A", "B"], "seat": "S1"},
    {"passenger": "B", "segment": ["B", "C"], "seat": "S2"}
  ]
}
```

## 🔗 Backend API Endpoints
------------------------------------------------------------------
| API             | Method | Description                         |
|---------------- |------- |-------------------------------------|
| /add_train      | POST   | Add new train                       |
| /get_trains     | GET    | Fetch all trains                    |
| /get_segments   | GET    | Fetch segments of a selected train  |
| /book_normal    | POST   | Book seat using static logic        |
| /book_dynamic   | POST   | Book seat with dynamic switching    |
| /reset          | POST   | Clear bookings for a train          |
-----------------------------------------------------------------
## 🤖 Dynamic Allocation Algorithm Flow (Greedy + Backtracking)
1. Passenger selects a train and journey (source → destination)
2. System checks seat availability **segment by segment**
3. Greedy attempt to allocate **one seat** for the entire journey
4. If fails, **backtracking** applies to attempt mid-journey seat switches
5. Continue until a valid seat path is found
6. If no valid path → Output: **"Train Full"**
7. Update **booking history** and **UI seat colors**

## 📈 Optional Advanced Features for Future Expansion
- 🔄 **Seat Releasing Post Journey**
- 🔍 **Passenger Journey Preview Before Booking**
- 📊 **Booking Statistics Dashboard**
- ✏️ **Booking Modification / Cancellation**
- 🛠 **Admin Dashboard for CRUD operations**
- 🗄 **Use train IDs for database optimization**

## 🛠 Installation & Setup
```bash
pip install flask pymongo
python app.py
```
- Open the respective HTML pages to test (index.html, normal.html, dynamic.html)
- MongoDB should be running locally or remotely

## 🚀 Example User Flow
1. **Add Train:** Name, Junctions, Seats → Stored in DB
2. **Normal Booking:** Book static segment-wise seat → Check overlap → Lock seat
3. **Dynamic Booking:** Book long journey → Auto seat switch if required
4. **Reset:** Clears only that train's bookings

## 📌 License & Contributions
✅ Open for contributions  
✅ MIT License  
✅ Suggestions for AI-based enhancements welcome

## ✅ Conclusion
This system efficiently handles:
- Segment-wise train seat bookings
- Dynamic seat reallocation for complex journeys
- Real-time UI updates and MongoDB-based persistence

Scalable for:
- Multi-train operations
- Future predictive AI-based booking systems
- Expansion to full railway seat reservation systems

📂 Database Name: train_booking_system
✅ Collection 1: trains
Stores train-specific data including junctions, segments, seat details, and bookings.

📄 Example Document:
json
Copy
Edit
{
  "_id": "train_id_1",
  "train_name": "Express 101",
  "junctions": ["A", "B", "C", "D"],
  "segments": [["A", "B"], ["B", "C"], ["C", "D"], ["A", "C"], ["B", "D"], ["A", "D"]],
  "seats": ["S1", "S2", "S3", "S4", "S5"],
  "bookings": [
    {
      "passenger": "A",
      "segment": ["A", "B"],
      "seat": "S1"
    },
    {
      "passenger": "B",
      "segment": ["B", "C"],
      "seat": "S2"
    }
  ]
}
✅ Collection 2 (Optional for History): booking_history
Maintains a record of all completed or historical bookings for audit or display.

📄 Example Document:
json
Copy
Edit
{
  "_id": "history_id_1",
  "train_id": "train_id_1",
  "passenger": "C",
  "journey": ["A", "C"],
  "seats_assigned": [
    {"segment": ["A", "B"], "seat": "S3"},
    {"segment": ["B", "C"], "seat": "S2"}
  ],
  "booking_type": "dynamic",
  "timestamp": "2025-03-21T10:30:00Z"
}
✅ Collection 3 (Optional): passengers
If you want a detailed passenger record (even though passenger names are static like A, B, C, D).

json
Copy
Edit
{
  "_id": "passenger_id_A",
  "name": "A",
  "bookings": [
    {"train_id": "train_id_1", "segment": ["A", "B"], "seat": "S1"}
  ]
}
✅ Collection 4 (Optional for Admin): trains_meta
Contains metadata like created time, updated time, reset status.
json
Copy
Edit
{
  "_id": "meta_train_id_1",
  "train_id": "train_id_1",
  "created_at": "2025-03-21T09:00:00Z",
  "last_updated": "2025-03-21T10:00:00Z",
  "reset_status": false
}
🔁 Data Flow Summary:
Add Train: Populates trains collection with junctions, segments, seats.
Normal Booking: Updates bookings array in the respective train document.
Dynamic Booking: Updates bookings with possible seat switches and logs in booking_history.
Reset: Clears the bookings array of a specific train document.
Booking History: booking_history can be shown as a table for UI/Reports.