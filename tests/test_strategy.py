import pytest
from src.strategies.max_oi import MaxOIStrategy
from src.pubsub.publisher import OptionChainData

def test_max_oi_strategy():
    strategy = MaxOIStrategy()
    publisher = OptionChainData()
    
    # Subscribe to ALL strikes
    publisher.add_subscriber(strategy)
    
    # Generate 15 strikes around an underlying of 25000
    # True underlying will be 25000
    market_data = {
        "underlying_ltp": 25000,
        "strikes": {}
    }
    
    # Distances from 25000:
    # 24300, 24400, ..., 25700 (15 strikes in total, 100 intervals)
    for strike in range(24300, 25800, 100):
        strike_str = str(strike)
        market_data["strikes"][strike_str] = {
            "CE": {"open_interest": 10},
            "PE": {"open_interest": 10}
        }
        
    # The 12 strikes nearest to 25000 are 24400 through 25500.
    # The strikes left out should be the 3 furthest:
    # 25700 (dist 700), 24300 (dist 700), 25600 (dist 600)
    
    # Let's put a massive OI in an ignored furthest strike:
    market_data["strikes"]["24300"]["CE"]["open_interest"] = 999999  # Too far, ignored
    
    # Within the 12 nearest, let's put the max OI for PE at 25100
    market_data["strikes"]["25100"]["PE"]["open_interest"] = 5000
    
    
    publisher.notify(market_data)
    
    # Verify the results
    oi_type, oi_strike = strategy.get_max_oi_details()
    
    assert oi_type == "PE"
    assert oi_strike == "25100"
    assert strategy.max_oi_value == 5000

    # 2. Update with new higher OI data
    # Change the highest within the nearest 12 to a Call option at 24900
    market_data["strikes"]["24900"]["CE"]["open_interest"] = 10000
    
    publisher.notify(market_data)
    
    oi_type, oi_strike = strategy.get_max_oi_details()
    assert oi_type == "CE"
    assert oi_strike == "24900"
    assert strategy.max_oi_value == 10000
