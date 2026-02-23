from typing import Dict, Type
from src.client.interfaces import TradingClient
from src.client.groww import GrowwClient


class ClientFactory:
    """
    Factory to instantiate different trading clients.
    """ 
    
    _clients: Dict[str, Type[TradingClient]] = {
        "groww": GrowwClient,
    }

    @classmethod
    def register_client(cls, name: str, client_class: Type[TradingClient]):
        """Register a new client type."""
        cls._clients[name.lower()] = client_class

    @classmethod
    def get_client(cls, name: str, **kwargs) -> TradingClient:
        """
        Get a trading client instance by name.
        """
        client_class = cls._clients.get(name.lower())
        if not client_class:
            raise ValueError(f"Trading client '{name}' not found. Supported clients: {list(cls._clients.keys())}")
        return client_class(**kwargs)
