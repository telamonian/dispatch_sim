from abc import ABC
from dataclasses import dataclass

from .order import Order

__all__ = ["Event", "OrderEvent", "FoodPrepEvent", "CourierArrivalEvent", "PickupEvent", "eventClasses"]


@dataclass
class Event(ABC):
    """Base Event type that has fields for time and basic info about a single order
    """
    time: float
    order: Order


@dataclass
class OrderEvent(Event):
    """Event type that represents receiving an order
    """
    def __str__(self) -> str:
        return ("Order received\n"
                f"\ttime: {self.time:.3f} s\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


@dataclass
class FoodPrepEvent(Event):
    """Event type that represents the completion of food prep for an order
    """
    def __str__(self) -> str:
        return ("Food prep finished\n"
                f"\ttime: {self.time:.3f} s\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


@dataclass
class CourierArrivalEvent(Event):
    """Event type that represents the arrival of a courier dispatched in response to particular order
    """
    def __str__(self) -> str:
        return ("Courier arrived\n"
                f"\ttime: {self.time:.3f} s\n"
                f"\tdispatched for order id: {self.order.id}\n"
                f"\tdispatched for order name: {self.order.name}")


@dataclass
class PickupEvent(Event):
    """Event type that represents order pickup. Includes some extra info about the order's food prep
    and courier
    """
    foodPrepEvent: FoodPrepEvent
    courierArrivalEvent: CourierArrivalEvent

    def __str__(self) -> str:
        return ("Order picked up by courier\n"
                f"\ttime: {self.time:.3f} s\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}\n"
                f"\tfood wait time: {round(self.foodWaitTime*1e3)} ms\n"
                f"\tcourier wait time: {round(self.courierWaitTime*1e3)} ms")

    @property
    def courierWaitTime(self) -> float:
        """THe difference between the pickup time and the arrival time of the relevant courier
        """
        return self.time - self.courierArrivalEvent.time

    @property
    def foodWaitTime(self) -> float:
        """The difference between the pickup time and the food prep completion time of the relevant order
        """
        return self.time - self.foodPrepEvent.time

eventClasses = {
    "OrderEvent": OrderEvent,
    "FoodPrepEvent": FoodPrepEvent,
    "CourierArrivalEvent": CourierArrivalEvent,
    "PickupEvent": PickupEvent
}
