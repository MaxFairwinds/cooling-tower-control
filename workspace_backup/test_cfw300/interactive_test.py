#!/usr/bin/env python3
"""
Interactive CFW300 Test Script

Manual control and exploration of CFW300 VFD.
Use this for hands-on testing and debugging.
"""

import time
import logging
from config_cfw300 import *
from vfd_controller_cfw300 import CFW300Manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_menu():
    """Display interactive menu"""
    print("\n" + "="*60)
    print("CFW300 INTERACTIVE TEST")
    print("="*60)
    print("1. Read Status")
    print("2. Set Frequency")
    print("3. Start Forward")
    print("4. Start Reverse")
    print("5. Stop")
    print("6. Reset Fault")
    print("7. Frequency Ramp Test")
    print("8. Read All Registers")
    print("9. Exit")
    print("="*60)

def read_status(vfd):
    """Read and display VFD status"""
    print("\nReading status...")
    status = vfd.get_status()
    
    print(f"  Status Word: {status['status_word']}")
    print(f"  Speed: {status['speed_hz']:.2f} Hz (scaled: {status['speed_scaled']})")
    print(f"  Fault Code: {status['fault_code']}")
    print(f"  Healthy: {status['healthy']}")
    print(f"  Error Count: {vfd.error_count}")

def set_frequency(vfd):
    """Set frequency interactively"""
    try:
        hz = float(input("Enter frequency (Hz, 0-60): "))
        if 0 <= hz <= 60:
            vfd.set_frequency(hz)
            print(f"Set frequency to {hz} Hz")
        else:
            print("Frequency out of range!")
    except ValueError:
        print("Invalid input!")

def ramp_test(vfd):
    """Run a frequency ramp test"""
    print("\nFrequency Ramp Test")
    print("WARNING: Motor will run if connected!")
    input("Press Enter to continue or Ctrl+C to abort...")
    
    print("\nStarting ramp test...")
    vfd.start_forward()
    
    for hz in range(10, 51, 5):
        print(f"Setting {hz} Hz...")
        vfd.set_frequency(hz)
        time.sleep(2)
        status = vfd.get_status()
        print(f"  Actual: {status['speed_hz']:.2f} Hz")
    
    print("\nRamping down...")
    for hz in range(50, 9, -5):
        print(f"Setting {hz} Hz...")
        vfd.set_frequency(hz)
        time.sleep(2)
    
    print("\nStopping...")
    vfd.stop()
    print("Ramp test complete")

def read_all_registers(vfd):
    """Read all important registers"""
    print("\nReading all registers...")
    for name, addr in CFW300_REGISTERS.items():
        value = vfd.read_register(addr)
        print(f"  P{addr:03d} ({name}): {value}")

def main():
    """Main interactive loop"""
    print("Connecting to CFW300...")
    manager = CFW300Manager(SERIAL_PORT, SERIAL_BAUDRATE, RATED_FREQUENCY)
    
    if not manager.connect():
        print("ERROR: Failed to connect to serial port!")
        return 1
    
    # Add VFD
    device_id = int(input("Enter CFW300 device ID (default 101): ") or "101")
    manager.add_vfd('test', device_id, f'CFW300 ID {device_id}')
    vfd = manager.get_vfd('test')
    
    print(f"\nConnected to CFW300 (Device ID: {device_id})")
    
    try:
        while True:
            print_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                read_status(vfd)
            elif choice == '2':
                set_frequency(vfd)
            elif choice == '3':
                print("Starting FORWARD...")
                vfd.start_forward()
            elif choice == '4':
                print("Starting REVERSE...")
                vfd.start_reverse()
            elif choice == '5':
                print("Stopping...")
                vfd.stop()
            elif choice == '6':
                print("Resetting fault...")
                vfd.reset_fault()
            elif choice == '7':
                ramp_test(vfd)
            elif choice == '8':
                read_all_registers(vfd)
            elif choice == '9':
                break
            else:
                print("Invalid option!")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        print("\nStopping VFD and closing connection...")
        vfd.stop()
        manager.close()
        print("Done")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
