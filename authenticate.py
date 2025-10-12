#!/usr/bin/env python3
"""
Manual Upstox Authentication

Simple script to manually complete Upstox OAuth flow.
Run this script, visit the URL, and enter the authorization code.
"""

from upstox_auth import create_upstox_client

def main():
    print("🔐 Upstox Manual Authentication")
    print("=" * 40)
    
    try:
        # Create client
        client = create_upstox_client()
        print("✅ Upstox client initialized")
        
        # Show authorization URL
        auth_url = client.get_auth_url()
        print(f"\n🔗 Step 1: Visit this URL to authorize:")
        print(auth_url)
        print("\n📋 Step 2: After authorization, you'll be redirected to:")
        print("http://localhost:8080/?code=XXXXX&state=upstox_auth")
        
        # Get authorization code from user
        print("\n📝 Step 3: Copy the code from the callback URL")
        code = input("Enter your authorization code: ").strip()
        
        if not code:
            print("❌ No code provided. Exiting.")
            return
        
        print("\n🔄 Exchanging code for access token...")
        
        # Exchange code for token
        token_info = client.set_access_token(code)
        print("✅ Successfully authenticated!")
        print(f"🕒 Token expires at: {token_info.get('expires_at', 'Unknown')}")
        
        # Save token to file
        if client.save_token_to_file():
            print("💾 Token saved to upstox_token.json")
        else:
            print("⚠️  Could not save token to file")
        
        # Test connection
        print("\n🧪 Testing connection...")
        profile = client.get_user_profile()
        print(f"👤 User: {profile['user_name']}")
        print(f"📧 Email: {profile['email']}")
        print(f"🏦 Broker: {profile['broker']}")
        print(f"📊 Exchanges: {', '.join(profile['exchanges'])}")
        
        # Get market status
        print("\n📈 Market Status:")
        try:
            market_status = client.get_market_status()
            for exchange, status in market_status.items():
                print(f"  {exchange}: {status}")
        except Exception as e:
            print(f"  ⚠️  Could not fetch market status: {e}")
        
        print("\n🎉 Authentication completed successfully!")
        print("You can now use the Upstox API with this authenticated client.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        if "API key and secret are required" in str(e):
            print("\n💡 Make sure your .env file contains:")
            print("   UPSTOX_API_KEY=your_api_key")
            print("   UPSTOX_API_SECRET=your_api_secret")
            print("   UPSTOX_REDIRECT_URI=http://localhost:8080")

if __name__ == "__main__":
    main()
