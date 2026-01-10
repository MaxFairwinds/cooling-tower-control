# A2 SENSOR TECHNICAL ANALYSIS REPORT
## Date: January 8, 2026

---

## HARDWARE CONFIGURATION

**ADC:** ADS1115 16-bit I2C ADC (address 0x48)
- **Gain setting:** 1 (±4.096V range)
- **Resolution:** 16-bit (0.125mV per bit)
- **Channel:** A2 (differential input)

**Voltage Divider Circuit:**
- **Supply voltage (Vcc):** 3.3V
- **Bias resistor (R_bias):** 100Ω to 3.3V
- **Sensor resistance:** ~84-87Ω (measured with multimeter)
- **Configuration:** Sensor connected between A2 and GND, bias resistor between A2 and 3.3V

**Expected voltage calculation:**
```
V_a2 = Vcc × R_sensor / (R_sensor + R_bias)
V_a2 = 3.3V × 87Ω / (87Ω + 100Ω) = 1.535V
```

---

## TEST METHODOLOGY

**Test Duration:** 20 seconds (40 samples at 0.5-second intervals)

**Sampling Parameters:**
- Sample rate: 2 Hz (500ms between readings)
- Total samples: 40
- ADC read method: AnalogIn(ads, 2).voltage
- No averaging or filtering applied (raw readings)

**Test Code:**
```python
import board, busio, time
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1
chan = AnalogIn(ads, 2)

for i in range(40):
    v = chan.voltage
    print(f'{i:2d}s: {v:.4f}V')
    time.sleep(0.5)
```

---

## MEASUREMENT RESULTS

### Statistical Summary
- **Mean voltage:** 1.5326V
- **Minimum voltage:** 1.3478V
- **Maximum voltage:** 1.5460V
- **Voltage range:** 0.1983V (198.3mV)
- **Standard deviation:** ~0.015V (15mV) excluding anomaly
- **Coefficient of variation:** 0.98%

### Nominal Operation
- **Typical voltage:** 1.530V - 1.546V
- **Normal variation:** ±5-15mV
- **Baseline stability:** Very stable (±1% variation)

---

## VOLTAGE ANOMALY DETECTION

### Primary Anomaly Event
**Timestamp:** Sample #8 (4 seconds into test)

**Voltage sequence:**
```
Sample #7:  1.5312V  (baseline)
Sample #8:  1.3478V  ← DROP OF 0.1835V (183.5mV)
Sample #9:  1.5309V  ← RECOVERY +0.1831V
Sample #10: 1.5410V  (back to baseline)
```

**Anomaly characteristics:**
- **Drop magnitude:** 183.5mV (12% voltage decrease)
- **Duration:** <1 second (single sample)
- **Recovery time:** Immediate (next sample)
- **Recovery pattern:** Clean return to baseline

**Calculated resistance during anomaly:**
```
R = V × R_bias / (Vcc - V)
R = 1.3478V × 100Ω / (3.3V - 1.3478V)
R = 69.04Ω
```

**Resistance change:** 87Ω → 69Ω → 87Ω (18Ω / 21% decrease)

### Secondary Variations
**Samples with >10mV changes:**
- Sample #10: +10.1mV
- Sample #18: +12.9mV  
- Sample #19: -12.4mV
- Sample #24: +12.1mV
- Sample #26: +11.4mV
- Sample #27: -12.9mV

**Pattern:** Small, brief deviations (10-13mV) occurring randomly throughout test

---

## TECHNICAL INTERPRETATION

### Signal Characteristics

1. **Baseline Stability: EXCELLENT**
   - Excluding anomalies: ±1% voltage variation
   - Consistent with a passive resistive sensor
   - Far too stable for temperature measurement in cooling tower environment

2. **Anomaly Pattern: DISCRETE EVENT**
   - Single-sample duration (<500ms)
   - Sharp transition down and immediate recovery
   - No gradual drift or exponential decay
   - Suggests: physical switching, contact closure, or detection event

3. **Noise Floor: LOW**
   - ±5-15mV typical variation
   - Equivalent to ±2.7-8.1Ω resistance change
   - Clean signal with minimal EMI/electrical noise

### 20-Hour Historical Data Context

From continuous logging (1,358 samples @ 60-second intervals):
- **Average voltage:** 1.5346V
- **Voltage std dev:** 0.0423V (42.3mV)
- **Voltage range:** 1.3561V - 3.0765V
- **95th percentile change:** 0.0088V per minute

**Long-term anomalies observed:**
- Occasional drops to 1.35-1.36V (matching live test)
- Rare spike to 3.08V (once in 1,358 samples)
- Zero correlation with water temperature changes (r = -0.044)
- Zero correlation with ambient temperature (40°F outside, sensor stable at 70°F-equivalent)

---

## SENSOR TYPE ANALYSIS

### Ruled Out:
- ❌ **RTD Temperature Sensor** - No response to 13°F water temp change or 30°F ambient change
- ❌ **Thermistor** - Would show exponential resistance-temperature curve
- ❌ **Fixed Resistor** - Demonstrated active voltage changes
- ❌ **High Water Level Switch** - Located 6" above normal water level, not at high-level point

### Likely Candidates:

#### 1. **Humidity/Condensation Sensor** (Most Probable)
- **Evidence:** 
  - Located in high-humidity cooling tower interior
  - Stable reading = constant ~95%+ RH environment
  - Brief drops = momentary condensation/droplet contact
  - 84Ω nominal = typical bias resistor for capacitive humidity sensors
- **Expected behavior:** Stable in saturated air, changes with droplet contact/evaporation

#### 2. **Capacitive Proximity/Level Sensor**
- **Evidence:**
  - 6" mounting height above water
  - Brief changes = water splash or surface wave detection
  - Capacitance changes with dielectric (air vs water proximity)
- **Expected behavior:** Stable baseline, spikes when water approaches

#### 3. **Conductivity/Moisture Detection**
- **Evidence:**
  - Small form factor (1" box)
  - Discrete on/off style events
  - Resistance drop = increased conductivity path
- **Expected behavior:** Dry = high R, wet = low R

---

## CONCLUSIONS

1. **Sensor is ACTIVE and FUNCTIONAL** - Not a dead component or fixed resistor

2. **NOT measuring temperature** - Zero thermal response over 20+ hour test period

3. **Detecting discrete events** - Single-sample anomalies suggest binary or threshold detection

4. **Stable baseline operation** - 99% of time reads 1.53V ±15mV

5. **Environmental sensor** - Most likely humidity, condensation, or water proximity detection

---

## RECOMMENDATIONS

1. **Identify sensor model** - Check device for markings/part numbers
2. **Consult installation documentation** - May indicate original purpose
3. **Correlate anomalies** - Check if voltage drops align with pump cycling, fan operation, or water level changes
4. **Measure wire count** - 2-wire = simple resistive, 3+ = active sensor with power
5. **Test water contact** - Introduce controlled moisture/water proximity to trigger response

---

## DATA AVAILABILITY

- **Live test data:** 40 samples, 0.5s intervals
- **Historical data:** 1,358 samples, 60s intervals, 22.6 hours duration
- **CSV log location:** /var/log/cooling-tower/sensor_data.csv
- **Analysis scripts:** Available in workspace

---

**Report prepared for technical consultation regarding unknown sensor identification**
