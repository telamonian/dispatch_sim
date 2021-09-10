import argparse
import numpy as np
from pathlib import Path
from queue import PriorityQueue
import time
from typing import Optional, Union

from dispatch_sim.dispatcher import MatchedDispatcher, FifoDispatcher
from dispatch_sim.event import Event, OrderEvent, FoodPrepEvent, CourierArrivalEvent, PickupEvent
from dispatch_sim.order import loadOrders, Order

HERE = Path(__file__).resolve().parent


class Sim:
    _dispatcher: Union[MatchedDispatcher, FifoDispatcher]
    _eventCount: int
    _eventQueue: PriorityQueue[tuple[int, Event]]
    _eta: Optional[float]
    _realtime: bool

    def __init__(self, fifo: bool=False, _eta: Optional[float]=None):
        self._dispatcher = FifoDispatcher() if fifo else MatchedDispatcher()
        self._eventCount = 0
        self._eventQueue = PriorityQueue()

        # if _eta is set, trigger "test mode" by also setting _relatime to False
        self._eta = _eta
        self._realtime = _eta is None

    def getEvent(self) -> Event:
        """Fetch the next event from the event queue, discarding the entry count
        """
        _, event = self._eventQueue.get()
        return event

    def putEvent(self, event: Event):
        """Add an event to this Sim instance's event queue. For stability in case of tie
        Elements in the queue are implemented as (cnt, event) pairs, where cnt is the entry count
        """
        self._eventQueue.put((self._eventCount, event))
        self._eventCount += 1

    def addOrder(self, order: Order, time: float):
        self.putEvent(
            # food prep event associated with this order event
            OrderEvent(
                order=order,
                time=time,
            ),
        )

    def addOrdersFromFile(self, fpath: str, t0: float=0, tdelta: float=.5):
        for i, order in enumerate(loadOrders(fpath)):
            self.addOrder(order, t0 + i*tdelta)

    def run(self):
        t0 = time.time()
        while self._eventQueue.not_empty:
            nextEvent = self.getEvent()

            if self._realtime:
                # implement the real time behavior via timeout
                now = time.time() - t0
                time.sleep(nextEvent.time - now)

            if isinstance(nextEvent, OrderEvent):
                postOrderInfo = self._dispatcher.doOrder(event=nextEvent)
                self.simulateOrderFollowup(postOrderInfo)

            elif isinstance(nextEvent, FoodPrepEvent):
                prePickupInfo = self._dispatcher.doFoodPrep(event=nextEvent)
                if prePickupInfo is not None:
                    self.simulatePickup(*prePickupInfo)

            elif isinstance(nextEvent, CourierArrivalEvent):
                prePickupInfo = self._dispatcher.doCourierArrival(event=nextEvent)
                if prePickupInfo is not None:
                    self.simulatePickup(*prePickupInfo)

            if isinstance(nextEvent, PickupEvent):
                self._dispatcher.doPickup(event=nextEvent)

            else:
                raise NotImplementedError

    def simulateOrderFollowup(self, event: Event):
        self.putEvent(
            # food prep event associated with this order event
            FoodPrepEvent(
                order=event.order,
                time=event.time + event.order.prepTime,
            )
        )
        self.putEvent(
            # courier arrival event associated with this order event
            CourierArrivalEvent(
                order=event.order,
                time=event.time + self._getEta(),
            )
        )

    def simulatePickup(self, foodPrepEvent: FoodPrepEvent, courierArrivalEvent: CourierArrivalEvent):
        self.putEvent(
            # courier arrival event associated with this order event
            PickupEvent(
                order=foodPrepEvent.order,
                time=max(foodPrepEvent.time, courierArrivalEvent.time),
                foodPrepEvent=foodPrepEvent,
                courierArrivalEvent=courierArrivalEvent,
            )
        )

    def _getEta(self):
        if self._eta is None:
            return np.random.uniform(3, 15)
        else:
            return self._eta


def main():
    parser = argparse.ArgumentParser(description="Simple order-dispatch real-time simulation script")
    parser.add_argument("--fifo", action="store_true", default=False,
                        help="if set, use fifo algorithm for courier dispatch, in place of default matching algorithm")
    parser.add_argument("--fpath", default=HERE/"data"/"dispatch_orders.json",
                        help="path to input file containing orders in json format, as per the schema in the spec")
    parser.add_argument("--eta", default=None,
                        help="if set to a float value, the Sim will run in 'test mode'; all random values are set to "
                             "the option value, and all wait times in between events are ignored")

    args = vars(parser.parse_args())
    fifo = args["fifo"]
    fpath = args["fpath"]
    _eta = args["eta"]

    sim = Sim(fifo=fifo, _eta=_eta)
    sim.addOrdersFromFile(fpath)
    sim.run()


if __name__ == "__main__":
    main()