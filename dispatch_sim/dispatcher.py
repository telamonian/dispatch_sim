from abc import ABC
import numpy as np
from queue import Queue
import time
from typing import Optional, TypedDict, Union

from dispatch_sim.event import OrderEvent, FoodPrepEvent, CourierArrivalEvent, PickupEvent

__all__ = ["MatchedDispatcher", "FifoDispatcher"]

# some type hint aliases
class _EventHistory(TypedDict):
    OrderEvent: list[OrderEvent]
    FoodPrepEvent: list[FoodPrepEvent]
    CourierArrivalEvent: list[CourierArrivalEvent]
    PickupEvent: list[PickupEvent]

_EventUnion = Union[OrderEvent, FoodPrepEvent, CourierArrivalEvent, PickupEvent]
_PrePickupInfo = Optional[tuple[FoodPrepEvent, CourierArrivalEvent]]


class Dispatcher(ABC):
    """Abstract base class for Dispatcher, an object that supplies the business logic for handling/dispatching the
    various events that occur as part of our simulated order dispatch system. In theory, this component could be
    re-used in a "real", non-simulated dispatch system. For example, a Dispatcher could be used to help implement
    the behavior of a REST server
    """
    history: _EventHistory
    timestamp: bool

    def __init__(self, timestamp: bool=False):
        self.history = {
            "OrderEvent": [],
            "FoodPrepEvent": [],
            "CourierArrivalEvent": [],
            "PickupEvent": [],
        }
        self.timestamp = timestamp

    def __str__(self) -> str:
        return (f"Mean food wait time: {round(self.foodWaitTimeMean*1e3)} ms\n"
                f"Mean courier wait time: {round(self.courierWaitTimeMean*1e3)} ms")

    def doOrder(self, event: OrderEvent) -> OrderEvent:
        """Handle recieving an order event. Prints an informative message to stdout and adds the event to the
        history for later perusal.

        Returns the order event so that the calling context can then
        submit (or simulate the submission of) the relevant order to restaurant that will prepare it
        """
        self._addToHistory(event)
        return event

    def doFoodPrep(self, event: FoodPrepEvent) -> _PrePickupInfo:
        """Handle receiving a food prep done event. Prints an informative message to stdout and adds the event to the
        history for later perusal.

        Attempts to match the newly prepared food with an appropriate courier for pickup. If a matching courier is
        found, returns the relevant (FoodPrepEvent, CourierArrivalEvent) pair. If no such courier is currently
        avaible, returns None
        """
        raise NotImplementedError

    def doCourierArrival(self, event: CourierArrivalEvent) -> _PrePickupInfo:
        """Handle receiving a courier arrival event. Prints an informative message to stdout and adds the event to the
        history for later perusal.

        Attempts to match the newly arrived courier with an appropriate prepared order. If a matching prepared order
        is found, returns the relevant (FoodPrepEvent, CourierArrivalEvent) pair. If no such prepared order is
        currently avaible, returns None
        """
        raise NotImplementedError

    def doPickup(self, event: PickupEvent):
        """Handle recieving an order event. Prints an informative message to stdout and adds the event to the
        history for later perusal.
        """
        self._addToHistory(event)

    @property
    def foodWaitTimeMean(self) -> float:
        """Returns the mean of the "food wait time" of all picked up orders observed by this Dispatcher instance.
        "food wait time" is the difference between when an order is picked up and when it's preparation is finished
        """
        return np.mean([event.foodWaitTime for event in self.history["PickupEvent"]])

    @property
    def courierWaitTimeMean(self) -> float:
        """Returns the mean of the "courier wait time" of all picked up orders observed by this Dispatcher instance.
        "food wait time" is the difference between when an order is picked up and when it's courier arrives
        """
        return np.mean([event.courierWaitTime for event in self.history["PickupEvent"]])

    def _addToHistory(self, event: _EventUnion):
        # print an informative message about the event to stdout
        if self.timestamp:
            print(f"[{time.time():.4f}]", end=" ")
        print(event, end="\n\n")

        # save the event by type for later analysis
        self.history[event.__class__.__name__].append(event)

class MatchedDispatcher(Dispatcher):
    """Dispatcher subclass that matches for pickup each courier with the order for which they were originally dispatched
    """
    courierArrivalDict: dict[str, CourierArrivalEvent]
    foodPrepDict: dict[str, FoodPrepEvent]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.courierArrivalDict = {}
        self.foodPrepDict = {}

    def doFoodPrep(self, event: FoodPrepEvent) -> _PrePickupInfo:
        self._addToHistory(event)

        oid = event.order.id
        if oid in self.courierArrivalDict:
            return event, self.courierArrivalDict.pop(oid)
        else:
            self.foodPrepDict[oid] = event
            return None

    def doCourierArrival(self, event: CourierArrivalEvent) -> _PrePickupInfo:
        self._addToHistory(event)

        oid = event.order.id
        if oid in self.foodPrepDict:
            return self.foodPrepDict.pop(oid), event
        else:
            self.courierArrivalDict[oid] = event
            return None

class FifoDispatcher(Dispatcher):
    """Dispatcher subclass that matches for pickup each prepared order with the first available courier
    """
    foodPrepQueue: Queue[FoodPrepEvent]
    courierArrivalQueue: Queue[CourierArrivalEvent]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.foodPrepQueue: Queue[FoodPrepEvent] = Queue()
        self.courierArrivalQueue: Queue[CourierArrivalEvent] = Queue()

    def doFoodPrep(self, event: FoodPrepEvent) -> _PrePickupInfo:
        self._addToHistory(event)

        if not self.courierArrivalQueue.empty():
            return event, self.courierArrivalQueue.get(block=False)
        else:
            self.foodPrepQueue.put(event, block=False)
            return None

    def doCourierArrival(self, event: CourierArrivalEvent) -> _PrePickupInfo:
        self._addToHistory(event)

        if not self.foodPrepQueue.empty():
            return self.foodPrepQueue.get(block=False), event
        else:
            self.courierArrivalQueue.put(event, block=False)
            return None
