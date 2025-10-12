#!/usr/bin/env python3
"""
Upstox Authentication Debugger

This script helps debug OAuth authentication issues.
"""

from upstox_auth import create_upstox_client
import os

def main():
    print("🔍 Upstox Authentication Debugger")
    print("=" * 40)
    
    try:
        # Create client and show configuration
        client = create_upstox_client()
        
        print("📋 Current Configuration:")
        print(f"  API Key: {client.api_key[:6]}...{client.api_key[-4:]}")
        print(f"  API Secret: {client.api_secret[:6]}...{client.api_secret[-4:]}")
        print(f"  Redirect URI: {client.redirect_uri}")
        print()
        
        # Generate fresh auth URL
        auth_url = client.get_auth_url()
        print("🔗 Fresh Authorization URL:")
        print(auth_url)
        print()
        
        print("🚨 IMPORTANT NOTES:")
        print("1. Use this FRESH URL (don't reuse old ones)")
        print("2. Complete authorization within 5 minutes")
        print("3. Copy ONLY the code parameter (no spaces/extra chars)")
        print("4. Each code can only be used ONCE")
        print()
        
        print("📝 After visiting the URL above:")
        print("1. You'll be redirected to: http://localhost:8080/?code=XXXXX&state=upstox_auth")
        print("2. Copy ONLY the code part (between 'code=' and '&state')")
        print("3. Paste it below")
        print()
        
        # Get code with validation
        while True:
            code = input("Enter authorization code: ").strip()
            
            if not code:
                print("❌ No code entered. Please try again.")
                continue
                
            if len(code) < 10:
                print("⚠️  Code seems too short. Make sure you copied the full code.")
                retry = input("Continue anyway? (y/n): ").lower()
                if retry != 'y':
                    continue
            
            if '&' in code or '?' in code:
                print("⚠️  Code contains URL characters. Make sure to copy ONLY the code part.")
                # Try to extract code automatically
                if 'code=' in code:
                    extracted = code.split('code=')[1].split('&')[0]
                    print(f"🔧 Extracted code: {extracted}")
                    use_extracted = input("Use extracted code? (y/n): ").lower()
                    if use_extracted == 'y':
                        code = extracted
                        break
                continue
            
            break
        
        print(f"\n🔄 Using code: {code[:10]}...{code[-10:]}")
        print("💭 Attempting token exchange...")
        
        # Try token exchange
        token_info = client.set_access_token(code)
        
        print("✅ SUCCESS! Token obtained.")
        print(f"👤 User: {token_info['user_info']['user_name']}")
        print(f"📧 Email: {token_info['user_info']['email']}")
        
        # Save token
        if client.save_token_to_file():
            print("💾 Token saved to upstox_token.json")
        
        print("\n🎉 Authentication completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
        if "Invalid Auth code" in str(e):
            print("\n🔧 Troubleshooting tips:")
            print("1. Get a fresh authorization code (old ones expire quickly)")
            print("2. Make sure your redirect URI in Upstox app settings matches exactly")
            print("3. Copy only the code parameter, no extra characters")
            print("4. Complete the process quickly (within 5 minutes)")
            
        elif "401" in str(e) or "Unauthorized" in str(e):
            print("\n🔧 Check your credentials:")
            print("1. Verify API Key and Secret in your .env file")
            print("2. Make sure your Upstox app is approved/active")
            print("3. Check if redirect URI matches your app settings")

if __name__ == "__main__":
    main()
