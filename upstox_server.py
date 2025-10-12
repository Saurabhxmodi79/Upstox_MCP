"""
Upstox MCP Server with profile functionality
"""

from mcp.server.fastmcp import FastMCP
import upstox_client
from upstox_client.rest import ApiException
from config import configuration, api_version

# Create MCP server
mcp = FastMCP("Upstox Profile Server")

@mcp.tool()
def get_user_profile() -> str:
    """Get Upstox user profile information"""
    try:
        api_instance = upstox_client.UserApi(upstox_client.ApiClient(configuration))
        response = api_instance.get_profile(api_version)
        
        # Profile data is nested under 'data' attribute and accessed with dot notation
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
        
    except ApiException as e:
        return f"❌ Error getting profile: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


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
   Avg Price: ₹{holding.average_price:.2f}
   Last Price: ₹{holding.last_price:.2f}
   Investment: ₹{investment_value:,.2f}
   Current Value: ₹{current_value:,.2f}
   P&L: ₹{holding.pnl:.2f}
   Day Change: {holding.day_change_percentage:.2f}%
   Exchange: {holding.exchange}
   
"""
        
        total_pnl = total_current_value - total_investment
        pnl_percentage = (total_pnl / total_investment * 100) if total_investment > 0 else 0
        
        result += f"""💰 Portfolio Summary:
Total Investment: ₹{total_investment:,.2f}
Current Value: ₹{total_current_value:,.2f}
Total P&L: ₹{total_pnl:,.2f} ({pnl_percentage:.2f}%)"""
        
        return result
        
    except ApiException as e:
        return f"❌ Error getting holdings: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


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
   Buy Price: ₹{position.buy_price if position.buy_price else 0:.2f}
   Sell Price: ₹{position.sell_price if position.sell_price else 0:.2f}
   Last Price: ₹{position.last_price:.2f}
   Value: ₹{position.value:,.2f}
   P&L: ₹{position.pnl:.2f}
   Unrealised: ₹{position.unrealised:.2f}
   Realised: ₹{position.realised:.2f}
   Product: {position.product}
   
"""
        
        result += f"""💹 Positions Summary:
Total P&L: ₹{total_pnl:,.2f}
Total Unrealised: ₹{total_unrealised:,.2f}
Total Realised: ₹{total_realised:,.2f}"""
        
        return result
        
    except ApiException as e:
        return f"❌ Error getting positions: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
