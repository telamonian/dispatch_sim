from enum import Enum, auto
import json
import jsonschema
from operator import attrgetter
from queue import Queue


orderSchema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "prepTime": {"type": "number"},
    },
}


def loadOrders(fpath):
    with open(fpath) as blob:
        orders = json.load(blob)
        for order in orders:
            jsonschema.validate(order)

    return [{ix: ix, **order} for ix, order in enumerate(orders)]


class Event:
    def __init__(self, *, time, order):
        # the originating order (ie a dict containing {id, name, prepTime}) associated with this event
        self.order = order

        # the simulation time at which the event occurs
        self.time = time


class OrderEvent(Event):
    def __repr__(self):
        return ("Order submitted\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


class FoodPrepEvent(Event):
    def __repr__(self):
        return ("Food prep finished\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


class CourierArrivalEvent(Event):
    def __repr__(self):
        return ("Courier arrived\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tdispatched for order id: {self.order.id}\n"
                f"\tdispatched for order name: {self.order.name}")


class PickupEvent(Event):
    def __init__(self, *, foodPrepEvent, courierArrivalEvent, **kwargs):
        super().__init__(**kwargs)

        self.foodPrepEvent = foodPrepEvent
        self.courierArrivalEvent = courierArrivalEvent

    def __repr__(self):
        return ("Order picked up by courier\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}"
                f"\tfood wait time: {self.foodWaitTime():.4f}\n"
                f"\tcourier wait time: {self.courierWaitTime():.4f}")

    def courierWaitTime(self):
        return self.time - self.courierArrivalEvent.time

    def foodWaitTime(self):
        return self.time - self.foodPrepEvent.time


class Sim:
    """delta: step size between input orders, in seconds"""


    def addOrder(self, time, order):
        self.extendEventsToRun((
            # food prep event associated with this order event
            Event(
                kind=Event.Kind.order,
                order=order,
                time=time,
            ),
        ))

    def extendEventsToRun(self, iterable):
        self._eventsToRun.extend(iterable)
        self._eventsToRun.sort(key=attrgetter("time"), reverse=True)

    def recordEvent(self, event):

    def run(self):
        while self._eventsToRun:
            nextEvent = self._getNextEvent()

            if nextEvent.kind == Event.Kind.order:
                self.orderEvents.append(nextEvent)
                self.runOrder(event=nextEvent)

            elif nextEvent.kind == Event.Kind.foodPrep:
                self.foodPrepEvents.append(nextEvent)
                self.runFoodPrep(event=nextEvent)

            elif nextEvent.kind == Event.Kind.courierArrival:
                self.courrierArrivalEvents.append(nextEvent)
                self.runCourierArrival(event=nextEvent)

            else:
                raise NotImplementedError

    def runCourierArrival(self, event):
        raise NotImplementedError

    def runFoodPrep(self, event):
        raise NotImplementedError

    def runOrder(self, event):
        self.orderEvents.append(event)

        self.extendEventsToRun((
            # food prep event associated with this order event
            Event(
                kind=Event.Kind.foodPrep,
                order=event.order,
                time=event.time + event.order["prepTime"],
            ),
            # courier arrival event associated with this order event
            Event(
                kind=Event.Kind.courierArrival,
                order=event.order,
                time=event.time + self._getEta(),
            ),
        ))

    def _getEta(self):
        if self._eta == None:
            return np.random.uniform(3, 15)
        else:
            return self._eta

    def _getNextEvent(self):
        return self._eventsToRun.pop()

    def loadSimOrders(self, fpath, _delta=.5):
        for i, order in enumerate(loadOrders(fpath)):
            self.addOrder(time=i*_delta, order=order)

class BaseDispatcher:
    def __init__(self, _eta=None):
        self.eventHistory = {key: [] for key in Event.Kind}

        self._eta = _eta
    def __init__(self, fname, eta=None):
        self.orders = loadOrders(fname=fname)

        self.starts = []
        self.dones = []
        self.arrivals = []
        self.pickups = []

        self._queue = [
            (0, "start", 0, self.inputArr["id"][0])
        ] if self.inputArr.shape[0] else []

class MatchedDispatcher(BaseDispatcher):
    def __init__(self, fname, eta=None):
        super().__init__(fname=fname, eta=eta)
        self.doneSet = set()
        self.arrivalSet = set()

    def runArrival(self, event):
        time, _, orderIx, orderId = event
        self.arrivals.append((time, orderIx, orderId))

        if orderId in self.doneSet:
            self.pickups.append((time, orderIx, orderId, orderId))
            self.doneSet.remove(orderId)
        else:
            self.arrivalSet.add(orderId)

    def runDone(self, event):
        time, _, orderIx, orderId = event
        self.dones.append((time, orderIx, orderId))

        if orderId in self.arrivalSet:
            self.pickups.append((time, orderIx, orderId, orderId))
            self.arrivalSet.remove(orderId)
        else:
            self.doneSet.add(orderId)


class FifoDispatcher(BaseDispatcher):
    def __init__(self, fname, eta=None):
        super().__init__(fname=fname, eta=eta)

        self.doneQueue = Queue()
        self.arrivalQueue = Queue()

    def runArrival(self, event):
        time, _, arrivalIx, arrivalId = event
        self.arrivals.append((time, arrivalIx, arrivalId))

        if not self.doneQueue.empty():
            _, _, doneIx, doneId = self.doneQueue.get(block=False)
            self.pickups.append((time, doneIx, arrivalIx, doneId, arrivalId))
        else:
            self.arrivalQueue.put(event, block=False)

    def runDone(self, event):
        time, _, doneIx, doneId = event
        self.dones.append((time, doneIx, doneId))

        if not self.arrivalQueue.empty():
            _, _, arrivalIx, arrivalId = self.arrivalQueue.get(block=False)
            self.pickups.append((time, doneIx, arrivalIx, doneId, arrivalId))
        else:
            self.doneQueue.put(event, block=False)