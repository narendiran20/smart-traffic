if speed > SPEED_LIMIT:
    with open("fine_log.txt", "a") as file:
        file.write(f"Overspeed Vehicle Detected - Speed: {speed:.2f} km/h at frame {frame_id}\n")
