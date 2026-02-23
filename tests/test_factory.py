import pytest
from src.client.factory import ClientFactory
from src.client.groww import GrowwClient
from src.client.interfaces import TradingClient

class DummyClient(TradingClient):
    def get_option_chain(self, exchange: str, underlying: str, expiry_date: str):
        return {}

@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    class MockGrowwAPI:
        EXCHANGE_NSE = "NSE"
        EXCHANGE_BSE = "BSE"
        @classmethod
        def get_access_token(cls, api_key, totp): return "mock_token"
        def __init__(self, token): self.token = token
        def get_option_chain(self, exch, under, exp): return {}
        
    class MockTOTP:
        def __init__(self, secret): pass
        def now(self): return "123"
        
    class MockPyOTP:
        TOTP = MockTOTP

    monkeypatch.setattr("src.client.groww.GrowwAPI", MockGrowwAPI)
    monkeypatch.setattr("src.client.groww.pyotp", MockPyOTP)

def test_factory_get_existing_client():
    client = ClientFactory.get_client("groww", api_key="test_key", totp_secret="test_secret")
    assert isinstance(client, GrowwClient)
    assert client.api_key == "test_key"
    assert client.totp_secret == "test_secret"

def test_factory_get_nonexistent_client():
    with pytest.raises(ValueError):
        ClientFactory.get_client("zerodha", api_key="test_key", totp_secret="test_secret")

def test_factory_register_new_client():
    ClientFactory.register_client("dummy", DummyClient)
    client = ClientFactory.get_client("dummy")
    assert isinstance(client, DummyClient)
