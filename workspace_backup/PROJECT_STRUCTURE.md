# RaspCoolingTower Project Structure

## Directory Organization

```
prograde-kilonova/
├── production/              # G540 Production Code (IDs 1-3)
│   ├── config.py
│   ├── vfd_controller.py
│   ├── sensor_manager.py
│   ├── main_control.py
│   └── pump_failover.py
│
├── test_cfw300/            # CFW300 Test Environment (IDs 101-103)
│   ├── config_cfw300.py
│   ├── vfd_controller_cfw300.py
│   ├── test_suite.py
│   ├── interactive_test.py
│   ├── deploy_cfw300.sh
│   └── README_CFW300.md
│
├── manage.sh               # Production management script
├── deploy_code.sh          # Production deployment
└── README.md               # Main project README
```

## Production vs Test

| Aspect | Production (G540) | Test (CFW300) |
|--------|-------------------|---------------|
| **Purpose** | Live cooling tower control | Bench testing & validation |
| **Device IDs** | 1, 2, 3 | 101, 102, 103 |
| **VFD Model** | Galt G540 | WEG CFW300 |
| **Registers** | TBD from manual | P682, P681, P683 |
| **Directory** | `production/` | `test_cfw300/` |
| **Motor** | Required | Optional |

## Quick Start

### Production System
```bash
cd production
./deploy_code.sh    # Deploy to Pi
./manage.sh test    # Run 10-second test
```

### CFW300 Testing
```bash
cd test_cfw300
./deploy_cfw300.sh          # Deploy to Pi
ssh max@coolingtower.local
cd test_cfw300
source ../venv/bin/activate
python3 test_suite.py       # Automated tests
python3 interactive_test.py # Manual control
```

## Why Separate?

1. **Safety**: Prevents accidental commands to production equipment
2. **Clarity**: Different register maps clearly separated
3. **Testing**: Validate all logic before touching live system
4. **Development**: Test new features on CFW300 first
