import numpy as np
from queue import Queue
from typing import Optional, TypedDict, Union

from dispatch_sim.event import OrderEvent, FoodPrepEvent, CourierArrivalEvent, PickupEvent

__all__ = ["MatchedDispatcher", "FifoDispatcher"]

# some type hinst aliases
_EventHistory = TypedDict(
    '_EventHistory',
    OrderEvent=list[OrderEvent],
    FoodPrepEvent=list[FoodPrepEvent],
    CourierArrivalEvent=list[CourierArrivalEvent],
    PickupEvent=list[PickupEvent],
)
_EventUnion = Union[OrderEvent, FoodPrepEvent, CourierArrivalEvent, PickupEvent]
_PrePickupInfo = Optional[tuple[FoodPrepEvent, CourierArrivalEvent]]


class _BaseDispatcher:
    history: _EventHistory

    def __init__(self):
        self.history = {
            "OrderEvent": [],
            "FoodPrepEvent": [],
            "CourierArrivalEvent": [],
            "PickupEvent": [],
        }

    def __repr__(self):
        return (f"Mean food wait time: {self.foodWaitTimeMean():.4f}\n"
                f"Mean courier wait time: {self.courierWaitTimeMean():.4f}")

    def addToHistory(self, event: _EventUnion):
        # print an informative message about the event to stdout
        print(event)

        # save the event by type for later analysis
        self.history[event.__class__.__name__].append(event)

    def doOrder(self, event: OrderEvent) -> OrderEvent:
        self.addToHistory(event)
        return event

    def doFoodPrep(self, event: FoodPrepEvent) -> _PrePickupInfo:
        raise NotImplementedError

    def doCourierArrival(self, event: CourierArrivalEvent) -> _PrePickupInfo:
        raise NotImplementedError

    def doPickup(self, event: PickupEvent):
        self.addToHistory(event)

    def foodWaitTimeMean(self) -> float:
        return np.mean([event.foodWaitTime for event in self.history["PickupEvent"]])

    def courierWaitTimeMean(self) -> float:
        return np.mean([event.courierWaitTime for event in self.history["PickupEvent"]])

class MatchedDispatcher(_BaseDispatcher):
    courierArrivalDict: dict[str, CourierArrivalEvent]
    foodPrepDict: dict[str, FoodPrepEvent]

    def __init__(self):
        super().__init__()

        self.courierArrivalDict = {}
        self.foodPrepDict = {}

    def doFoodPrep(self, event: FoodPrepEvent) -> _PrePickupInfo:
        self.addToHistory(event)

        oid = event.order.id
        if oid in self.courierArrivalDict:
            return event, self.courierArrivalDict.pop(oid)
        else:
            self.foodPrepDict[oid] = event

    def doCourierArrival(self, event: CourierArrivalEvent) -> _PrePickupInfo:
        self.addToHistory(event)

        oid = event.order.id
        if oid in self.foodPrepDict:
            return self.foodPrepDict.pop(oid), event
        else:
            self.courierArrivalDict[oid] = event


class FifoDispatcher(_BaseDispatcher):
    foodPrepQueue: Queue[FoodPrepEvent]
    courierArrivalQueue: Queue[CourierArrivalEvent]

    def __init__(self):
        super().__init__()

        self.foodPrepQueue: Queue[FoodPrepEvent] = Queue()
        self.courierArrivalQueue: Queue[CourierArrivalEvent] = Queue()

    def doFoodPrep(self, event: FoodPrepEvent) -> _PrePickupInfo:
        self.addToHistory(event)

        if not self.courierArrivalQueue.empty():
            return event, self.courierArrivalQueue.get(block=False)
        else:
            self.foodPrepQueue.put(event, block=False)

    def doCourierArrival(self, event: CourierArrivalEvent) -> _PrePickupInfo:
        self.addToHistory(event)

        if not self.foodPrepQueue.empty():
            return self.foodPrepQueue.get(block=False), event
        else:
            self.courierArrivalQueue.put(event, block=False)
