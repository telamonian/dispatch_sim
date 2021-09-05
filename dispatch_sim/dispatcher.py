import numpy as np
from queue import Queue

from dispatch_sim.event import OrderEvent, FoodPrepEvent, CourierArrivalEvent, PickupEvent

__all__ = ["MatchedDispatcer", "FifoDispatcher"]


class _BaseDispatcher:
    def __init__(self):
        self.history = {klass.__name__: [] for klass in (OrderEvent, FoodPrepEvent, CourierArrivalEvent, PickupEvent)}

    def __repr__(self):
        return (f"Mean food wait time: {self.foodWaitTimeMean():.4f}\n"
                f"Mean courier wait time: {self.courierWaitTimeMean():.4f}")

    def addToHistory(self, event, EventClass):
        # sanity check the event class
        if not isinstance(event, EventClass):
            raise ValueError

        # print an informative message about the event to stdout
        print(event)

        # save the event by type for later analysis
        self.history[event.__class__.__name__].append(event)

    def doOrder(self, event):
        self.addToHistory(event, OrderEvent)
        return event

    def doFoodPrep(self, event):
        raise NotImplementedError

    def doCourierArrival(self, event):
        raise NotImplementedError

    def doPickup(self, event):
        self.addToHistory(event, PickupEvent)
        return event

    def foodWaitTimeMean(self):
        return np.mean(event.foodWaitTime() for event in self.history['PickupEvent'])

    def courierWaitTimeMean(self):
        return np.mean(event.courierWaitTime() for event in self.history['PickupEvent'])

class MatchedDispatcher(_BaseDispatcher):
    def __init__(self):
        super().__init__()

        self.courierArrivalDict = {}
        self.foodPrepDict = {}

    def doFoodPrep(self, event):
        self.addToHistory(event, FoodPrepEvent)

        oid = event.order.id
        if oid in self.courierArrivalDict:
            return event, self.courierArrivalDict.pop(oid)
        else:
            self.foodPrepDict[oid] = event

    def doCourierArrival(self, event):
        self.addToHistory(event, CourierArrivalEvent)

        oid = event.order.id
        if oid in self.foodPrepDict:
            return self.foodPrepDict.pop(oid), event
        else:
            self.courierArrivalDict[oid] = event


class FifoDispatcher(_BaseDispatcher):
    def __init__(self):
        super().__init__()

        self.foodPrepQueue = Queue()
        self.courierArrivalQueue = Queue()

    def doFoodPrep(self, event):
        self.addToHistory(event, FoodPrepEvent)

        if not self.courierArrivalQueue.empty():
            return event, self.courierArrivalQueue.get(block=False)
        else:
            self.foodPrepQueue.put(event, block=False)

    def doCourierArrival(self, event):
        self.addToHistory(event, CourierArrivalEvent)

        if not self.foodPrepQueue.empty():
            return self.foodPrepQueue.get(block=False), event
        else:
            self.courierArrivalQueue.put(event, block=False)
