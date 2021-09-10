from dataclasses import dataclass
import json
import jsonschema

__all__ = ["Order", "loadOrders"]

orderSchema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "prepTime": {"type": "number"},
    },
}


@dataclass
class Order:
    id: str
    name: str
    prepTime: float

def loadOrders(fpath: str) -> list[Order]:
    with open(fpath) as blob:
        return [Order(**o) for o in json.load(blob) if jsonschema.validate(o, orderSchema)]