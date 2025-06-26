import cv2
import time
from config import SPEED_LIMIT  # Make sure config.py exists with SPEED_LIMIT = 80 or your preferred value

# Load car detector
car_cascade = cv2.CascadeClassifier('cars.xml')
video = cv2.VideoCapture('traffic.mp4')

# Get FPS of video
fps = video.get(cv2.CAP_PROP_FPS)
print("Video FPS:", fps)

# To store car position and frame for tracking
car_positions = {}
frame_id = 0
car_id_counter = 0

def estimate_speed(x1, x2, t):
    distance_pixels = abs(x2 - x1)
    if t <= 0:
        return 0
    speed = (distance_pixels / t) * 0.1  # scale factor ~0.1 for demo
    return speed

while True:
    ret, frame = video.read()
    if not ret:
        break

    frame_id += 1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cars = car_cascade.detectMultiScale(gray, 1.1, 2)

    current_car_positions = []

    for (x, y, w, h) in cars:
        center_x = x + w // 2
        center_y = y + h // 2
        current_car_positions.append((center_x, center_y, x, y, w, h))

    for pos in current_car_positions:
        cx, cy, x, y, w, h = pos
        matched = False

        for car_id in list(car_positions.keys()):
            prev_cx, prev_frame = car_positions[car_id]

            if abs(cx - prev_cx) < 40:  # basic matching by X position
                time_diff = (frame_id - prev_frame) / fps
                speed = estimate_speed(prev_cx, cx, time_diff)

                # Filter for realistic speeds
                if 20 <= speed <= 150:
                    label = f"Speed: {int(speed)} km/h"
                    cv2.putText(frame, label, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                    if speed > SPEED_LIMIT:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red for overspeed
                        
                        # Log fine to file
                        with open("fine_log.txt", "a") as file:
                            file.write(f"Overspeed Vehicle Detected - Speed: {speed:.2f} km/h at frame {frame_id}\n")
                    else:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green = safe

                else:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)  # Blue for unknown or unrealistic

                # Update position
                car_positions[car_id] = (cx, frame_id)
                matched = True
                break

        if not matched:
            # Assign new car ID
            car_positions[car_id_counter] = (cx, frame_id)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
            car_id_counter += 1

    # Display frame
    cv2.imshow("Speed Estimation", frame)

    # Exit with ESC key
    if cv2.waitKey(30) & 0xFF == 27:
        break

# Release resources
video.release()
cv2.destroyAllWindows()
