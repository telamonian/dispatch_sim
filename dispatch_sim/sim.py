import json
import jsonschema
from operator import attrgetter

from dispatch_sim.dispatcher import MatchedDispatcher, FifoDispatcher
from dispatch_sim.event import OrderEvent, FoodPrepEvent, CourierArrivalEvent, PickupEvent

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

    return orders


class Sim:
    """delta: step size between input orders, in seconds"""


    def addOrder(self, time, order):
        self.extendEventsToRun((
            # food prep event associated with this order event
            OrderEvent(
                order=order,
                time=time,
            ),
        ))

    def extendEventsToRun(self, iterable):
        self._eventsToRun.extend(iterable)
        self._eventsToRun.sort(key=attrgetter("time"), reverse=True)


    def run(self):
        while self._eventsToRun:
            nextEvent = self._getNextEvent()

            if nextEvent.kind == BaseEvent.Kind.order:
                self.orderEvents.append(nextEvent)
                self.runOrder(event=nextEvent)

            elif nextEvent.kind == BaseEvent.Kind.foodPrep:
                self.foodPrepEvents.append(nextEvent)
                self.runFoodPrep(event=nextEvent)

            elif nextEvent.kind == BaseEvent.Kind.courierArrival:
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
            FoodPrepEvent(
                order=event.order,
                time=event.time + event.order["prepTime"],
            ),
            # courier arrival event associated with this order event
            CourierArrivalEvent(
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

