from pathlib import Path

from dispatch_sim.dispatcher import Dispatcher, MatchedDispatcher, FifoDispatcher
from dispatch_sim.event import OrderEvent, FoodPrepEvent, CourierArrivalEvent, PickupEvent

# reuse the literal set of Order instances that gets verified by TestOrder
from .test_order import TestOrder as _TestOrder
orders = [*_TestOrder.realOrders]

HERE = Path(__file__).resolve().parent

class TestDispatcher:
    realOrderEvent = OrderEvent(17.5, orders[0])
    realFoodPrepEvent = FoodPrepEvent(21.5, orders[0])
    realCourierArrivalEvent = CourierArrivalEvent(26.5, orders[0])
    realPickupEvent = PickupEvent(
        26.5,
        orders[0],
        FoodPrepEvent(21.5, orders[0]),
        CourierArrivalEvent(26.5, orders[0]),
    )

    def setup_method(self, test_method):
        self.dispatcher = Dispatcher()

    def test_doOrder(self):
        testOrderEvent = self.dispatcher.doOrder(self.realOrderEvent)

        assert self.realOrderEvent == testOrderEvent
        assert self.realOrderEvent == self.dispatcher.history["OrderEvent"][0]

    # def doFoodPrep(self, event: FoodPrepEvent) -> _PrePickupInfo:
    #     raise NotImplementedError

    # def doCourierArrival(self, event: CourierArrivalEvent) -> _PrePickupInfo:
    #     raise NotImplementedError

    # def doPickup(self, event: PickupEvent):
    #     self._addToHistory(event)
