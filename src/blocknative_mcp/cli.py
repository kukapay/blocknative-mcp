import os
from typing import Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.prompts import base

# Configuration
BLOCKNATIVE_API_KEY = os.getenv("BLOCKNATIVE_API_KEY")  # Optional for low-frequency access
BLOCKNATIVE_GAS_API_URL = "https://api.blocknative.com/gasprices/blockprices"
BLOCKNATIVE_CHAINS_API_URL = "https://api.blocknative.com/chains"

# Initialize MCP server
mcp = FastMCP(
    name="Blocknative Gas Server",
    dependencies=["httpx"]
)

# Helper function to fetch gas prices from Blocknative
async def fetch_gas_prices(chain_id: int = 1) -> Dict:
    """Fetch gas price predictions from Blocknative API for a given chain."""
    try:
        headers = {"Authorization": BLOCKNATIVE_API_KEY} if BLOCKNATIVE_API_KEY else {}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                BLOCKNATIVE_GAS_API_URL,
                headers=headers,
                params={"chainid": chain_id}
            )
            response.raise_for_status()
            data = response.json()
        
        # Extract relevant fields from the response
        block_prices = data.get("blockPrices", [])
        if not block_prices:
            return {"error": "No block prices found in API response"}
        
        # Use the first block's data
        first_block = block_prices[0]
        return {
            "baseFeePerGas": first_block.get("baseFeePerGas", 0),
            "estimatedPrices": first_block.get("estimatedPrices", []),
            "unit": data.get("unit", "gwei"),
            "system": data.get("system", "unknown"),
            "network": data.get("network", "unknown")
        }
    except httpx.HTTPError as e:
        return {"error": f"Failed to fetch gas prices for chain ID {chain_id}: {str(e)}"}

# Helper function to fetch supported chains from Blocknative
async def fetch_supported_chains() -> Dict:
    """Fetch the list of supported chains from Blocknative Chains API."""
    try:
        headers = {"Authorization": BLOCKNATIVE_API_KEY} if BLOCKNATIVE_API_KEY else {}
        async with httpx.AsyncClient() as client:
            response = await client.get(BLOCKNATIVE_CHAINS_API_URL, headers=headers)
            response.raise_for_status()
            data = response.json()
        return {"chains": data, "error": None}
    except httpx.HTTPError as e:
        return {"chains": [], "error": f"Failed to fetch supported chains: {str(e)}"}

# Tools
@mcp.tool()
async def predict_gas_price(chain_id: int = 1, ctx: Optional[Context] = None) -> str:
    """
    Predict gas prices for a specified chain, including base fee and detailed prediction data in a Markdown table.

    Parameters:
    - chain_id (int): The ID of the blockchain network (e.g., 1 for Ethereum Mainnet). Default: 1.
    - ctx (Optional[Context]): The MCP context object. Default: None.
    """
    data = await fetch_gas_prices(chain_id)
    if "error" in data:
        return data["error"]
    
    # Format base fee and metadata
    base_fee = data["baseFeePerGas"]
    output = f"Gas Price Predictions for Chain ID {chain_id} ({data['system']}/{data['network']}):\n"
    output += f"- Base Fee Per Gas: {base_fee} Gwei\n\n"
    
    # Format predictions as a Markdown table
    predictions = data["estimatedPrices"]
    if not predictions:
        output += "No prediction data available."
    else:
        output += "| Confidence | Price (Gwei) | Max Priority Fee (Gwei) | Max Fee (Gwei) |\n"
        output += "|------------|--------------|-------------------------|----------------|\n"
        for price in predictions:
            confidence = price.get("confidence", 0)
            price_value = price.get("price", 0)
            max_priority_fee = price.get("maxPriorityFeePerGas", 0)
            max_fee = price.get("maxFeePerGas", 0)
            output += (
                f"| {confidence}% | {price_value} | {max_priority_fee} | {max_fee} |\n"
            )
    
    return output

@mcp.tool()
async def estimate_gas_cost(gas_limit: int, confidence: int = 99, chain_id: int = 1, ctx: Optional[Context] = None) -> str:
    """
    Estimate gas cost for a transaction based on gas limit, confidence level, and chain.

    Parameters:
    - gas_limit (int): The gas limit for the transaction (e.g., 21000 for a simple transfer).
    - confidence (int): The confidence level for gas price prediction (0-100).
    - chain_id (int): The ID of the blockchain network (e.g., 1 for Ethereum Mainnet). Default: 1.
    - ctx (Optional[Context]): The MCP context object. Default: None.
    """
    if not (0 <= confidence <= 100):
        return "Error: Confidence must be between 0 and 100"
    if gas_limit <= 0:
        return "Error: Gas limit must be positive"
    
    data = await fetch_gas_prices(chain_id)
    if "error" in data:
        return data["error"]
    
    # Find the closest confidence level
    predictions = data["estimatedPrices"]
    closest_prediction = min(
        predictions,
        key=lambda p: abs(p.get("confidence", 0) - confidence),
        default={}
    )
    
    if not closest_prediction:
        return "Error: No matching gas price prediction found"
    
    max_fee = closest_prediction.get("maxFeePerGas", 0)
    total_cost_gwei = max_fee * gas_limit
    total_cost_eth = total_cost_gwei / 1e9  # Convert Gwei to ETH
    
    return (
        f"Estimated Gas Cost (Confidence {confidence}%, Chain ID {chain_id}):\n"
        f"- Gas Limit: {gas_limit}\n"
        f"- Max Fee Per Gas: {max_fee} Gwei\n"
        f"- Total Cost: {total_cost_gwei} Gwei ({total_cost_eth:.6f} ETH)"
    )

@mcp.tool()
async def get_supported_chains(ctx: Optional[Context] = None) -> str:
    """
    List the blockchain networks supported by the Blocknative Gas Platform, formatted as a Markdown table.

    Parameters:
    - ctx (Optional[Context]): The MCP context object. Default: None.

    Returns:
    - A Markdown table listing supported chains with their chain ID, system, and network.
    """
    data = await fetch_supported_chains()
    if data["error"]:
        return data["error"]
    
    chains = data["chains"]
    if not chains:
        return "No supported chains found."
    
    output = "Supported Chains:\n\n"
    output += "| Chain ID | System | Network |\n"
    output += "|----------|--------|---------|\n"
    for chain in chains:
        chain_id = chain.get("chainId", "Unknown")
        system = chain.get("system", "Unknown")
        network = chain.get("network", "Unknown")
        output += f"| {chain_id} | {system} | {network} |\n"
    
    return output

# Prompts
@mcp.prompt()
def gas_price_query(confidence: int, chain_id: int = 1) -> List[base.Message]:
    """
    Prompt template for querying gas prices at a specific confidence level and chain.

    Parameters:
    - confidence (int): The confidence level for gas price prediction (0-100).
    - chain_id (int): The ID of the blockchain network (e.g., 1 for Ethereum Mainnet). Default: 1.
    """
    try:
        if not (0 <= confidence <= 100):
            raise ValueError("Confidence must be between 0 and 100")
        if chain_id <= 0:
            raise ValueError("Invalid chain ID")
    except ValueError as e:
        return [
            base.UserMessage(f"Please provide valid inputs: {str(e)}")
        ]
    
    return [
        base.UserMessage(
            f"What is the current gas price for chain ID {chain_id} transactions "
            f"with {confidence}% confidence?"
        ),
        base.AssistantMessage(
            f"Let me fetch the gas price predictions for chain ID {chain_id}."
        )
    ]

# Run the server
def main() -> None:
    mcp.run()
