"""
Configuration Manager - Utility for handling configuration files

Manages loading and parsing of YAML configuration files with environment variable substitution.
"""

import os
import yaml
from typing import Dict, Any
from loguru import logger


class ConfigManager:
    """Manages configuration loading and parsing."""
    
    def __init__(self, config_path: str):
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = None
        
    def get_config(self) -> Dict[str, Any]:
        """Get the loaded configuration.
        
        Returns:
            Dictionary containing the configuration
        """
        if self.config is None:
            self.load_config()
        return self.config
    
    def load_config(self):
        """Load and parse the configuration file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace environment variables
            content = self._replace_env_vars(content)
            
            # Parse YAML
            self.config = yaml.safe_load(content)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def _replace_env_vars(self, content: str) -> str:
        """Replace environment variable placeholders in configuration content.
        
        Args:
            content: Configuration file content
            
        Returns:
            Content with environment variables replaced
        """
        # Find all ${VAR_NAME} patterns
        import re
        pattern = r'\$\{([^}]+)\}'
        
        def replace_var(match):
            var_name = match.group(1)
            value = os.getenv(var_name)
            if value is None:
                logger.warning(f"Environment variable {var_name} not found")
                return match.group(0)  # Keep original if not found
            return value
        
        return re.sub(pattern, replace_var, content)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        config = self.get_config()
        
        # Support dot notation for nested keys
        keys = key.split('.')
        value = config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        if self.config is None:
            self.load_config()
        
        # Support dot notation for nested keys
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        logger.info(f"Configuration updated: {key} = {value}")
    
    def save_config(self):
        """Save the current configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def reload(self):
        """Reload the configuration from file."""
        self.config = None
        self.load_config()
    
    def validate(self) -> bool:
        """Validate the configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            config = self.get_config()
            
            # Check required fields
            required_fields = [
                'discord.token',
                'discord.guild_id',
                'cpx_research.username',
                'cpx_research.password'
            ]
            
            for field in required_fields:
                if not self.get(field):
                    logger.error(f"Required configuration field missing: {field}")
                    return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False 