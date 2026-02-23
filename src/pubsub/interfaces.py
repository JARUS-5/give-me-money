from abc import ABC, abstractmethod
from typing import Any, Dict


class ISubscriber(ABC):
    """
    Subscriber interface for receiving live data updates.
    """
    
    @abstractmethod
    def update(self, data: Dict[str, Any]):
        """Receive update from publisher."""
        pass


class IPublisher(ABC):
    """
    Publisher interface for managing subscribers and sending data updates.
    """
    
    @abstractmethod
    def add_subscriber(self, subscriber: ISubscriber, strike: str = None):
        """Add a new subscriber, optionally filtering by strike."""
        pass

    @abstractmethod
    def remove_subscriber(self, subscriber: ISubscriber):
        """Remove an existing subscriber."""
        pass

    @abstractmethod
    def notify(self, data: Dict[str, Any]):
        """Send updates to all subscribers based on their registered strikes."""
        pass
