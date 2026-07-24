from typing import Optional
from pydantic import BaseModel
from enum import Enum

class SensorType(str, Enum):
    WATER = "WATER"
    FEED = "FEED"
    TEMPERATURE = "TEMPERATURE"
    HEATING = "HEATING"
    AIR_QUALITY = "AIR_QUALITY"
    EGG_COUNT = "EGG_COUNT"

class Sensor(BaseModel):
    id: str
    type: SensorType
    name: str
    unit: str
    current_value: float
    min_value: float = 0.0
    max_value: float = 100.0
    warning_threshold: float = 20.0
    is_online: bool = True
    last_seen: int = 0

class Coop(BaseModel):
    id: str
    name: str
    serial: str

class Subscription(BaseModel):
    tariff: str
    status: str
    expires_at: int