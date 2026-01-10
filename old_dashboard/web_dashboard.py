import secrets
#!/usr/bin/env python3
"""
Cooling Tower Web Dashboard
Full control and monitoring interface for 3 VFDs + sensors
"""

from flask import Flask, redirect, render_template, jsonify, request, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import time
import logging
from datetime import datetime
from vfd_controller import MultiVFDManager
from sensor_manager import SensorManager
from pump_failover import PumpFailoverManager
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Security configuration
app.secret_key = secrets.token_hex(32)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple user class
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Default credentials (change these!)
USERNAME = 'admin'
PASSWORD_HASH = generate_password_hash('cooling2025')  # Change this password!

@login_manager.user_loader
def load_user(user_id):
    if user_id == USERNAME:
        return User(user_id)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USERNAME and check_password_hash(PASSWORD_HASH, password):
            user = User(USERNAME)
            login_user(user)
            return redirect(request.args.get('next') or '/')
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


class CoolingTowerSystem:
    def __init__(self):
        self.running = False
        self.auto_mode = False
        self.system_state = {
            'timestamp': None,
            'sensors': {'pressure_psi': 0, 'temperature_f': 0, 'a2_voltage': 0},
            'fan': {'state': 'Unknown', 'frequency': 0, 'current': 0, 'fault': 0},
            'pump_primary': {'state': 'Unknown', 'frequency': 0, 'current': 0, 'fault': 0},
            'pump_backup': {'state': 'Unknown', 'frequency': 0, 'current': 0, 'fault': 0},
            'active_pump': 'primary',
            'control_params': CONTROL_PARAMS.copy(),
            'errors': []
        }
        
        # Initialize hardware
        try:
            self.vfd_manager = MultiVFDManager(
                port=SERIAL_PORT,
                baudrate=SERIAL_BAUDRATE,
                parity=SERIAL_PARITY,
                stopbits=SERIAL_STOPBITS,
                bytesize=SERIAL_BYTESIZE
            )
            
            for name, cfg in VFD_CONFIG.items():
                self.vfd_manager.add_vfd(name, cfg['device_id'], cfg['description'])
            
            self.fan_vfd = self.vfd_manager.get_vfd('fan')
            pump_primary = self.vfd_manager.get_vfd('pump_primary')
            pump_backup = self.vfd_manager.get_vfd('pump_backup')
            
            self.pump_manager = PumpFailoverManager(
                pump_primary,
                pump_backup,
                max_errors=PUMP_FAILOVER['max_consecutive_errors'],
                check_interval=PUMP_FAILOVER['health_check_interval']
            )
            
            self.sensors = SensorManager(
                i2c_address=SENSOR_CONFIG['i2c_address'],
                gain=SENSOR_CONFIG['ads_gain']
            )
            
            self.vfd_manager.connect()
            logger.info("Hardware initialized successfully")
            
        except Exception as e:
            logger.error(f"Hardware initialization failed: {e}")
            self.system_state['errors'].append(str(e))
    
    def update_sensors(self):
        """Update sensor readings only (fast ~0.02s)"""
        try:
            sensor_data = self.sensors.read_all()
            self.system_state['sensors'] = sensor_data
            self.system_state['timestamp'] = datetime.now().isoformat()
        except Exception as e:
            logger.error(f"Sensor update error: {e}")
    
    def update_vfds(self):
        """Update VFD status (slow ~30s)"""
        try:
            # Read VFD states
            fan_status = self.fan_vfd.get_status()
            self.system_state['fan'] = {
                'state': fan_status['state'],
                'frequency': fan_status['output_frequency'],
                'current': fan_status['output_current'],
                'fault': fan_status['fault_code']
            }
            
            pump_status = self.pump_manager.get_status()
            self.system_state['active_pump'] = pump_status['active_pump']
            
            primary_status = self.pump_manager.primary.get_status()
            self.system_state['pump_primary'] = {
                'state': primary_status['state'],
                'frequency': primary_status['output_frequency'],
                'current': primary_status['output_current'],
                'fault': primary_status['fault_code']
            }
            
            backup_status = self.pump_manager.backup.get_status()
            self.system_state['pump_backup'] = {
                'state': backup_status['state'],
                'frequency': backup_status['output_frequency'],
                'current': backup_status['output_current'],
                'fault': backup_status['fault_code']
            }
        except Exception as e:
            logger.error(f"VFD update error: {e}")
    
    def update_state(self):
        """Update complete system state from hardware"""
        self.update_sensors()
        self.update_vfds()
    
    def control_loop(self):
        """Main control loop"""
        while self.running:
            try:
                self.update_state()
                
                if self.auto_mode:
                    # Automatic pressure control
                    pressure = self.system_state['sensors']['pressure_psi']
                    target = self.system_state['control_params']['target_pressure']
                    kp = self.system_state['control_params']['kp']
                    
                    error = target - pressure
                    output_hz = 30.0 + (error * kp)
                    
                    output_hz = max(
                        self.system_state['control_params']['min_frequency'],
                        min(self.system_state['control_params']['max_frequency'], output_hz)
                    )
                    
                    self.pump_manager.set_frequency(output_hz)
                    
                    # Check pump health for failover
                    if PUMP_FAILOVER['auto_failover_enabled']:
                        self.pump_manager.check_health()
                
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Control loop error: {e}")
                time.sleep(5.0)
    
    def start_system(self):
        """Start the cooling tower system"""
        if self.running:
            return
        
        self.running = True
        
        # Start fan
        self.fan_vfd.set_frequency(45.0)
        self.fan_vfd.start()
        
        # Start primary pump
        active_pump = self.pump_manager.get_active_vfd()
        active_pump.set_frequency(30.0)
        active_pump.start()
        
        # Start control thread
        self.control_thread = threading.Thread(target=self.control_loop, daemon=True)
        self.control_thread.start()
        
        logger.info("System started")
    
    def stop_system(self):
        """Stop the cooling tower system"""
        self.running = False
        self.auto_mode = False
        
        time.sleep(2.0)  # Let control loop finish
        
        self.pump_manager.stop()
        self.fan_vfd.stop()
        
        logger.info("System stopped")

# Global system instance
system = CoolingTowerSystem()

# ==================== WEB ROUTES ====================

@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/api/status')
@login_required
def get_status():
    """Get current system status"""
    response = make_response(jsonify(system.system_state))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/start', methods=['POST'])
@login_required
def start_system():
    """Start the cooling tower"""
    try:
        system.start_system()
        return jsonify({'success': True, 'message': 'System started'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@login_required
@app.route('/api/stop', methods=['POST'])
def stop_system():
    """Stop the cooling tower"""
    try:
        system.stop_system()
        return jsonify({'success': True, 'message': 'System stopped'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@login_required
@app.route('/api/auto', methods=['POST'])
def toggle_auto():
    """Toggle automatic control mode"""
    data = request.json
    system.auto_mode = data.get('enabled', False)
    return jsonify({'success': True, 'auto_mode': system.auto_mode})

@login_required
@app.route('/api/vfd/<name>/frequency', methods=['POST'])
def set_vfd_frequency(name):
    """Set VFD frequency manually"""
    try:
        data = request.json
        frequency = float(data['frequency'])
        
        if name == 'fan':
            system.fan_vfd.set_frequency(frequency)
        elif name == 'pump_primary':
            system.pump_manager.primary.set_frequency(frequency)
        elif name == 'pump_backup':
            system.pump_manager.backup.set_frequency(frequency)
        else:
            return jsonify({'success': False, 'error': 'Invalid VFD name'}), 400
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@login_required
@app.route('/api/vfd/<name>/start', methods=['POST'])
def start_vfd(name):
    """Start individual VFD"""
    try:
        if name == 'fan':
            system.fan_vfd.start()
        elif name == 'pump_primary':
            system.pump_manager.primary.start()
        elif name == 'pump_backup':
            system.pump_manager.backup.start()
        else:
            return jsonify({'success': False, 'error': 'Invalid VFD name'}), 400
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@login_required
@app.route('/api/vfd/<name>/stop', methods=['POST'])
def stop_vfd(name):
    """Stop individual VFD"""
    try:
        if name == 'fan':
            system.fan_vfd.stop()
        elif name == 'pump_primary':
            system.pump_manager.primary.stop()
        elif name == 'pump_backup':
            system.pump_manager.backup.stop()
        else:
            return jsonify({'success': False, 'error': 'Invalid VFD name'}), 400
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@login_required
@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update control parameters"""
    try:
        data = request.json
        
        if 'target_pressure' in data:
            system.system_state['control_params']['target_pressure'] = float(data['target_pressure'])
        if 'kp' in data:
            system.system_state['control_params']['kp'] = float(data['kp'])
        if 'min_frequency' in data:
            system.system_state['control_params']['min_frequency'] = float(data['min_frequency'])
        if 'max_frequency' in data:
            system.system_state['control_params']['max_frequency'] = float(data['max_frequency'])
        
        return jsonify({'success': True, 'settings': system.system_state['control_params']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@login_required
@app.route('/api/pump/switch', methods=['POST'])
def switch_pump():
    """Manually switch active pump"""
    try:
        if system.system_state['active_pump'] == 'primary':
            system.pump_manager._failover_to_backup()
        else:
            system.pump_manager._failback_to_primary()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Start status update thread
    def update_thread():
        """Fast sensor updates every 2 seconds"""
        while True:
            system.update_sensors()
            time.sleep(2.0)
    
    def vfd_update_thread():
        """Slow VFD status updates every 10 seconds"""
        while True:
            system.update_vfds()
            time.sleep(10.0)
    
    threading.Thread(target=update_thread, daemon=True).start()
    threading.Thread(target=vfd_update_thread, daemon=True).start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8001, debug=False)
