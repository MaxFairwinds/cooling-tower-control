import serial
import time

try:
    p = serial.Serial("/dev/ttySC0", 9600)
    print("Sending data...")
    for _ in range(50):
        p.write(b"U")
        time.sleep(0.1)
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
