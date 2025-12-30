# GenFlux

GenFlux Python SDK.

## Installation

```bash
pip install genflux
```

## Quick Start

```python
import genflux

# Simple greeting
print(genflux.hello())          # Hello, World!
print(genflux.hello("GenFlux")) # Hello, GenFlux!

# Check version
print(genflux.version())        # 0.1.0
```

## Using the Client

```python
from genflux import GenFlux

client = GenFlux()

# Test the SDK
print(client.ping())   # {'status': 'ok', 'message': 'GenFlux SDK is working!'}

# Echo a message
print(client.echo("Hello!"))  # Hello!

# Simple calculation
print(client.add(1, 2))  # 3
```

## Configuration (for API features)

For API features that require authentication:

### 1. Direct API Key

```python
from genflux import GenFlux

client = GenFlux(api_key="your-api-key")
```

### 2. Environment Variable

Set the `GENFLUX_API_KEY` environment variable:

```bash
export GENFLUX_API_KEY="your-api-key"
```

Then initialize without arguments:

```python
from genflux import GenFlux

client = GenFlux()
```

## Development

### Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### Running Tests

```bash
uv run pytest
```
