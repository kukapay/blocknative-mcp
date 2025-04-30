# Blocknative MCP Server

An MCP server that provides real-time gas price predictions across multiple blockchains, powered by Blocknative.

![GitHub License](https://img.shields.io/github/license/kukapay/blocknative-mcp)
![Python Version](https://img.shields.io/badge/python-3.10+-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## Features

- **Tools**:
  - `predict_gas_price`: Fetches gas price predictions for a specified chain (default: Ethereum Mainnet, `chain_id=1`), including base fee and a table with confidence levels, price, max priority fee, and max fee.
  - `estimate_gas_cost`: Estimates transaction costs based on gas limit, confidence level, and chain ID, returning costs in Gwei and ETH.
  - `get_supported_chains`: Lists supported blockchains in a table with chain ID, system, and network.
- **Prompt**:
  - `gas_price_query`: A prompt template for querying gas prices at a specific confidence level and chain ID.
- **Asynchronous**: Uses `httpx` for non-blocking HTTP requests to Blocknative's Gas Price and Chains APIs.
- **Optional API Key**: Supports low-frequency access without a Blocknative API key; high-frequency use requires setting `BLOCKNATIVE_API_KEY`.

## Prerequisites

- **Python**: Version 3.10
- **uv**: For dependency management and running the project ([installation guide](https://github.com/astral-sh/uv))
- **Blocknative API Key** (optional): Required for high-frequency API access. Sign up at [Blocknative](https://www.blocknative.com/) to obtain a free API key.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/kukapay/blocknative-mcp.git
   cd blocknative-mcp
   ```

2. **Set Up the Project with `uv`**:
   ```bash
   uv sync
   ```

3. **Set the Blocknative API Key (Optional)**:
   - For high-frequency access, set the environment variable:
     ```bash
     export BLOCKNATIVE_API_KEY="your-api-key-here"
     ```
   - For low-frequency access, skip this step.


## Usage

The server provides three tools and one prompt, accessible via the FastMCP framework. You can run the server in development mode, execute it directly, or integrate it with Claude Desktop.

### Running the Server

1. **Development Mode with MCP Inspector**:
   ```bash
   uv run mcp dev blocknative-mcp
   ```
   This opens the MCP Inspector, a web interface for testing tools and prompts interactively.

2. **Direct Execution**:
   ```bash
   uv run blocknative-mcp
   ```

3. **Claude Desktop Integration**:
   ```bash
   uv run mcp install blocknative-mcp --name "Blocknative MCP Server"
   ```
   This installs the server for use with Claude Desktop.

### Tools

- **`predict_gas_price(chain_id: int = 1) -> str`**:
  Fetches gas price predictions for a chain (default: Ethereum Mainnet). Returns base fee and a Markdown table with confidence levels, price, max priority fee, and max fee.
  - Example:
    ```markdown
    Gas Price Predictions for Chain ID 1 (ethereum/main):
    - Base Fee Per Gas: 0.382910791 Gwei

    | Confidence | Price (Gwei) | Max Priority Fee (Gwei) | Max Fee (Gwei) |
    |------------|--------------|-------------------------|----------------|
    | 99%        | 0.52         | 0.14                    | 0.9            |
    | 95%        | 0.48         | 0.094                   | 0.86           |
    | 90%        | 0.47         | 0.089                   | 0.85           |
    | 80%        | 0.46         | 0.079                   | 0.84           |
    | 70%        | 0.45         | 0.069                   | 0.83           |
    ```

- **`estimate_gas_cost(gas_limit: int, confidence: int = 99, chain_id: int = 1) -> str`**:
  Estimates transaction costs based on gas limit, confidence level, and chain ID. Returns costs in Gwei and ETH.
  - Example:
    ```markdown
    Estimated Gas Cost (Confidence 90%, Chain ID 1):
    - Gas Limit: 21000
    - Max Fee Per Gas: 0.85 Gwei
    - Total Cost: 17850 Gwei (0.00001785 ETH)
    ```

- **`get_supported_chains(ctx: Optional[Context] = None) -> str`**:
  Lists supported chains in a Markdown table with chain ID, system, and network.
  - Example:
    ```markdown
    Supported Chains:

    | Chain ID   | System   | Network   |
    |------------|----------|-----------|
    | 1          | ethereum | main      |
    | 137        | polygon  | mainnet   |
    | 8453       | base     | mainnet   |
    | 11155111   | ethereum | sepolia   |
    ```

### Prompts
    
- **`gas_price_query(confidence: int, chain_id: int = 1) -> List[base.Message]`**:
  A prompt template for querying gas prices at a specific confidence level and chain ID.
  - Example:
    ```markdown
    - User: What is the current gas price for chain ID 1 transactions with 90% confidence?
    - Assistant: Let me fetch the gas price predictions for chain ID 1.
    ```


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

