from typing import Any, Dict
from src.client.interfaces import TradingClient

try:
    from growwapi import GrowwAPI
    import pyotp
except ImportError:
    GrowwAPI = None
    pyotp = None

class GrowwClient(TradingClient):
    """
    Groww API client implementation.
    """
    
    def __init__(self, api_key: str, totp_secret: str):
        self.api_key = api_key
        self.totp_secret = totp_secret
        
        if GrowwAPI is None or pyotp is None:
            raise ImportError("growwapi or pyotp is not installed. Please install them to use GrowwClient.")
            
        totp_gen = pyotp.TOTP(totp_secret)
        totp = totp_gen.now()
        
        access_token = GrowwAPI.get_access_token(api_key=api_key, totp=totp)
        self.client = GrowwAPI(access_token)

    def get_option_chain(self, exchange: str, underlying: str, expiry_date: str) -> Dict[str, Any]:
        """
        Fetch the option chain using Groww SDK.
        """
        # Map exchange string to SDK constant if needed. We assume NSE by default if not provided correctly.
        exch = self.client.EXCHANGE_NSE if exchange.upper() == "NSE" else self.client.EXCHANGE_BSE
        
        response = self.client.get_option_chain(
            exchange=exch,
            underlying=underlying,
            expiry_date=expiry_date
        )
        return response
