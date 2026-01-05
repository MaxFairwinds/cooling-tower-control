#!/usr/bin/env python3
"""
CFW300 Communication Test Suite

Automated tests for validating RS-485 and Modbus communication
with WEG CFW300 VFD. No motor required.
"""

import sys
import time
import logging
from config_cfw300 import *
from vfd_controller_cfw300 import CFW300Manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestResult:
    """Simple test result tracker"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, name):
        self.passed += 1
        self.tests.append((name, True, None))
        print(f"✓ PASS: {name}")
        logger.info(f"PASS: {name}")
    
    def add_fail(self, name, reason):
        self.failed += 1
        self.tests.append((name, False, reason))
        print(f"✗ FAIL: {name} - {reason}")
        logger.error(f"FAIL: {name} - {reason}")
    
    def summary(self):
        total = self.passed + self.failed
        print("\n" + "="*60)
        print(f"TEST SUMMARY: {self.passed}/{total} passed")
        print("="*60)
        if self.failed > 0:
            print("\nFailed tests:")
            for name, passed, reason in self.tests:
                if not passed:
                    print(f"  - {name}: {reason}")
        return self.failed == 0


def test_connection(manager):
    """Test 1: RS-485 Connection"""
    result = TestResult()
    
    print("\n--- Test 1: RS-485 Connection ---")
    if manager.connect():
        result.add_pass("RS-485 connection established")
    else:
        result.add_fail("RS-485 connection", "Failed to open serial port")
    
    return result


def test_single_vfd_communication(manager, device_id=101):
    """Test 2: Single VFD Communication"""
    result = TestResult()
    
    print(f"\n--- Test 2: Single VFD Communication (ID {device_id}) ---")
    
    # Add VFD
    manager.add_vfd('test1', device_id, f'CFW300 Test ID {device_id}')
    vfd = manager.get_vfd('test1')
    
    # Test read
    status = vfd.read_register(CFW300_REGISTERS['STATUS_WORD'])
    if status is not None:
        result.add_pass(f"Read status word from device {device_id}")
    else:
        result.add_fail(f"Read status word", f"No response from device {device_id}")
        return result
    
    # Test write (frequency setpoint)
    if vfd.set_frequency(30.0):
        result.add_pass(f"Write frequency setpoint to device {device_id}")
    else:
        result.add_fail(f"Write frequency setpoint", "Write failed")
    
    # Verify write
    time.sleep(0.2)
    status_data = vfd.get_status()
    if status_data['speed_scaled'] is not None:
        expected = vfd.hz_to_scaled(30.0)
        actual = status_data['speed_scaled']
        if abs(actual - expected) < 10:  # Allow small tolerance
            result.add_pass(f"Verify frequency setpoint (expected ~{expected}, got {actual})")
        else:
            result.add_fail(f"Verify frequency setpoint", f"Mismatch: expected {expected}, got {actual}")
    
    return result


def test_frequency_scaling(manager):
    """Test 3: Frequency Scaling"""
    result = TestResult()
    
    print("\n--- Test 3: Frequency Scaling ---")
    
    vfd = manager.get_vfd('test1')
    if not vfd:
        result.add_fail("Frequency scaling", "VFD not initialized")
        return result
    
    # Test various frequencies
    test_freqs = [0.0, 15.0, 30.0, 45.0, 60.0]
    for hz in test_freqs:
        scaled = vfd.hz_to_scaled(hz)
        back_to_hz = vfd.scaled_to_hz(scaled)
        
        if abs(back_to_hz - hz) < 0.1:
            result.add_pass(f"Scaling {hz} Hz -> {scaled} -> {back_to_hz:.2f} Hz")
        else:
            result.add_fail(f"Scaling {hz} Hz", f"Round-trip error: {back_to_hz:.2f} Hz")
    
    return result


def test_control_commands(manager):
    """Test 4: Control Commands (Start/Stop)"""
    result = TestResult()
    
    print("\n--- Test 4: Control Commands ---")
    print("WARNING: Motor will start if connected!")
    print("Press Ctrl+C within 3 seconds to abort...")
    
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        result.add_fail("Control commands", "Aborted by user")
        return result
    
    vfd = manager.get_vfd('test1')
    if not vfd:
        result.add_fail("Control commands", "VFD not initialized")
        return result
    
    # Set low frequency for safety
    vfd.set_frequency(10.0)
    time.sleep(0.2)
    
    # Test start
    if vfd.start_forward():
        result.add_pass("Send START FORWARD command")
    else:
        result.add_fail("Send START FORWARD command", "Command failed")
    
    time.sleep(2)
    
    # Test stop
    if vfd.stop():
        result.add_pass("Send STOP command")
    else:
        result.add_fail("Send STOP command", "Command failed")
    
    return result


def test_error_handling(manager):
    """Test 5: Error Handling"""
    result = TestResult()
    
    print("\n--- Test 5: Error Handling ---")
    
    # Try to communicate with non-existent device
    manager.add_vfd('ghost', 250, 'Non-existent VFD')
    ghost = manager.get_vfd('ghost')
    
    status = ghost.read_register(CFW300_REGISTERS['STATUS_WORD'])
    if status is None:
        result.add_pass("Timeout on non-existent device")
    else:
        result.add_fail("Timeout handling", "Got response from non-existent device")
    
    if ghost.error_count > 0:
        result.add_pass("Error counter incremented")
    else:
        result.add_fail("Error counter", "Not incremented on failure")
    
    return result


def main():
    """Run all tests"""
    print("="*60)
    print("CFW300 COMMUNICATION TEST SUITE")
    print("="*60)
    print(f"Serial Port: {SERIAL_PORT}")
    print(f"Baudrate: {SERIAL_BAUDRATE}")
    print(f"Device ID: 101")
    print("="*60)
    
    manager = CFW300Manager(SERIAL_PORT, SERIAL_BAUDRATE, RATED_FREQUENCY)
    all_results = []
    
    try:
        # Run tests
        all_results.append(test_connection(manager))
        all_results.append(test_single_vfd_communication(manager, 101))
        all_results.append(test_frequency_scaling(manager))
        all_results.append(test_control_commands(manager))
        all_results.append(test_error_handling(manager))
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test suite error: {e}", exc_info=True)
    finally:
        manager.stop_all()
        manager.close()
    
    # Print summary
    print("\n" + "="*60)
    print("OVERALL TEST RESULTS")
    print("="*60)
    total_pass = sum(r.passed for r in all_results)
    total_fail = sum(r.failed for r in all_results)
    total = total_pass + total_fail
    
    print(f"Total: {total_pass}/{total} tests passed")
    
    if total_fail > 0:
        print(f"\n{total_fail} tests failed - see details above")
        return 1
    else:
        print("\n✓ All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
