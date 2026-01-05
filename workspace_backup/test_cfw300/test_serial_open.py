import serial
import sys
import os

port = "/dev/ttyS0"

print(f"Testing access to {port}...")

if not os.path.exists(port):
    print(f"ERROR: {port} does not exist!")
    sys.exit(1)

print(f"Permissions: {oct(os.stat(port).st_mode)[-3:]}")
print(f"Owner: {os.stat(port).st_uid}:{os.stat(port).st_gid}")

try:
    s = serial.Serial(port, 9600, timeout=1)
    print("SUCCESS: Port opened!")
    s.close()
except Exception as e:
    print(f"FAILURE: Could not open port: {e}")
    sys.exit(1)
