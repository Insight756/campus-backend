from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
import sqlite3

app = Flask(__name__)

@app.route("/spots", methods=["GET"])
def get_spots():
    conn = sqlite3.connect("campus_parking.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, spot_number, status
    FROM parking_spots
    WHERE id >= 6 AND is_active = 1
    """)

    rows = cursor.fetchall()
    conn.close()

    spots = []
    for row in rows:
        spots.append({
            "id": row[0],
            "spot_number": row[1],
            "status": row[2]
        })

    return jsonify(spots)



from flask import request

@app.route("/book", methods=["POST"])
def book_spot():
    data = request.json

    if not data or "id" not in data:
        return jsonify({"message": "Неверные данные"}), 400

    spot_id = data.get("id")

    conn = sqlite3.connect("campus_parking.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT status FROM parking_spots
    WHERE id = ? AND is_active = 1
    """, (spot_id,))

    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({"message": "Место не найдено"}), 404

    if result[0] == "occupied":
        conn.close()
        return jsonify({"message": "Место уже занято"}), 400

    cursor.execute("""
    UPDATE parking_spots
    SET status = 'occupied'
    WHERE id = ?
    """, (spot_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Место успешно забронировано"})

@app.route("/unbook", methods=["POST"])
def unbook_spot():
    data = request.json

    if not data or "id" not in data:
        return jsonify({"message": "Неверные данные"}), 400

    spot_id = data.get("id")

    conn = sqlite3.connect("campus_parking.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT status FROM parking_spots
    WHERE id = ? AND is_active = 1
    """, (spot_id,))

    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({"message": "Место не найдено"}), 404

    if result[0] == "free":
        conn.close()
        return jsonify({"message": "Место уже свободно"}), 400

    cursor.execute("""
    UPDATE parking_spots
    SET status = 'free'
    WHERE id = ?
    """, (spot_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Бронь отменена"})

@app.route("/")
def home():
    return "Campus backend is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)