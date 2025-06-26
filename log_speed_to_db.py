import cv2
import sqlite3
import time

# Load Haar Cascade
car_cascade = cv2.CascadeClassifier('cars.xml')
video = cv2.VideoCapture('traffic.mp4')

# Create/connect to SQLite database
conn = sqlite3.connect('traffic_data.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicle_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        speed REAL
    )
''')
conn.commit()

# Get FPS
fps = video.get(cv2.CAP_PROP_FPS)
frame_id = 0
car_positions = {}

def estimate_speed(x1, x2, t):
    distance = abs(x2 - x1)
    return (distance / t) * 0.1  # scale factor

while True:
    ret, frame = video.read()
    if not ret:
        break

    frame_id += 1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cars = car_cascade.detectMultiScale(gray, 1.1, 2)

    for i, (x, y, w, h) in enumerate(cars):
        center_x = x + w // 2
        car_id = i

        if car_id in car_positions:
            prev_x, prev_frame = car_positions[car_id]
            time_diff = (frame_id - prev_frame) / fps
            speed = estimate_speed(prev_x, center_x, time_diff)

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO vehicle_log (timestamp, speed) VALUES (?, ?)", (timestamp, speed))
            conn.commit()

            label = f"Speed: {int(speed)} km/h"
            cv2.putText(frame, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            color = (0, 0, 255) if speed > 80 else (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

        else:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)

        car_positions[car_id] = (center_x, frame_id)

    cv2.imshow("Vehicle Speed Logging", frame)
    if cv2.waitKey(30) & 0xFF == 27:
        break

video.release()
conn.close()
cv2.destroyAllWindows()

