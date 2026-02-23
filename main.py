import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.client.factory import ClientFactory
from src.pubsub.publisher import OptionChainData
from src.strategies.max_oi import MaxOIStrategy

def get_next_expiry_date(currently: datetime) -> str:
    """
    Returns the date string of the next upcoming Tuesday.
    If today is Tuesday, it returns today.
    """
    days_ahead = 1 - currently.weekday() # Tuesday is 1
    if days_ahead < 0:
        days_ahead += 7
    next_tuesday = currently + timedelta(days=days_ahead)
    return next_tuesday.strftime("%Y-%m-%d")

def main():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GROWW_API_KEY")
    totp_secret = os.getenv("GROWW_TOTP_SECRET")
    
    if not api_key or api_key == "your_groww_api_key_here" or not totp_secret or totp_secret == "your_totp_secret_here":
        print("Please configure valid GROWW_API_KEY and GROWW_TOTP_SECRET in the .env file.")
        return

    print("Initializing components...")
    
    # 1. Setup Client
    client = ClientFactory.get_client("groww", api_key=api_key, totp_secret=totp_secret)
    
    # 2. Setup Publisher and Strategy
    publisher = OptionChainData()
    strategy = MaxOIStrategy()
    
    # Subscribe the strategy to listen to all strikes (global)
    publisher.add_subscriber(strategy)
    
    exchange = "NSE"
    underlying = "NIFTY"
    expiry_date = get_next_expiry_date(datetime.now())

    print(f"Starting execution loop for {underlying} ({exchange}) expiring {expiry_date}...")
    
    while True:
        try:
            print(f"[{datetime.now()}] Fetching live option chain data...")
            market_data = client.get_option_chain(
                exchange=exchange,
                underlying=underlying,
                expiry_date=expiry_date
            )
            
            # Notify the publisher so subscribers (our strategy) get updated
            publisher.notify(market_data)
            
            # Print the results computed by the strategy
            oi_type, oi_strike = strategy.get_max_oi_details()
            
            underlying_ltp = market_data.get("underlying_ltp")
            print(f"[{datetime.now()}] Current LTP: {underlying_ltp}")
            
            if oi_type and oi_strike:
                print(f"[{datetime.now()}] Max OI near LTP detected in {oi_type} at Strike {oi_strike} (OI: {strategy.max_oi_value})")
            else:
                print(f"[{datetime.now()}] No valid OI strikes found within the nearest 12 strikes to the current LTP.")
                
            print("-" * 50)
            
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Gracefully stopping execution. Goodbye!")
            break
        except Exception as e:
            print(f"[{datetime.now()}] Error fetching or processing data: {e}")
            
        # Wait 60 seconds before next fetch
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Gracefully stopping execution during sleep. Goodbye!")
            break


if __name__ == "__main__":
    main()
