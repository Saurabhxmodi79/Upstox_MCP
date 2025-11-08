"""
Upstox MCP Server
Provides trading and market data tools via Model Context Protocol
"""

from mcp.server.fastmcp import FastMCP
import upstox_client
from upstox_client.rest import ApiException
from config import configuration, api_version
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Create MCP server
mcp = FastMCP("Upstox Trading Server")

# ============================================================================
# Helper Functions
# ============================================================================

def handle_api_error(e: Exception, context: str = "API operation") -> str:
    """
    Centralized error handling for API calls
    
    Args:
        e: Exception object
        context: Context description for the error
    
    Returns:
        Formatted error message
    """
    if isinstance(e, ApiException):
        return f"❌ API Error during {context}: {e.status} - {e.reason}"
    return f"❌ Error during {context}: {str(e)}"


def load_stock_data() -> Optional[Dict[str, Any]]:
    """
    Load categorized stock data from JSON file
    
    Returns:
        Dictionary with categorized stocks or None if failed
    """
    try:
        json_path = Path(__file__).parent / "categorized_stocks.json"
        if not json_path.exists():
            return None
        
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def format_currency(amount: float) -> str:
    """Format currency with Indian numbering system"""
    return f"₹{amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format percentage with sign"""
    return f"{value:+.2f}%"

# ============================================================================
# User Profile & Portfolio Tools
# ============================================================================

@mcp.tool()
def get_user_profile() -> str:
    """Get Upstox user profile information"""
    try:
        api_instance = upstox_client.UserApi(upstox_client.ApiClient(configuration))
        response = api_instance.get_profile(api_version)
        profile = response.data
        
        return f"""👤 User Profile:
Name: {profile.user_name}
Email: {profile.email}
User ID: {profile.user_id}
Broker: {profile.broker}
Exchanges: {', '.join(profile.exchanges)}
Products: {', '.join(profile.products)}
Order Types: {', '.join(profile.order_types)}
User Type: {profile.user_type}
POA Status: {profile.poa}
Active: {profile.is_active}"""
        
    except Exception as e:
        return handle_api_error(e, "fetching user profile")


@mcp.tool()
def get_holdings() -> str:
    """Get Upstox portfolio holdings"""
    try:
        api_instance = upstox_client.PortfolioApi(upstox_client.ApiClient(configuration))
        response = api_instance.get_holdings(api_version)
        holdings = response.data
        
        if not holdings:
            return "📊 No holdings found in your portfolio."
        
        result = f"📊 Portfolio Holdings ({len(holdings)} stocks):\n\n"
        total_investment = 0
        total_current_value = 0
        
        for holding in holdings:
            investment_value = holding.average_price * holding.quantity
            current_value = holding.last_price * holding.quantity
            total_investment += investment_value
            total_current_value += current_value
            
            result += f"""🏢 {holding.company_name} ({holding.trading_symbol})
   Quantity: {holding.quantity}
   Avg Price: {format_currency(holding.average_price)}
   Last Price: {format_currency(holding.last_price)}
   Investment: {format_currency(investment_value)}
   Current Value: {format_currency(current_value)}
   P&L: {format_currency(holding.pnl)}
   Day Change: {format_percentage(holding.day_change_percentage)}
   Exchange: {holding.exchange}
   
"""
        
        total_pnl = total_current_value - total_investment
        pnl_percentage = (total_pnl / total_investment * 100) if total_investment > 0 else 0
        
        result += f"""💰 Portfolio Summary:
Total Investment: {format_currency(total_investment)}
Current Value: {format_currency(total_current_value)}
Total P&L: {format_currency(total_pnl)} ({format_percentage(pnl_percentage)})"""
        
        return result
        
    except Exception as e:
        return handle_api_error(e, "fetching holdings")


@mcp.tool()
def get_positions() -> str:
    """Get Upstox trading positions"""
    try:
        api_instance = upstox_client.PortfolioApi(upstox_client.ApiClient(configuration))
        response = api_instance.get_positions(api_version)
        positions = response.data
        
        if not positions:
            return "📈 No open positions found."
        
        result = f"📈 Trading Positions ({len(positions)} positions):\n\n"
        total_pnl = 0
        total_unrealised = 0
        total_realised = 0
        
        for position in positions:
            total_pnl += position.pnl
            total_unrealised += position.unrealised
            total_realised += position.realised
            
            status = "✅ CLOSED" if position.quantity == 0 else "🔄 OPEN"
            
            result += f"""📊 {position.trading_symbol} ({position.exchange}) {status}
   Quantity: {position.quantity}
   Buy Price: {format_currency(position.buy_price if position.buy_price else 0)}
   Sell Price: {format_currency(position.sell_price if position.sell_price else 0)}
   Last Price: {format_currency(position.last_price)}
   Value: {format_currency(position.value)}
   P&L: {format_currency(position.pnl)}
   Unrealised: {format_currency(position.unrealised)}
   Realised: {format_currency(position.realised)}
   Product: {position.product}
   
"""
        
        result += f"""💹 Positions Summary:
Total P&L: {format_currency(total_pnl)}
Total Unrealised: {format_currency(total_unrealised)}
Total Realised: {format_currency(total_realised)}"""
        
        return result
        
    except Exception as e:
        return handle_api_error(e, "fetching positions")

# ============================================================================
# Market Data Tools
# ============================================================================

@mcp.tool()
def get_stock_price(instrument_key: str) -> str:
    """Get the current stock price for a given instrument key
    
    Args:
        instrument_key: The instrument key (e.g., 'NSE_EQ|INE009A01021')
    
    Returns:
        Current stock price information
    """
    try:
        market_api = upstox_client.MarketQuoteApi(upstox_client.ApiClient(configuration))
        response = market_api.ltp(symbol=instrument_key, api_version=api_version)
        
        if response.status == 'success' and response.data:
            for key, price_data in response.data.items():
                return f"""📈 Current Stock Price:

Instrument Key: {instrument_key}
Last Price: {format_currency(price_data.last_price)}
Status: Active ✅"""
        
        return f"❌ No price data available for instrument key: {instrument_key}"
        
    except Exception as e:
        return handle_api_error(e, "fetching stock price")


@mcp.tool()
def get_full_market_quote(instrument_key: str) -> str:
    """Get detailed market quote including OHLC data for a given instrument key
    
    Args:
        instrument_key: The instrument key (e.g., 'NSE_EQ|INE009A01021')
    
    Returns:
        Detailed market information including open, high, low, close, volume
    """
    try:
        market_api = upstox_client.MarketQuoteApi(upstox_client.ApiClient(configuration))
        response = market_api.get_full_market_quote(
            symbol=instrument_key,
            api_version=api_version
        )
        
        if response.status == 'success' and response.data:
            for key, quote_data in response.data.items():
                ohlc = quote_data.ohlc
                
                # Calculate day change
                day_change = ohlc.close - ohlc.open if ohlc.close and ohlc.open else 0
                day_change_pct = (day_change / ohlc.open * 100) if ohlc.open and ohlc.open != 0 else 0
                
                result = f"""📊 Full Market Quote:

Instrument Key: {instrument_key}

💰 Price Information:
   Last Price: {format_currency(quote_data.last_price)}
   Open: {format_currency(ohlc.open)}
   High: {format_currency(ohlc.high)}
   Low: {format_currency(ohlc.low)}
   Close (Prev): {format_currency(ohlc.close)}

📈 Day Performance:
   Change: {format_currency(day_change)} ({format_percentage(day_change_pct)})

📊 Volume Information:
   Volume: {quote_data.volume:,}
   
⏰ Last Update: {quote_data.last_trade_time if hasattr(quote_data, 'last_trade_time') else 'N/A'}

Status: Active ✅"""
                
                return result
        
        return f"❌ No market data available for instrument key: {instrument_key}"
        
    except Exception as e:
        return handle_api_error(e, "fetching full market quote")

# ============================================================================
# Stock Search Tools
# ============================================================================

@mcp.tool()
def get_instrument_key(symbol: str) -> str:
    """Get the instrument key for a stock symbol
    
    Args:
        symbol: The stock symbol (e.g., 'RELIANCE', 'TCS', 'INFY')
    
    Returns:
        The instrument key and company name for the stock
    """
    try:
        categorized_stocks = load_stock_data()
        
        if not categorized_stocks:
            return "❌ Error: Stock data not available"
        
        # Search through all categories for the symbol
        symbol_upper = symbol.upper()
        found_stocks = []
        
        for category, stocks in categorized_stocks.items():
            for stock in stocks:
                if stock['symbol'].upper() == symbol_upper:
                    found_stocks.append({
                        'symbol': stock['symbol'],
                        'instrument_key': stock['instrument_key'],
                        'name': stock.get('name', 'N/A'),
                        'category': category
                    })
        
        if not found_stocks:
            return f"❌ Stock symbol '{symbol}' not found in the database"
        
        # Single match
        if len(found_stocks) == 1:
            stock = found_stocks[0]
            return f"""🔑 Instrument Key Found:

Symbol: {stock['symbol']}
Name: {stock['name']}
Instrument Key: {stock['instrument_key']}
Category: {stock['category']}"""
        
        # Multiple matches
        result = f"🔑 Found {len(found_stocks)} matches for '{symbol}':\n\n"
        for idx, stock in enumerate(found_stocks, 1):
            result += f"""{idx}. Symbol: {stock['symbol']}
   Name: {stock['name']}
   Instrument Key: {stock['instrument_key']}
   Category: {stock['category']}

"""
        return result
            
    except Exception as e:
        return handle_api_error(e, "searching for instrument")


@mcp.tool()
def search_stocks(search_term: str, limit: int = 10) -> str:
    """Search for stocks by symbol or name
    
    Args:
        search_term: Search query (symbol or company name)
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of matching stocks with their details
    """
    try:
        categorized_stocks = load_stock_data()
        
        if not categorized_stocks:
            return "❌ Error: Stock data not available"
        
        search_lower = search_term.lower()
        matches = []
        
        # Search through all categories
        for category, stocks in categorized_stocks.items():
            for stock in stocks:
                symbol_match = search_lower in stock['symbol'].lower()
                name_match = search_lower in stock.get('name', '').lower()
                
                if symbol_match or name_match:
                    matches.append({
                        'symbol': stock['symbol'],
                        'name': stock.get('name', 'N/A'),
                        'instrument_key': stock['instrument_key'],
                        'category': category
                    })
                    
                    if len(matches) >= limit:
                        break
            
            if len(matches) >= limit:
                break
        
        if not matches:
            return f"❌ No stocks found matching '{search_term}'"
        
        result = f"🔍 Search Results for '{search_term}' ({len(matches)} matches):\n\n"
        
        for idx, stock in enumerate(matches, 1):
            result += f"""{idx}. {stock['symbol']} - {stock['name']}
   Instrument Key: {stock['instrument_key']}
   Category: {stock['category']}

"""
        
        return result
        
    except Exception as e:
        return handle_api_error(e, "searching stocks")


if __name__ == "__main__":
    mcp.run(transport="stdio")
