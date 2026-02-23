from abc import ABC, abstractmethod
from typing import Any, Dict


class TradingClient(ABC):
    """
    Abstract base class for all broker clients.
    """

    @abstractmethod
    def get_option_chain(self, exchange: str, underlying: str, expiry_date: str) -> Dict[str, Any]:
        """
        Fetch the option chain for a given underlying and expiry date.
        """
        pass
