#!/usr/bin/env python3
"""
Upstox Authentication Script
Simple and clean OAuth flow for Upstox API
"""

from upstox_auth import create_upstox_client
import sys

def print_header():
    """Print application header"""
    print("\n" + "=" * 60)
    print("🔐 Upstox Authentication")
    print("=" * 60 + "\n")

def print_step(number: int, message: str):
    """Print step message"""
    print(f"📝 Step {number}: {message}")

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️  {message}")

def main():
    """Main authentication flow"""
    print_header()
    
    try:
        # Create client
        client = create_upstox_client()
        
        # Check if already authenticated
        if client.is_authenticated:
            print_success("Already authenticated with saved token")
            
            # Test connection
            connection = client.check_connection()
            if connection['connected']:
                print(f"\n👤 User: {connection['user_name']}")
                print(f"🏦 Broker: {connection['broker']}")
                print(f"📊 Exchanges: {', '.join(connection['exchanges'])}")
                
                # Ask if user wants to re-authenticate
                print("\n" + "-" * 60)
                choice = input("Do you want to re-authenticate? (y/n): ").strip().lower()
                
                if choice != 'y':
                    print("\n✨ Using existing authentication")
                    return
            else:
                print_warning("Saved token is invalid or expired")
        
        # Start fresh authentication
        print("\n" + "=" * 60)
        print("Starting OAuth Authentication Flow")
        print("=" * 60 + "\n")
        
        # Get authorization URL
        auth_url = client.get_auth_url()
        
        print_step(1, "Visit this URL to authorize:")
        print(f"\n{auth_url}\n")
        
        print_step(2, "After authorization, you'll be redirected to:")
        print("http://localhost:8080/?code=XXXXX&state=upstox_auth\n")
        
        print_step(3, "Copy the authorization code from the URL")
        print("(The code is the value after 'code=' and before '&state')\n")
        
        # Get authorization code
        print("-" * 60)
        code = input("Enter authorization code: ").strip()
        
        if not code:
            print_error("No code provided. Exiting.")
            sys.exit(1)
        
        # Clean up code if user pasted full URL
        if 'code=' in code:
            code = code.split('code=')[1].split('&')[0]
            print(f"🔧 Extracted code: {code[:10]}...{code[-10:]}")
        
        print("\n🔄 Exchanging code for access token...")
        
        # Exchange code for token
        token_info = client.set_access_token(code)
        
        print_success("Successfully authenticated!")
        
        # Display user info
        print(f"\n👤 User: {token_info['user_info']['user_name']}")
        print(f"📧 Email: {token_info['user_info']['email']}")
        print(f"🏦 Broker: {token_info['user_info']['broker']}")
        print(f"🕒 Token expires at: {token_info.get('expires_at', 'Unknown')}")
        
        # Save token
        if client.save_token_to_file():
            print_success("Token saved to upstox_token.json")
        else:
            print_warning("Could not save token to file")
        
        print("\n" + "=" * 60)
        print("🎉 Authentication completed successfully!")
        print("=" * 60)
        print("\nYou can now use the Upstox MCP server:")
        print("  uv run python upstox_server.py")
        print()
        
    except ValueError as e:
        print_error(f"Configuration error: {e}")
        print("\n💡 Make sure your .env file contains:")
        print("   UPSTOX_API_KEY=your_api_key")
        print("   UPSTOX_API_SECRET=your_api_secret")
        print("   UPSTOX_REDIRECT_URI=http://localhost:8080")
        sys.exit(1)
        
    except Exception as e:
        print_error(f"Authentication failed: {e}")
        
        if "Invalid Auth code" in str(e) or "401" in str(e):
            print("\n🔧 Troubleshooting tips:")
            print("  1. Get a fresh authorization code (they expire quickly)")
            print("  2. Verify redirect URI matches your Upstox app settings")
            print("  3. Copy only the code parameter, no extra characters")
            print("  4. Complete the process within 5 minutes")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
