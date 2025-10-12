import upstox_client
import json

# Load access token from saved file
with open('upstox_token.json', 'r') as f:
    token_data = json.load(f)
    access_token = token_data['access_token']

# Create global configuration
configuration = upstox_client.Configuration()
configuration.access_token = access_token
api_version = '2.0'
