__all__ = ["OrderEvent", "FoodPrepEvent", "CourierArrivalEvent", "PickupEvent"]

class BaseEvent:
    def __init__(self, *, order, time):
        # the originating order (ie a dict containing {id, name, prepTime}) associated with this event
        self.order = order

        # the simulation time at which the event occurs
        self.time = time


class OrderEvent(BaseEvent):
    def __repr__(self):
        return ("Order submitted\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


class FoodPrepEvent(BaseEvent):
    def __repr__(self):
        return ("Food prep finished\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}")


class CourierArrivalEvent(BaseEvent):
    def __repr__(self):
        return ("Courier arrived\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tdispatched for order id: {self.order.id}\n"
                f"\tdispatched for order name: {self.order.name}")


class PickupEvent(BaseEvent):
    def __init__(self, *, courierArrivalEvent, foodPrepEvent, **kwargs):
        super().__init__(**kwargs)

        self.foodPrepEvent = foodPrepEvent
        self.courierArrivalEvent = courierArrivalEvent

    def __repr__(self):
        return ("Order picked up by courier\n"
                f"\ttime: {self.time:.4f}\n"
                f"\tid: {self.order.id}\n"
                f"\tname: {self.order.name}"
                f"\tfood wait time: {self.foodWaitTime():.4f}\n"
                f"\tcourier wait time: {self.courierWaitTime():.4f}")

    def courierWaitTime(self):
        return self.time - self.courierArrivalEvent.time

    def foodWaitTime(self):
        return self.time - self.foodPrepEvent.time