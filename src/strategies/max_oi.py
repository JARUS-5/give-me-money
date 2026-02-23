from typing import Any, Dict, Tuple, Optional
from src.pubsub.interfaces import ISubscriber

class MaxOIStrategy(ISubscriber):
    """
    A strategy that listens to option chain data, finds the 12 strike 
    prices nearest to the current underlying LTP, and identifies which 
    specific option (Call or Put) has the absolute highest Open Interest (OI)
    among them, returning its type ("CE" or "PE") and strike price.
    """
    
    def __init__(self):
        self.max_oi_type: Optional[str] = None  # "CE" or "PE"
        self.max_oi_strike: Optional[str] = None
        self.max_oi_value: int = -1

    def update(self, data: Dict[str, Any]):
        """
        Process the option chain data and identify the strike with max OI 
        among the 12 strikes nearest to the underlying_ltp.
        """
        if "strikes" not in data or "underlying_ltp" not in data:
            return
            
        underlying_ltp = data.get("underlying_ltp", 0.0)
        if not underlying_ltp:
            return

        strikes_data = data["strikes"]
        
        # 1. Parse and sort strikes by distance to underlying_ltp
        strike_distances = []
        for strike in strikes_data.keys():
            try:
                dist = abs(float(strike) - float(underlying_ltp))
                strike_distances.append((dist, strike))
            except ValueError:
                continue
                
        strike_distances.sort(key=lambda x: x[0])
        
        # 2. Take the 12 nearest
        nearest_strikes = [s[1] for s in strike_distances[:12]]
        
        # 3. Find the maximum OI among these nearest strikes (Calls and Puts)
        max_oi = -1
        max_type = None
        max_strike = None
        
        for strike in nearest_strikes:
            strike_info = strikes_data[strike]
            
            ce_oi = strike_info.get("CE", {}).get("open_interest", -1)
            pe_oi = strike_info.get("PE", {}).get("open_interest", -1)
            
            if ce_oi > max_oi:
                max_oi = ce_oi
                max_type = "CE"
                max_strike = strike
                
            if pe_oi > max_oi:
                max_oi = pe_oi
                max_type = "PE"
                max_strike = strike
                
        # 4. Update the strategy's current state with the result for this tick
        self.max_oi_value = max_oi
        self.max_oi_type = max_type
        self.max_oi_strike = max_strike
                
    def get_max_oi_details(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Returns:
            Tuple[Type ("CE" or "PE"), Strike with max OI]
        """
        return self.max_oi_type, self.max_oi_strike
