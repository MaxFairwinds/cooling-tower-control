import time
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class PumpState(Enum):
    """Pump operational states"""
    PRIMARY = "primary"
    BACKUP = "backup"
    FAILED = "failed"

class PumpFailoverManager:
    """Manages automatic failover between primary and backup pump motors"""
    
    def __init__(self, primary_vfd, backup_vfd, max_errors=3, check_interval=5.0):
        """
        Initialize pump failover manager.
        
        Args:
            primary_vfd: VFDController for primary pump
            backup_vfd: VFDController for backup pump
            max_errors: Maximum consecutive errors before failover
            check_interval: Health check interval in seconds
        """
        self.primary = primary_vfd
        self.backup = backup_vfd
        self.max_errors = max_errors
        self.check_interval = check_interval
        
        self.active_pump = PumpState.PRIMARY
        self.last_check = time.time()
        
        logger.info("Pump Failover Manager initialized")
        logger.info(f"Primary: {primary_vfd.description}")
        logger.info(f"Backup: {backup_vfd.description}")
    
    def get_active_vfd(self):
        """Get the currently active pump VFD"""
        if self.active_pump == PumpState.PRIMARY:
            return self.primary
        elif self.active_pump == PumpState.BACKUP:
            return self.backup
        return None
    
    def check_health(self):
        """Check health and perform failover if needed"""
        now = time.time()
        if now - self.last_check < self.check_interval:
            return  # Not time to check yet
        
        self.last_check = now
        
        if self.active_pump == PumpState.PRIMARY:
            if not self.primary.is_healthy(self.max_errors):
                logger.warning(f"Primary pump unhealthy (errors: {self.primary.error_count})")
                self._failover_to_backup()
        
        elif self.active_pump == PumpState.BACKUP:
            # Check if primary has recovered
            if self.primary.is_healthy(self.max_errors):
                logger.info("Primary pump recovered, switching back")
                self._failback_to_primary()
    
    def _failover_to_backup(self):
        """Switch from primary to backup pump"""
        logger.warning("FAILOVER: Switching to backup pump")
        
        # Stop primary
        self.primary.stop()
        
        # Start backup
        if self.backup.start():
            self.active_pump = PumpState.BACKUP
            logger.info("Backup pump activated successfully")
        else:
            logger.error("CRITICAL: Backup pump failed to start!")
            self.active_pump = PumpState.FAILED
    
    def _failback_to_primary(self):
        """Switch from backup back to primary pump"""
        logger.info("FAILBACK: Switching to primary pump")
        
        # Stop backup
        self.backup.stop()
        
        # Start primary
        if self.primary.start():
            self.active_pump = PumpState.PRIMARY
            self.primary.error_count = 0  # Reset error count
            logger.info("Primary pump reactivated successfully")
        else:
            logger.error("Primary pump failed to restart, staying on backup")
            self.backup.start()  # Restart backup
    
    def set_frequency(self, hz):
        """Set frequency on the active pump"""
        active = self.get_active_vfd()
        if active:
            return active.set_frequency(hz)
        return False
    
    def stop(self):
        """Stop both pumps"""
        logger.info("Stopping all pumps")
        self.primary.stop()
        self.backup.stop()
    
    def get_status(self):
        """Get status of pump system"""
        active = self.get_active_vfd()
        return {
            "active_pump": self.active_pump.value,
            "primary_healthy": self.primary.is_healthy(self.max_errors),
            "backup_healthy": self.backup.is_healthy(self.max_errors),
            "primary_errors": self.primary.error_count,
            "backup_errors": self.backup.error_count,
            "active_vfd_status": active.get_status() if active else None
        }
