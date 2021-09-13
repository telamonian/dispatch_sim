import argparse
import numpy as np
from os import PathLike
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
    _eventQueue: PriorityQueue[tuple[float, int, Event]]
    _eta: Optional[float]
    _realtime: bool

    def __init__(self, fifo: bool=False, timestamp: bool=False, _eta: Optional[float]=None, _realtime: bool=True):
        self._dispatcher = FifoDispatcher(timestamp=timestamp) if fifo else MatchedDispatcher(timestamp=timestamp)
        self._eventCount = 0
        self._eventQueue = PriorityQueue()

        self._eta = _eta
        self._realtime = _realtime

    def addOrder(self, order: Order, time: float):
        self._putEvent(
            # food prep event associated with this order event
            OrderEvent(
                order=order,
                time=time,
            ),
        )

    def addOrdersFromFile(self, fpath: PathLike, t0: float=0, tdelta: float=.5):
        for i, order in enumerate(loadOrders(fpath)):
            self.addOrder(order, t0 + i*tdelta)

    def run(self):
        t0 = time.time()
        while not self._eventQueue.empty():
            nextEvent = self._getEvent()

            if self._realtime:
                # implement the real time behavior via timeout
                now = time.time() - t0
                while nextEvent.time > now:
                    time.sleep(nextEvent.time - now)
                    now = time.time() - t0

            if isinstance(nextEvent, OrderEvent):
                postOrderInfo = self._dispatcher.doOrder(event=nextEvent)
                self._simulateOrderFollowup(postOrderInfo)

            elif isinstance(nextEvent, FoodPrepEvent):
                prePickupInfo = self._dispatcher.doFoodPrep(event=nextEvent)
                if prePickupInfo is not None:
                    self._simulatePickup(*prePickupInfo)

            elif isinstance(nextEvent, CourierArrivalEvent):
                prePickupInfo = self._dispatcher.doCourierArrival(event=nextEvent)
                if prePickupInfo is not None:
                    self._simulatePickup(*prePickupInfo)

            elif isinstance(nextEvent, PickupEvent):
                self._dispatcher.doPickup(event=nextEvent)

            else:
                raise NotImplementedError

        # print final stat summary message
        print(self._dispatcher, end="\n\n")

    def _getEta(self):
        if self._eta is None:
            return np.random.uniform(3, 15)
        else:
            return self._eta

    def _getEvent(self) -> Event:
        """Fetch the next event from the event queue, discarding the tuple entries used
        for sorting
        """
        _, _, event = self._eventQueue.get()
        return event

    def _putEvent(self, event: Event):
        """Add an event to this Sim instance's event queue as a (eventTime, eventCount, event) triple. Storing objects
        as triples in a priority queue is a common approach that has several advantages (avoids object comparison,
        ensures stability in case of equal priority, etc). See: https://docs.python.org/3/library/heapq.html
        """
        self._eventQueue.put((event.time, self._eventCount, event))
        self._eventCount += 1

    def _simulateOrderFollowup(self, event: Event):
        self._putEvent(
            # food prep event associated with this order event
            FoodPrepEvent(
                order=event.order,
                time=event.time + event.order.prepTime,
            )
        )
        self._putEvent(
            # courier arrival event associated with this order event
            CourierArrivalEvent(
                order=event.order,
                time=event.time + self._getEta(),
            )
        )

    def _simulatePickup(self, foodPrepEvent: FoodPrepEvent, courierArrivalEvent: CourierArrivalEvent):
        self._putEvent(
            # courier arrival event associated with this order event
            PickupEvent(
                order=foodPrepEvent.order,
                time=max(foodPrepEvent.time, courierArrivalEvent.time),
                foodPrepEvent=foodPrepEvent,
                courierArrivalEvent=courierArrivalEvent,
            )
        )


def main():
    parser = argparse.ArgumentParser(description="Simple order-dispatch real-time simulation script")
    parser.add_argument("--eta", default=None, type=int,
        help="if set to a float value, the Sim will use it as the time in between courier dispatch and arrival")
    parser.add_argument("--discrete", action="store_true", default=False,
        help="if set, do a discrete time Sim; all inter-event waiting times are ignored")
    parser.add_argument("--fifo", action="store_true", default=False,
        help="if set, use fifo algorithm for courier dispatch, in place of default matching algorithm")
    parser.add_argument("--fpath", default=HERE/"data"/"dispatch_orders.json",
        help="path to input file containing orders in json format, as per the schema in the spec")
    parser.add_argument("--timestamp", action="store_true", default=False,
        help="if set, prepend timestamp (in wall clock seconds since simulation start) to all event messages")

    kwargs = vars(parser.parse_args())

    sim = Sim(
        fifo=kwargs["fifo"],
        timestamp=kwargs["timestamp"],
        _eta=kwargs["eta"],
        _realtime=(not kwargs["discrete"]),
    )

    sim.addOrdersFromFile(kwargs["fpath"])
    sim.run()


if __name__ == "__main__":
    main()
