"""
Upstox Configuration Module
Handles configuration and authentication setup
"""

import upstox_client
import json
import os
from pathlib import Path

# API version
api_version = '2.0'

def get_configuration():
    """
    Load and return Upstox configuration with access token
    
    Returns:
        upstox_client.Configuration: Configured client
    
    Raises:
        FileNotFoundError: If token file doesn't exist
        ValueError: If token is invalid or missing
    """
    token_file = Path('upstox_token.json')
    
    if not token_file.exists():
        raise FileNotFoundError(
            "Token file not found. Please run authentication first:\n"
            "  uv run python authenticate.py"
        )
    
    try:
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data.get('access_token')
        if not access_token:
            raise ValueError("Access token missing in token file")
        
        # Create and configure client
        configuration = upstox_client.Configuration()
        configuration.access_token = access_token
        
        return configuration
        
    except json.JSONDecodeError:
        raise ValueError("Invalid token file format")
    except Exception as e:
        raise ValueError(f"Error loading configuration: {str(e)}")

# Global configuration instance
try:
    configuration = get_configuration()
except Exception as e:
    # In case of errors, create empty config
    # The server will handle authentication errors gracefully
    configuration = upstox_client.Configuration()
    print(f"⚠️  Warning: {str(e)}")
