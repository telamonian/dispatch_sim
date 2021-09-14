from pathlib import Path

from dispatch_sim.event import OrderEvent
from dispatch_sim.sim import Sim

# reuse the literal set of Order instances that gets verified by TestOrder
from .test_order import TestOrder as _TestOrder
orders = [*_TestOrder.realOrders]

HERE = Path(__file__).resolve().parent
ordersFpath = HERE / "data" / "dispatch_orders.json"

class TestSim:
    realSimLog = "Order received\n\ttime: 17.500 s\n\tid: a8cfcb76-7f24-4420-a5ba-d46dd77bdffd\n\tname: Banana Split\n\nOrder received\n\ttime: 18.000 s\n\tid: 58e9b5fe-3fde-4a27-8e98-682e58a4a65d\n\tname: McFlury\n\nOrder received\n\ttime: 18.500 s\n\tid: 2ec069e3-576f-48eb-869f-74a540ef840c\n\tname: Acai Bowl\n\nFood prep finished\n\ttime: 20.500 s\n\tid: 2ec069e3-576f-48eb-869f-74a540ef840c\n\tname: Acai Bowl\n\nFood prep finished\n\ttime: 21.500 s\n\tid: a8cfcb76-7f24-4420-a5ba-d46dd77bdffd\n\tname: Banana Split\n\nCourier arrived\n\ttime: 26.500 s\n\tdispatched for order id: a8cfcb76-7f24-4420-a5ba-d46dd77bdffd\n\tdispatched for order name: Banana Split\n\nOrder picked up by courier\n\ttime: 26.500 s\n\tid: 2ec069e3-576f-48eb-869f-74a540ef840c\n\tname: Acai Bowl\n\tfood wait time: 6000 ms\n\tcourier wait time: 0 ms\n\nCourier arrived\n\ttime: 27.000 s\n\tdispatched for order id: 58e9b5fe-3fde-4a27-8e98-682e58a4a65d\n\tdispatched for order name: McFlury\n\nOrder picked up by courier\n\ttime: 27.000 s\n\tid: a8cfcb76-7f24-4420-a5ba-d46dd77bdffd\n\tname: Banana Split\n\tfood wait time: 5500 ms\n\tcourier wait time: 0 ms\n\nCourier arrived\n\ttime: 27.500 s\n\tdispatched for order id: 2ec069e3-576f-48eb-869f-74a540ef840c\n\tdispatched for order name: Acai Bowl\n\nFood prep finished\n\ttime: 41.000 s\n\tid: 58e9b5fe-3fde-4a27-8e98-682e58a4a65d\n\tname: McFlury\n\nOrder picked up by courier\n\ttime: 41.000 s\n\tid: 58e9b5fe-3fde-4a27-8e98-682e58a4a65d\n\tname: McFlury\n\tfood wait time: 0 ms\n\tcourier wait time: 13500 ms\n\nMean food wait time: 3833 ms\nMean courier wait time: 4500 ms\n\n"

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
        self.sim = Sim(
            fifo=True,
            _eta=9,
            _realtime=False,
        )

    def test_addOrder(self):
        self.sim.addOrder(orders[0], 17.5)
        self.sim.addOrder(orders[1], 18.0)
        self.sim.addOrder(orders[2], 18.5)
        testTriples = self.sim._eventQueue.queue

        assert self.realTriples == testTriples

    def test_addOrdersFromFile(self):
        self.sim.addOrdersFromFile(ordersFpath, t0=17.5, tdelta=.5)
        testTriples = self.sim._eventQueue.queue

        assert self.realTriples == testTriples

    def test_run(self, capsys):
        self.sim.addOrdersFromFile(ordersFpath, t0=17.5, tdelta=.5)
        self.sim.run()
        testSimLog, testSimErr = capsys.readouterr()

        assert self.realSimLog == testSimLog
