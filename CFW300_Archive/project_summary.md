# Project Status: RaspCoolingTower & CFW300 VFD Integration

## Executive Summary
This project controls a WEG CFW300 Variable Frequency Drive (VFD) via Modbus RTU using a Raspberry Pi 4B.
After diagnosing a hardware failure with the initial "Waveshare RS485 CAN HAT (B)", the system was migrated to a USB-RS485 adapter, which has been successfully verified.

## Hardware Configuration
| Component | Status | Details |
| :--- | :--- | :--- |
| **Controller** | Online | Raspberry Pi 4B (Bookworm OS) |
| **Interface** | **Verified** | USB-RS485 Adapter (`/dev/ttyUSB0`) |
| **Legacy Interface** | **Defective** | Waveshare RS485 CAN HAT (B) - RS485 Transceiver Dead |
| **VFD** | **Connected** | WEG CFW300 (Modbus RTU) |
| **Sensors** | Integrated | ADS1115 ADC (Pressure/Temp) |

### VFD Communication Settings (Confirmed)
- **Baud Rate:** 19,200 (P310 = 1)
- **Data Bits:** 8
- **Parity:** Even (P311 = 1)
- **Stop Bits:** 1
- **Slave ID:** 1 (P308 = 1)

## Software Architecture

### Core Components
- **`vfd_controller_cfw300.py`**: Main class for direct VFD control. Implements Modbus read/write for frequency, start/stop, and status.
- **`config_cfw300.py`**: Configuration constants (Registers, Modbus settings).
- **`sensor_manager_cfw300.py`** (Planned): Interface for ADS1115 sensors.

### Diagnostic & Test Scripts (in `test_cfw300/`)
| Script | Purpose | Status |
| :--- | :--- | :--- |
| `usb_vfd_test.py` | verifies connection with USB adapter | **PASS** |
| `rs485_loopback.py` | Tests hardware loopback (HAT) | FAIL |
| `can_toggle.py` | Tested CAN bus on HAT | PASS |
| `interrupt_test.py` | Diagnosed IRQ failure on HAT | FAIL |

## Recent Achievements
1.  **Fault Isolation**: Conclusively proved the Waveshare HAT RS-485 transceiver was hardware defective (0V output) despite working GPIO control and CAN bus.
2.  **Mitigation**: Switched to USB-RS485 adapter.
3.  **Parameter Discovery**: Identified correct VFD parameters (19200/8E1) opposed to standard defaults (9600/8N1), enabling successful communication.

## Next Steps
1.  **Integration**: Update `vfd_controller_cfw300.py` to use the proven `usb_vfd_test.py` configuration.
2.  **Control Loop**: Finalize the main control loop to read sensors and adjust VFD speed.
3.  **Deployment**: Configure systemd service for auto-start.

## Backup
A complete backup of the workspace is available in `workspace_backup.zip`.
