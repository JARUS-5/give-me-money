# Give Me Money - Trading Architecture

This project is a Python-based trading system architecture designed to handle live market data via a Publisher/Subscriber model, abstracted via a flexible Broker Client Factory.

## Current Progress

### Client Abstraction & Factory Pattern
- **`src/client/interfaces.py`**: A generalized `TradingClient` base interface to define methods that any broker client (e.g., Groww, Zerodha) must implement.
- **`src/client/groww.py`**: A localized mock implementation of a `GrowwClient` capable of returning options chain data structures.
- **`src/client/factory.py`**: A `ClientFactory` to dynamically register and instantiate various trading clients.

### Live Data Pub/Sub System
- **`src/pubsub/interfaces.py`**: Defined `IPublisher` and `ISubscriber` interfaces.
- **`src/pubsub/publisher.py`**: The `OptionChainData` class handles options chain updates:
  - Supports global subscribers (receive all strikes).
  - Supports strike-specific subscribers (receive only data related to their subscribed strike prices, e.g. `"23400"`).
  - Handles duplicate prevention to ensure subscribers taking both global and specific updates do not receive overlapping notifications.

### Testing
Comprehensive unit and integration testing have been completed using `pytest` inside the `tests/` directory:
- `test_factory.py`
- `test_pubsub.py`
- `test_integration.py`

## Running Tests
To run the automated test suite, activate your virtual environment and execute `pytest`:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate

# Run tests
pytest tests/
```
