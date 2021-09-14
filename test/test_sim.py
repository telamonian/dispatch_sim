from pathlib import Path

from dispatch_sim.event import OrderEvent
from dispatch_sim.order import Order
from dispatch_sim.sim import Sim

# reuse the literal set of Order instances that gets verified by TestOrder
from .test_order import TestOrder as _TestOrder
orders = [*_TestOrder.realOrders]

HERE = Path(__file__).resolve().parent


class TestSim:
    fpath = _TestOrder.fpath

    realTriples = [
        (
            17.5,
            0,
            OrderEvent(17.5, orders[0]),
        ),
        (
            18.0,
            1,
            OrderEvent(18.0, orders[1]),
        ),
        (
            18.5,
            2,
            OrderEvent(18.5, orders[2]),
        ),
    ]

    def setup_method(self, test_method):
        self.sim = Sim()

    def test_addOrder(self):
        self.sim.addOrder(orders[0], 17.5)
        self.sim.addOrder(orders[1], 18.0)
        self.sim.addOrder(orders[2], 18.5)
        testTriples = self.sim._eventQueue.queue

        assert self.realTriples == testTriples

    def test_addOrdersFromFile(self):
        self.sim.addOrdersFromFile(_TestOrder.fpath, t0=17.5, tdelta=.5)
        testTriples = self.sim._eventQueue.queue

        assert self.realTriples == testTriples

