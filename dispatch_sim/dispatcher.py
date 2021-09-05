__all__ = ["MatchedDispatcer", "FifoDispatcher"]

class BaseDispatcher:
    def __init__(self, _eta=None):
        self.eventHistory = {key: [] for key in BaseEvent.Kind}

        self._eta = _eta

        self.starts = []
        self.dones = []
        self.arrivals = []
        self.pickups = []

        self._queue = [
            (0, "start", 0, self.inputArr["id"][0])
        ] if self.inputArr.shape[0] else []

class MatchedDispatcher(BaseDispatcher):
    def __init__(self, fname, eta=None):
        super().__init__(fname=fname, eta=eta)
        self.doneSet = set()
        self.arrivalSet = set()

    def runArrival(self, event):
        time, _, orderIx, orderId = event
        self.arrivals.append((time, orderIx, orderId))

        if orderId in self.doneSet:
            self.pickups.append((time, orderIx, orderId, orderId))
            self.doneSet.remove(orderId)
        else:
            self.arrivalSet.add(orderId)

    def runDone(self, event):
        time, _, orderIx, orderId = event
        self.dones.append((time, orderIx, orderId))

        if orderId in self.arrivalSet:
            self.pickups.append((time, orderIx, orderId, orderId))
            self.arrivalSet.remove(orderId)
        else:
            self.doneSet.add(orderId)


class FifoDispatcher(BaseDispatcher):
    def __init__(self, fname, eta=None):
        super().__init__(fname=fname, eta=eta)

        self.doneQueue = Queue()
        self.arrivalQueue = Queue()

    def runArrival(self, event):
        time, _, arrivalIx, arrivalId = event
        self.arrivals.append((time, arrivalIx, arrivalId))

        if not self.doneQueue.empty():
            _, _, doneIx, doneId = self.doneQueue.get(block=False)
            self.pickups.append((time, doneIx, arrivalIx, doneId, arrivalId))
        else:
            self.arrivalQueue.put(event, block=False)

    def runDone(self, event):
        time, _, doneIx, doneId = event
        self.dones.append((time, doneIx, doneId))

        if not self.arrivalQueue.empty():
            _, _, arrivalIx, arrivalId = self.arrivalQueue.get(block=False)
            self.pickups.append((time, doneIx, arrivalIx, doneId, arrivalId))
        else:
            self.doneQueue.put(event, block=False)