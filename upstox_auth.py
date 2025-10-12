"""
Upstox Authentication Module

This module handles Upstox API authentication and provides a clean interface
for connecting to Upstox services.
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import upstox_client
from upstox_client import ApiClient, Configuration
from upstox_client.api import LoginApi, UserApi, MarketHolidaysAndTimingsApi

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class UpstoxAuth:
    """Handles Upstox API authentication and basic operations"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, redirect_uri: str = None):
        """
        Initialize Upstox authentication
        
        Args:
            api_key: Upstox API key (or set UPSTOX_API_KEY env var)
            api_secret: Upstox API secret (or set UPSTOX_API_SECRET env var)
            redirect_uri: Redirect URI (or set UPSTOX_REDIRECT_URI env var, defaults to localhost:8080)
        """
        self.api_key = api_key or os.getenv('UPSTOX_API_KEY')
        self.api_secret = api_secret or os.getenv('UPSTOX_API_SECRET')
        self.redirect_uri = redirect_uri or os.getenv('UPSTOX_REDIRECT_URI', 'http://localhost:8080')
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API key and secret are required. "
                "Provide them as parameters or set UPSTOX_API_KEY and UPSTOX_API_SECRET environment variables."
            )
        
        # Initialize configuration
        self.config = Configuration()
        self.config.host = "https://api.upstox.com"
        self.api_client = ApiClient(self.config)
        
        # Authentication state
        self.access_token = None
        self.token_expires_at = None
        self.is_authenticated = False
        
    def get_auth_url(self, state: str = "upstox_auth") -> str:
        """
        Get authorization URL for OAuth flow
        
        Args:
            state: State parameter for OAuth (optional)
            
        Returns:
            Authorization URL string
        """
        try:
            # Construct the authorization URL manually since the API doesn't return it
            base_url = "https://api.upstox.com/v2/login/authorization/dialog"
            auth_url = (
                f"{base_url}?"
                f"response_type=code&"
                f"client_id={self.api_key}&"
                f"redirect_uri={self.redirect_uri}&"
                f"state={state}"
            )
            return auth_url
        except Exception as e:
            raise Exception(f"Failed to get authorization URL: {str(e)}")
    
    def set_access_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            authorization_code: Code received from authorization callback
            
        Returns:
            Token information dict
        """
        try:
            login_api = LoginApi(self.api_client)
            
            token_response = login_api.token(
                api_version='2.0',
                code=authorization_code,
                client_id=self.api_key,
                client_secret=self.api_secret,
                redirect_uri=self.redirect_uri,
                grant_type='authorization_code'
            )
            
            # Store token information
            self.access_token = token_response.access_token
            # Upstox tokens are valid until 3:30 AM next day (no specific expires_at in response)
            self.token_expires_at = "3:30 AM next trading day"
            self.config.access_token = self.access_token
            self.is_authenticated = True
            
            return {
                'access_token': self.access_token,
                'expires_at': self.token_expires_at,
                'authenticated': True,
                'user_info': {
                    'user_name': token_response.user_name,
                    'email': token_response.email,
                    'user_id': token_response.user_id,
                    'broker': token_response.broker
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to exchange authorization code: {str(e)}")
    
    def load_token_from_file(self, file_path: str = "upstox_token.json") -> bool:
        """
        Load access token from file
        
        Args:
            file_path: Path to token file
            
        Returns:
            True if token loaded successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    token_data = json.load(f)
                
                self.access_token = token_data.get('access_token')
                self.token_expires_at = token_data.get('expires_at')
                
                if self.access_token:
                    self.config.access_token = self.access_token
                    self.is_authenticated = True
                    return True
            
            return False
        except Exception:
            return False
    
    def save_token_to_file(self, file_path: str = "upstox_token.json") -> bool:
        """
        Save access token to file
        
        Args:
            file_path: Path to save token file
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            if self.access_token:
                token_data = {
                    'access_token': self.access_token,
                    'expires_at': self.token_expires_at,
                    'saved_at': datetime.now().isoformat()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(token_data, f, indent=2)
                
                return True
            return False
        except Exception:
            return False
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get user profile information
        
        Returns:
            User profile dict
        """
        if not self.is_authenticated:
            raise Exception("Not authenticated. Please set access token first.")
        
        try:
            user_api = UserApi(self.api_client)
            profile = user_api.get_profile(api_version='2.0')
            
            return {
                'user_name': profile.user_name,
                'email': profile.email,
                'user_id': profile.user_id,
                'broker': profile.broker,
                'exchanges': profile.exchanges,
                'products': profile.products,
                'user_type': profile.user_type,
                'poa': profile.poa,
                'is_active': profile.is_active
            }
        except Exception as e:
            raise Exception(f"Failed to get user profile: {str(e)}")
    
    def get_market_status(self) -> Dict[str, str]:
        """
        Get market status for all exchanges
        
        Returns:
            Market status dict with exchange names as keys
        """
        if not self.is_authenticated:
            raise Exception("Not authenticated. Please set access token first.")
        
        try:
            market_api = MarketHolidaysAndTimingsApi(self.api_client)
            status_response = market_api.get_market_status(api_version='2.0')
            
            market_status = {}
            for exchange_status in status_response:
                market_status[exchange_status.exchange] = exchange_status.market_status
            
            return market_status
        except Exception as e:
            raise Exception(f"Failed to get market status: {str(e)}")
    
    def check_connection(self) -> Dict[str, Any]:
        """
        Check if connection is working by fetching user profile
        
        Returns:
            Connection status dict
        """
        try:
            if not self.is_authenticated:
                return {
                    'connected': False,
                    'error': 'Not authenticated'
                }
            
            profile = self.get_user_profile()
            return {
                'connected': True,
                'user_name': profile['user_name'],
                'broker': profile['broker'],
                'exchanges': profile['exchanges']
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }


def create_upstox_client(api_key: str = None, api_secret: str = None, 
                        redirect_uri: str = None, token_file: str = "upstox_token.json") -> UpstoxAuth:
    """
    Convenience function to create and optionally authenticate Upstox client
    
    Args:
        api_key: Upstox API key
        api_secret: Upstox API secret  
        redirect_uri: Redirect URI
        token_file: Path to token file (will try to load existing token)
        
    Returns:
        UpstoxAuth instance
    """
    client = UpstoxAuth(api_key, api_secret, redirect_uri)
    
    # Try to load existing token
    if os.path.exists(token_file):
        client.load_token_from_file(token_file)
    
    return client


if __name__ == "__main__":
    """
    Example usage / testing
    """
    print("🔗 Upstox Authentication Module")
    print("=" * 40)
    
    try:
        # Create client (you need to set environment variables or pass credentials)
        client = create_upstox_client()
        
        if client.is_authenticated:
            print("✅ Already authenticated with saved token")
            
            # Test connection
            connection = client.check_connection()
            if connection['connected']:
                print(f"👤 Connected as: {connection['user_name']}")
                print(f"🏦 Broker: {connection['broker']}")
                
                # Get market status
                market_status = client.get_market_status()
                print("\n📊 Market Status:")
                for exchange, status in market_status.items():
                    print(f"  {exchange}: {status}")
            else:
                print(f"❌ Connection failed: {connection['error']}")
        else:
            print("🔐 Not authenticated. Starting OAuth flow...")
            
            # Get authorization URL
            auth_url = client.get_auth_url()
            print(f"\n🔗 Visit this URL to authorize:")
            print(auth_url)
            print("\nAfter authorization, you'll get a code. Use set_access_token(code) to complete authentication.")
            
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 To use this module, set environment variables:")
        print("   export UPSTOX_API_KEY='your_api_key'")
        print("   export UPSTOX_API_SECRET='your_api_secret'")
        print("   export UPSTOX_REDIRECT_URI='http://localhost:8080'  # optional")
    except Exception as e:
        print(f"❌ Error: {e}")
