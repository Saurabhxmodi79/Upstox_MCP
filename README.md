# 🚀 Upstox MCP Server

A Model Context Protocol (MCP) server for Upstox trading platform, enabling seamless integration with Claude Desktop and other MCP-compatible clients.

## 🌟 Features

- **👤 User Profile**: Get your complete Upstox account information
- **📊 Portfolio Holdings**: View your long-term investments with P&L analysis
- **📈 Trading Positions**: Monitor active and closed positions across all exchanges
- **🔒 Secure Authentication**: OAuth-based secure authentication with Upstox
- **🐳 Docker Ready**: Easy deployment with Docker containers

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Upstox Developer Account with API credentials

### 1. Get Upstox API Credentials
1. Visit [Upstox Developer Console](https://upstox.com/developer/apps)
2. Create a new app or use existing one
3. Note down your `API Key` and `API Secret`
4. Set redirect URI to `http://localhost:8080`

### 2. Clone and Setup
```bash
git clone <repository-url>
cd Upstox-MCP
./setup.sh
```

The setup script will:
- ✅ Check Docker installation
- ✅ Create configuration files
- ✅ Guide you through authentication
- ✅ Start the MCP server

### 3. Configure Claude Desktop
Add this to your Claude Desktop config file:
```json
{
  "mcpServers": {
    "upstox-mcp": {
      "command": "docker",
      "args": [
        "exec",
        "upstox-mcp-server",
        "uv",
        "run",
        "upstox_server.py"
      ]
    }
  }
}
```

**Config file location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## 🛠️ Manual Setup (Development)

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation
```bash
# Clone repository
git clone <repository-url>
cd Upstox-MCP

# Install dependencies
uv sync

# Set up environment
cp env.example .env
# Edit .env with your Upstox API credentials

# Authenticate with Upstox
uv run python authenticate.py

# Test the server
uv run python upstox_server.py
```

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "upstox-mcp": {
      "command": "uv",
      "args": [
        "run",
        "upstox_server.py"
      ],
      "cwd": "/path/to/Upstox-MCP"
    }
  }
}
```

## 📋 Available Tools

### 🔧 MCP Tools

#### Portfolio & Account Tools
1. **`get_user_profile()`**
   - Returns complete user account information
   - Shows broker details, exchanges, products available

2. **`get_holdings()`**
   - Lists all portfolio holdings
   - Shows investment value, current value, P&L
   - Provides portfolio summary with total returns

3. **`get_positions()`**
   - Shows active and closed trading positions
   - Covers all exchanges (NSE, BSE, NFO, MCX, CDS)
   - Displays unrealised vs realised P&L

#### Market Data Tools
4. **`get_stock_price(instrument_key)`**
   - Get current Last Traded Price (LTP) for any stock
   - Quick price lookup using instrument key

5. **`get_full_market_quote(instrument_key)`**
   - Detailed market data with OHLC (Open, High, Low, Close)
   - Includes volume, day change, and percentage change

#### Stock Search Tools
6. **`get_instrument_key(symbol)`**
   - Find instrument key for any stock symbol
   - Returns company name and category

7. **`search_stocks(search_term, limit)`**
   - Search stocks by symbol or company name
   - Returns matching stocks with details

## 🐳 Docker Commands

```bash
# Start the server
docker-compose up -d

# View logs
docker-compose logs -f upstox-mcp

# Stop the server
docker-compose down

# Rebuild after code changes
docker-compose build --no-cache

# Run authentication helper
docker-compose --profile auth up upstox-auth-helper
```

## 🔐 Authentication

The authentication process uses Upstox OAuth2 flow:

1. **Get Authorization URL**: The server generates a secure authorization URL
2. **User Authorization**: You visit the URL and approve the application
3. **Token Exchange**: Authorization code is exchanged for access token
4. **Token Storage**: Access token is securely stored for future use

**Token Management:**
- Tokens expire at 3:30 AM IST daily
- Re-run authentication when needed: `uv run python authenticate.py`
- Tokens are automatically excluded from git commits

## 📁 Project Structure

```
Upstox-MCP/
├── upstox_server.py           # Main MCP server with all trading tools
├── upstox_auth.py             # Authentication module
├── authenticate.py            # Interactive authentication script
├── config.py                  # Configuration loader
├── categorized_stocks.json    # Curated stock database (2,484 stocks)
├── all_stocks_detailed.json   # Complete stock master data
├── Dockerfile                 # Docker container definition
├── docker-compose.yml         # Docker orchestration
├── setup.sh                   # Automated setup script
├── pyproject.toml             # Python project configuration
└── README.md                  # This file
```

## 🛡️ Security

- ✅ OAuth2 secure authentication
- ✅ Tokens stored locally, never in code
- ✅ Sensitive files excluded from git
- ✅ No hardcoded credentials
- ✅ Minimal required permissions

## 🐛 Troubleshooting

### Common Issues

**1. Authentication Failed**
```bash
# Check your API credentials
cat .env

# Re-run authentication
uv run python authenticate.py
```

**2. Server Not Starting**
```bash
# Check logs
docker-compose logs upstox-mcp

# Restart container
docker-compose restart upstox-mcp
```

**3. Claude Desktop Not Connecting**
- Ensure server is running: `docker ps`
- Check Claude Desktop config path
- Restart Claude Desktop after config changes

**4. Token Expired**
```bash
# Re-authenticate (tokens expire daily at 3:30 AM IST)
docker-compose --profile auth up upstox-auth-helper
```

## 📊 Example Usage

Once integrated with Claude Desktop, you can:

```
"Show me my Upstox portfolio"
→ Calls get_holdings() tool

"What are my current trading positions?"
→ Calls get_positions() tool

"Get my account details"
→ Calls get_user_profile() tool

"What's the current price of Infosys?"
→ Calls get_instrument_key("INFY") then get_stock_price()

"Search for Reliance stocks"
→ Calls search_stocks("Reliance")

"Get full market quote for TCS"
→ Calls get_instrument_key("TCS") then get_full_market_quote()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with your Upstox account
5. Submit a pull request

## ⚠️ Disclaimer

This is an unofficial integration with Upstox. Use at your own risk. Always verify trading data independently. Not responsible for any trading losses.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎯 Happy Trading with Upstox MCP Server!**
