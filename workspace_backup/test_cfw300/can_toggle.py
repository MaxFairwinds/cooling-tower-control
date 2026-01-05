import os
import time
import subprocess

def send_burst():
    # Send a burst of frames to keep the bus busy (Dominant)
    # Using cangen with a count limit is cleaner than starting/stopping a process
    subprocess.run("cangen can0 -g 0 -n 100 -I 42 -L 8 -D i", shell=True)

print("=" * 60)
print("CAN VOLTAGE TOGGLE TEST")
print("=" * 60)
print("Alternating between BUSY (Active) and IDLE (2.5V) every 2 seconds...")
print("Measure CAN H or CAN L to see the voltage jump.")
print("Press Ctrl+C to stop.")
print()

try:
    # Ensure interface is up
    os.system("sudo ip link set can0 up type can bitrate 500000 2>/dev/null")
    
    while True:
        print(">>> SENDING DATA (Voltage should change)")
        # Run cangen in background or loop it fast
        # We use a loop of cangen calls to create a "pulse"
        t_end = time.time() + 2
        while time.time() < t_end:
             subprocess.run("cangen can0 -g 0 -n 10 -I 42 -L 8 -D i >/dev/null 2>&1", shell=True)
        
        print("... IDLE (Voltage should be ~2.5V)")
        time.sleep(2)

except KeyboardInterrupt:
    print("\nStopped.")
except Exception as e:
    print(f"\nError: {e}")
