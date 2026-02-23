import pytest
from src.client.factory import ClientFactory
from src.client.groww import GrowwClient
from src.client.interfaces import TradingClient


class DummyClient(TradingClient):
    def get_option_chain(self, exchange: str, underlying: str, expiry_date: str):
        return {}


def test_factory_get_existing_client():
    client = ClientFactory.get_client("groww", api_token="test_token")
    assert isinstance(client, GrowwClient)
    assert client.api_token == "test_token"


def test_factory_get_nonexistent_client():
    with pytest.raises(ValueError):
        ClientFactory.get_client("zerodha", api_token="test_token")


def test_factory_register_new_client():
    ClientFactory.register_client("dummy", DummyClient)
    client = ClientFactory.get_client("dummy")
    assert isinstance(client, DummyClient)
