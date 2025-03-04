"""Configuration management for JARVIS."""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .utils.exceptions import ConfigError

class Config:
    """Configuration manager for JARVIS."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.settings = self._load_yaml("settings.yaml")
        self.responses = self._load_yaml("responses.yaml")
        
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file.
        
        Args:
            filename: Name of the YAML file to load
            
        Returns:
            Dictionary containing the configuration
            
        Raises:
            ConfigError: If the file cannot be loaded
        """
        try:
            with open(self.config_dir / filename, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ConfigError(f"Failed to load {filename}: {str(e)}")
    
    def get_setting(self, *keys: str, default: Any = None) -> Any:
        """Get a setting value using dot notation.
        
        Args:
            *keys: The key path to the setting
            default: Default value if setting not found
            
        Returns:
            The setting value or default
        """
        current = self.settings
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key, default)
        return current
    
    def get_response(self, *keys: str, default: Any = None) -> Any:
        """Get a response template using dot notation.
        
        Args:
            *keys: The key path to the response
            default: Default value if response not found
            
        Returns:
            The response template or default
        """
        current = self.responses
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key, default)
        return current 