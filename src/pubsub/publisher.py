from typing import Any, Dict, Set, DefaultDict, Union, List
from collections import defaultdict
from src.pubsub.interfaces import IPublisher, ISubscriber

class OptionChainData(IPublisher):
    """
    Publisher for option chain data.
    """
    
    def __init__(self):
        # Maps a strike price (string) to a set of subscribers interested in it.
        # Use an empty string "" to represent subscribers interested in ALL strikes.
        self._subscribers: DefaultDict[str, Set[ISubscriber]] = defaultdict(set)
        
        # Keep track of all raw subscribers so we can easily remove them later.
        self._all_subscribers: Set[ISubscriber] = set()

    def add_subscriber(self, subscriber: ISubscriber, strikes: Union[str, List[str]] = None):
        """
        Subscribe to OptionChain updates.
        If strikes is None or empty, the subscriber will receive data for all strikes.
        """
        if not strikes:
            keys = [""]
        elif isinstance(strikes, str):
            keys = [strikes]
        else:
            keys = strikes
            
        for key in keys:
            k = key if key else ""
            self._subscribers[k].add(subscriber)
            
        self._all_subscribers.add(subscriber)

    def remove_subscriber(self, subscriber: ISubscriber):
        """
        Remove a subscriber from all its subscriptions.
        """
        if subscriber in self._all_subscribers:
            self._all_subscribers.remove(subscriber)
            # Remove from all strike buckets
            for strike_subscribers in self._subscribers.values():
                if subscriber in strike_subscribers:
                    strike_subscribers.remove(subscriber)

    def notify(self, data: Dict[str, Any]):
        """
        Distribute data to subscribers.
        `data` should follow the Groww SDK Option Chain response schema, e.g.:
        {
            "underlying_ltp": 25641.7,
            "strikes": {
                "23400": { ... },
                "23450": { ... }
            }
        }
        """
        if "strikes" not in data:
            return

        strikes_data = data["strikes"]
        
        # 1. Notify global subscribers (those subscribed to all strikes)
        global_subs = self._subscribers.get("", set())
        for sub in global_subs:
            sub.update(data)
            
        # 2. Notify strike-specific subscribers
        for strike, strike_info in strikes_data.items():
            specific_subs = self._subscribers.get(strike, set())
            
            # Prevent double-notifying if a subscriber registered for both "" and a specific strike
            subs_to_notify = specific_subs - global_subs
            
            if subs_to_notify:
                # Construct a filtered data payload for this specific strike
                filtered_data = {
                    "underlying_ltp": data.get("underlying_ltp"),
                    "strikes": {strike: strike_info}
                }
                for sub in subs_to_notify:
                    sub.update(filtered_data)
