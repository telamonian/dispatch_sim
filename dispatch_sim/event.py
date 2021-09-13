from dataclasses import dataclass, field

from .order import Order

__all__ = ["Event", "OrderEvent", "FoodPrepEvent", "CourierArrivalEvent", "PickupEvent", "eventClasses"]


@dataclass
class Event:
    time: float
    order: Order


@dataclass
class OrderEvent(Event):
    def __repr__(self):
        return ("Order submitted\n"
                f"\ttime: {self.time:.3f} s\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


@dataclass
class FoodPrepEvent(Event):
    def __repr__(self):
        return ("Food prep finished\n"
                f"\ttime: {self.time:.3f} s\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


@dataclass
class CourierArrivalEvent(Event):
    def __repr__(self):
        return ("Courier arrived\n"
                f"\ttime: {self.time:.3f} s\n"
                f"\tdispatched for order id: {self.order.id}\n"
                f"\tdispatched for order name: {self.order.name}")


@dataclass
class PickupEvent(Event):
    foodPrepEvent: FoodPrepEvent
    courierArrivalEvent: CourierArrivalEvent

    def __repr__(self):
        return ("Order picked up by courier\n"
                f"\ttime: {self.time:.3f} s\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}\n"
                f"\tfood wait time: {round(self.foodWaitTime*1e3)} ms\n"
                f"\tcourier wait time: {round(self.courierWaitTime*1e3)} ms")

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
