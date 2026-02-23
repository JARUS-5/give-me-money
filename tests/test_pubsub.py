import pytest
from typing import Any, Dict
from src.pubsub.interfaces import ISubscriber
from src.pubsub.publisher import OptionChainData


class MockSubscriber(ISubscriber):
    def __init__(self):
        self.received_data = []

    def update(self, data: Dict[str, Any]):
        self.received_data.append(data)


@pytest.fixture
def publisher():
    return OptionChainData()


def test_add_and_remove_subscriber(publisher):
    sub = MockSubscriber()

    publisher.add_subscriber(sub, "23400")
    assert sub in publisher._all_subscribers
    assert sub in publisher._subscribers["23400"]

    publisher.remove_subscriber(sub)
    assert sub not in publisher._all_subscribers
    assert sub not in publisher._subscribers["23400"]


def test_notify_global_subscriber(publisher):
    sub = MockSubscriber()
    # Subscribe to ALL strikes
    publisher.add_subscriber(sub)

    data = {
        "underlying_ltp": 25641.7,
        "strikes": {
            "23400": {"CE": {"ltp": 2200}},
            "23450": {"CE": {"ltp": 2082}}
        }
    }

    publisher.notify(data)

    assert len(sub.received_data) == 1
    assert sub.received_data[0] == data


def test_notify_specific_strike_subscriber(publisher):
    sub_23400 = MockSubscriber()
    sub_23450 = MockSubscriber()
    sub_both = MockSubscriber()
    
    # Subscribe to specific strikes
    publisher.add_subscriber(sub_23400, "23400")
    publisher.add_subscriber(sub_23450, "23450")
    publisher.add_subscriber(sub_both, "23400")
    publisher.add_subscriber(sub_both, "23450")

    data = {
        "underlying_ltp": 25641.7,
        "strikes": {
            "23400": {"CE": {"ltp": 2200}},
            "23450": {"CE": {"ltp": 2082}}
        }
    }

    publisher.notify(data)

    # Check 23400 gets only 23400 data
    assert len(sub_23400.received_data) == 1
    assert sub_23400.received_data[0] == {
        "underlying_ltp": 25641.7,
        "strikes": {
            "23400": {"CE": {"ltp": 2200}}
        }
    }

    # Check 23450 gets only 23450 data
    assert len(sub_23450.received_data) == 1
    assert sub_23450.received_data[0] == {
        "underlying_ltp": 25641.7,
        "strikes": {
            "23450": {"CE": {"ltp": 2082}}
        }
    }
    
    # Check that subscriber to both got both independent notifications
    assert len(sub_both.received_data) == 2


def test_notify_empty_data(publisher):
    sub = MockSubscriber()
    publisher.add_subscriber(sub)
    publisher.notify({})
    assert len(sub.received_data) == 0


def test_add_subscriber_with_multiple_strikes(publisher):
    sub = MockSubscriber()
    
    # Subscribe using list of strikes
    publisher.add_subscriber(sub, strikes=["23400", "23500"])
    
    data = {
        "underlying_ltp": 25641.7,
        "strikes": {
            "23400": {"CE": {"ltp": 2200}},
            "23450": {"CE": {"ltp": 2080}},
            "23500": {"CE": {"ltp": 2000}}
        }
    }

    publisher.notify(data)

    # Should only receive 2 notifications/updates for the 2 subscribed strikes
    assert len(sub.received_data) == 2
    
    received_strikes = [list(update["strikes"].keys())[0] for update in sub.received_data]
    assert "23400" in received_strikes
    assert "23500" in received_strikes
    assert "23450" not in received_strikes


