import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class YNABConfig:
    api_key: str
    api_url: str = "https://api.ynab.com/v1"
    
    @classmethod
    def load(cls, config_path: Path = None) -> 'YNABConfig':
        """Load YNAB configuration from file or environment variables."""
        # First try environment variables
        api_key = os.environ.get('YNAB_API_KEY')
        
        # If not in env vars, try config file
        if not api_key and config_path and config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                api_key = config.get('ynab', {}).get('api_key')
        
        if not api_key:
            raise ValueError("YNAB API key not found in environment or config file")
            
        return cls(api_key=api_key)
