from dataclasses import dataclass
import json
import jsonschema
from os import PathLike

__all__ = ["Order", "loadOrders"]

"""JSON schema of an order, as defined in the exercise spec. Used for validation
"""
_orderSchema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "prepTime": {"type": "number"},
    },
    "required": ["id", "name", "prepTime"],
    "additionalProperties": False
}


@dataclass
class Order:
    """Dataclass with equivalent fields to those of the json representation of an order
    """
    id: str
    name: str
    prepTime: float

def loadOrders(fpath: PathLike) -> list[Order]:
    """Load a list of orders from a json file as a list of Order instances
    """
    with open(fpath) as blob:
        return [Order(**o) for o in json.load(blob) if jsonschema.validate(o, _orderSchema) is None]
