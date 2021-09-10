from dataclasses import dataclass, field

from .order import Order

__all__ = ["OrderEvent", "FoodPrepEvent", "CourierArrivalEvent", "PickupEvent"]


@dataclass
class BaseEvent:
    time: float
    order: Order=field(order=False)


@dataclass
class OrderEvent(BaseEvent):
    def __repr__(self):
        return ("Order submitted\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


@dataclass
class FoodPrepEvent(BaseEvent):
    def __repr__(self):
        return ("Food prep finished\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


@dataclass
class CourierArrivalEvent(BaseEvent):
    def __repr__(self):
        return ("Courier arrived\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tdispatched for order id: {self.order.id}\n"
                f"\tdispatched for order name: {self.order.name}")


@dataclass
class PickupEvent(BaseEvent):
    foodPrepEvent: FoodPrepEvent=field(order=False)
    courierArrivalEvent: CourierArrivalEvent=field(order=False)

    def __repr__(self):
        return ("Order picked up by courier\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}"
                f"\tfood wait time: {self.foodWaitTime():.4f}\n"
                f"\tcourier wait time: {self.courierWaitTime():.4f}")

    @property
    def courierWaitTime(self):
        return self.time - self.courierArrivalEvent.time

    @property
    def foodWaitTime(self):
        return self.time - self.foodPrepEvent.time
