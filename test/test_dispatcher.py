from operator import attrgetter

from dispatch_sim.dispatcher import MatchedDispatcher, FifoDispatcher
from dispatch_sim.event import OrderEvent, FoodPrepEvent, CourierArrivalEvent, PickupEvent

# reuse the literal set of Order instances that gets verified by TestOrder
from .test_order import TestOrder as _TestOrder
orders = [*_TestOrder.realOrders]

class _TestDispatcher:
    realOrderEvent = OrderEvent(17.5, orders[0])
    realPickupEvent = PickupEvent(
        26.5,
        orders[0],
        FoodPrepEvent(21.5, orders[0]),
        CourierArrivalEvent(26.5, orders[0]),
    )

    realFoodPrepEvents = [
        FoodPrepEvent(20.5, orders[2]),
        FoodPrepEvent(21.5, orders[0]),
        FoodPrepEvent(41, orders[1]),
    ]
    realCourierArrivalEvents = [
        CourierArrivalEvent(26.5, orders[0]),
        CourierArrivalEvent(27, orders[1]),
        CourierArrivalEvent(27.5, orders[2]),
    ]

    def test_doOrder(self):
        testOrderEvent = self.dispatcher.doOrder(self.realOrderEvent)

        assert self.realOrderEvent == testOrderEvent
        assert self.realOrderEvent == self.dispatcher.history["OrderEvent"][0]

    def test_doPickup(self):
        self.dispatcher.doPickup(self.realPickupEvent)

        assert self.realPickupEvent == self.dispatcher.history["PickupEvent"][0]

    def test_doFoodPrep_and_doCourierArrival(self):
        events = [*self.realFoodPrepEvents, *self.realCourierArrivalEvents]
        events.sort(key=attrgetter("time"))

        testPickupInfoPairs = [
            (self.dispatcher.doFoodPrep if isinstance(event, FoodPrepEvent) else self.dispatcher.doCourierArrival)(event) for event in events
        ]

        assert self.realPickupInfoPairs == testPickupInfoPairs
        assert self.realFoodPrepEvents == self.dispatcher.history["FoodPrepEvent"]
        assert self.realCourierArrivalEvents == self.dispatcher.history["CourierArrivalEvent"]

class TestMatchedDispatcher(_TestDispatcher):
    realPickupInfoPairs = [
        None,
        None,
        (FoodPrepEvent(21.5, orders[0]), CourierArrivalEvent(26.5, orders[0])),
        None,
        (FoodPrepEvent(20.5, orders[2]), CourierArrivalEvent(27.5, orders[2])),
        (FoodPrepEvent(41, orders[1]), CourierArrivalEvent(27, orders[1])),
    ]

    def setup_method(self, test_method):
        self.dispatcher = MatchedDispatcher()

class TestFifoDispatcher(_TestDispatcher):
    realPickupInfoPairs = [
        None,
        None,
        (FoodPrepEvent(20.5, orders[2]), CourierArrivalEvent(26.5, orders[0])),
        (FoodPrepEvent(21.5, orders[0]), CourierArrivalEvent(27, orders[1])),
        None,
        (FoodPrepEvent(41, orders[1]), CourierArrivalEvent(27.5, orders[2])),
    ]

    def setup_method(self, test_method):
        self.dispatcher = FifoDispatcher()
