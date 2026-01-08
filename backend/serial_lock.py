"""
File-based lock for serializing Modbus RTU access across multiple processes
"""
import fcntl
import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class SerialLock:
    """Process-safe file lock for serial port access"""
    
    LOCK_FILE = '/tmp/vfd_serial.lock'
    
    def __init__(self, timeout=5.0):
        self.timeout = timeout
        self.lockfile = None
        
    @contextmanager
    def acquire(self):
        """Acquire exclusive lock with timeout"""
        self.lockfile = open(self.LOCK_FILE, 'w')
        start = time.time()
        acquired = False
        
        try:
            while True:
                try:
                    fcntl.flock(self.lockfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    logger.debug("Lock acquired")
                    acquired = True
                    break
                except IOError as e:
                    if time.time() - start > self.timeout:
                        raise TimeoutError(f"Could not acquire lock after {self.timeout}s")
                    time.sleep(0.01)
            
            yield
            
        finally:
            if acquired:
                try:
                    fcntl.flock(self.lockfile.fileno(), fcntl.LOCK_UN)
                    logger.debug("Lock released")
                except:
                    pass
            try:
                self.lockfile.close()
            except:
                pass
