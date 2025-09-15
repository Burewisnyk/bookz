from enum import Enum


class BookStatus(Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"
    LOST = "lost"
    DECOMMISSIONED = "decommissioned"
    UNKNOWN = "unknown"


class BookStatement(Enum):
    NEW = "new"
    GOOD = "good"
    DAMAGED = "damaged"
    REPAIR = "repair"
    UNUSABLE = "unusable"


class PlacementStatus(Enum):
    OCCUPIED = "occupied"
    FREE = "free"
    RESERVED = "reserved"