from dataclasses import dataclass, field

from .order import Order

__all__ = ["Event", "OrderEvent", "FoodPrepEvent", "CourierArrivalEvent", "PickupEvent", "eventClasses"]


@dataclass(order=True)
class Event:
    time: float
    order: Order=field(compare=False)


@dataclass
class OrderEvent(Event):
    def __repr__(self):
        return ("Order submitted\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


@dataclass
class FoodPrepEvent(Event):
    def __repr__(self):
        return ("Food prep finished\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


@dataclass
class CourierArrivalEvent(Event):
    def __repr__(self):
        return ("Courier arrived\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tdispatched for order id: {self.order.id}\n"
                f"\tdispatched for order name: {self.order.name}")


@dataclass
class PickupEvent(Event):
    foodPrepEvent: FoodPrepEvent=field(compare=False)
    courierArrivalEvent: CourierArrivalEvent=field(compare=False)

    def __repr__(self):
        return ("Order picked up by courier\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}"
                f"\tfood wait time: {self.foodWaitTime:.4f}\n"
                f"\tcourier wait time: {self.courierWaitTime:.4f}")

    @property
    def courierWaitTime(self):
        return self.time - self.courierArrivalEvent.time

    @property
    def foodWaitTime(self):
        return self.time - self.foodPrepEvent.time

eventClasses = {
    "OrderEvent": OrderEvent,
    "FoodPrepEvent": FoodPrepEvent,
    "CourierArrivalEvent": CourierArrivalEvent,
    "PickupEvent": PickupEvent
}
