import cv2
import time
from config import SPEED_LIMIT
from telegram_alert import send_telegram_alert  # 🆕 Make sure telegram_alert.py exists

# Load pre-trained car classifier
car_cascade = cv2.CascadeClassifier('cars.xml')

# Load video
video = cv2.VideoCapture('traffic.mp4')

# Get video FPS
fps = video.get(cv2.CAP_PROP_FPS)

# Track positions to estimate speed
car_positions = {}
frame_id = 0

def estimate_speed(x1, x2, time_diff):
    distance_pixels = abs(x2 - x1)
    speed = (distance_pixels / time_diff) * 0.1  # Approximate conversion to km/h
    return speed

while True:
    ret, frame = video.read()
    if not ret:
        break

    frame_id += 1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect cars
    cars = car_cascade.detectMultiScale(gray, 1.1, 2)

    for i, (x, y, w, h) in enumerate(cars):
        center_x = x + w // 2
        car_id = i  # Simple logic (can be improved with tracking)

        if car_id in car_positions:
            prev_x, prev_frame = car_positions[car_id]
            time_diff = (frame_id - prev_frame) / fps

            if time_diff > 0:
                speed = estimate_speed(prev_x, center_x, time_diff)
                label = f"Speed: {int(speed)} km/h"
                cv2.putText(frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                if speed > SPEED_LIMIT:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 🔴 Red for overspeed

                    # Save to fine log
                    with open("fine_log.txt", "a") as f:
                        f.write(f"Overspeed Detected: {speed:.2f} km/h at frame {frame_id}\n")

                    # Send Telegram alert
                    alert_msg = f"🚨 Speed Alert!\nSpeed: {int(speed)} km/h\nFrame: {frame_id}"
                    send_telegram_alert(alert_msg)

                else:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 🟢 Green for safe
        else:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)  # 🔵 Blue for new car

        # Update position
        car_positions[car_id] = (center_x, frame_id)

    # Show result
    cv2.imshow('Vehicle Detection with Speed', frame)

    # Exit on ESC key
    if cv2.waitKey(30) & 0xFF == 27:
        break

video.release()
cv2.destroyAllWindows()
