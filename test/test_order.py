from dispatch_sim.order import loadOrders, Order
from pathlib import Path

HERE = Path(__file__).resolve().parent

class TestOrder:
    fpath = HERE / "data" / "dispatch_orders.json"

    realOrders = [
        Order(
            id="a8cfcb76-7f24-4420-a5ba-d46dd77bdffd",
            name="Banana Split",
            prepTime=4,
        ),
        Order(
            id="58e9b5fe-3fde-4a27-8e98-682e58a4a65d",
            name="McFlury",
            prepTime=23,
        ),
        Order(
            id="2ec069e3-576f-48eb-869f-74a540ef840c",
            name="Acai Bowl",
            prepTime= 2,
        ),
    ]

    def test_loadOrders(self):
        testOrders = loadOrders(self.fpath)

        # assert all(real == test for real, test in zip(self.realOrders, testOrders))
        assert self.realOrders == testOrders
