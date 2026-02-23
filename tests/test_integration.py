import pytest
from typing import Any, Dict

@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    class MockGrowwAPI:
        EXCHANGE_NSE = "NSE"
        EXCHANGE_BSE = "BSE"
        @classmethod
        def get_access_token(cls, api_key, totp): return "mock_token"
        def __init__(self, token): self.token = token
        
        # We need this to return the test Option Chain data we're expecting downstream!
        def get_option_chain(self, exchange, underlying, expiry_date):
            return {
                "underlying_ltp": 25641.7,
                "strikes": {
                    "23400": {"CE": {"ltp": 2200}},
                    "23450": {"CE": {"ltp": 2082}}
                }
            }
            
    class MockTOTP:
        def __init__(self, secret): pass
        def now(self): return "123"
        
    class MockPyOTP:
        TOTP = MockTOTP

    monkeypatch.setattr("src.client.groww.GrowwAPI", MockGrowwAPI)
    monkeypatch.setattr("src.client.groww.pyotp", MockPyOTP)

from src.client.factory import ClientFactory
from src.pubsub.interfaces import ISubscriber
from src.pubsub.publisher import OptionChainData

class StrategySubscriber(ISubscriber):

    def __init__(self, name: str):
        self.name = name
        self.received_updates = []

    def update(self, data: Dict[str, Any]):
        self.received_updates.append(data)


def test_client_to_pubsub_integration():

    
    # 1. Initialize Client
    client = ClientFactory.get_client("groww", api_key="dummy_token", totp_secret="dummy_secret")
    
    # 2. Setup Publisher and Subscribers
    publisher = OptionChainData()
    
    straddle_strategy = StrategySubscriber("straddle_23400")
    strangle_strategy = StrategySubscriber("strangle_23450")
    general_strategy = StrategySubscriber("general")
    
    # Straddle wants only 23400 strike
    publisher.add_subscriber(straddle_strategy, strikes="23400")
    
    # Strangle wants only 23450 strike
    publisher.add_subscriber(strangle_strategy, strikes="23450")
    
    # General strategy wants all strikes (no strike specified)
    publisher.add_subscriber(general_strategy)
    
    # 3. Fetch Data from Client
    market_data = client.get_option_chain(
        exchange="NSE",
        underlying="NIFTY",
        expiry_date="2025-11-28"
    )
    
    # 4. Notify Publisher
    publisher.notify(market_data)
    
    # 5. Verify received data
    
    # Straddle should only have 1 update, with strike 23400
    assert len(straddle_strategy.received_updates) == 1
    straddle_data = straddle_strategy.received_updates[0]
    assert "23400" in straddle_data["strikes"]
    assert "23450" not in straddle_data["strikes"]
    
    # Strangle should only have 1 update, with strike 23450
    assert len(strangle_strategy.received_updates) == 1
    strangle_data = strangle_strategy.received_updates[0]
    assert "23450" in strangle_data["strikes"]
    assert "23400" not in strangle_data["strikes"]
    
    # General strategy should receive the full unfiltered data
    assert len(general_strategy.received_updates) == 1
    general_data = general_strategy.received_updates[0]
    assert "23400" in general_data["strikes"]
    assert "23450" in general_data["strikes"]
    
    # Ensure all updates retain global fields like underlying_ltp
    assert straddle_data["underlying_ltp"] == 25641.7
    assert strangle_data["underlying_ltp"] == 25641.7
    assert general_data["underlying_ltp"] == 25641.7
