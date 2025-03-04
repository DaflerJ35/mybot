"""System monitoring utilities for JARVIS."""
import os
import psutil
from typing import Dict, List, Optional, Tuple

from ..config import Config
from .exceptions import MonitoringError

class SystemMonitor:
    """Monitor system resources and processes."""
    
    def __init__(self, config: Config):
        """Initialize system monitor.
        
        Args:
            config: JARVIS configuration instance
        """
        self.config = config
        self.critical_paths = config.get_setting('system', 'critical_paths', default=[])
        self.cpu_threshold = config.get_setting('system', 'rogue_cpu_threshold', default=80)
        self.mem_threshold = config.get_setting('system', 'rogue_mem_threshold', default=80)
        
    def get_system_status(self) -> Dict[str, float]:
        """Get current system resource usage.
        
        Returns:
            Dictionary with CPU and memory usage percentages
        """
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except Exception as e:
            raise MonitoringError(f"Failed to get system status: {str(e)}")
    
    def check_critical_processes(self) -> List[Dict[str, str]]:
        """Check status of critical system processes.
        
        Returns:
            List of dictionaries containing process information
        """
        critical_processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                if proc.info['exe'] and proc.info['exe'] in self.critical_paths:
                    critical_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'status': 'running'
                    })
            return critical_processes
        except Exception as e:
            raise MonitoringError(f"Failed to check critical processes: {str(e)}")
    
    def find_resource_hogs(self) -> List[Dict[str, Any]]:
        """Find processes using excessive resources.
        
        Returns:
            List of dictionaries containing resource-heavy processes
        """
        try:
            hogs = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if (proc.info['cpu_percent'] > self.cpu_threshold or 
                        proc.info['memory_percent'] > self.mem_threshold):
                        hogs.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return hogs
        except Exception as e:
            raise MonitoringError(f"Failed to find resource hogs: {str(e)}")
            
    def get_disk_usage(self, path: str = '/') -> Dict[str, float]:
        """Get disk usage statistics.
        
        Args:
            path: Path to check disk usage for
            
        Returns:
            Dictionary with disk usage information
        """
        try:
            usage = psutil.disk_usage(path)
            return {
                'total': usage.total / (1024 ** 3),  # Convert to GB
                'used': usage.used / (1024 ** 3),
                'free': usage.free / (1024 ** 3),
                'percent': usage.percent
            }
        except Exception as e:
            raise MonitoringError(f"Failed to get disk usage: {str(e)}") 