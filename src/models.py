from dataclasses import dataclass #builds constructors

@dataclass
class Asset:
        id: str
        name: str
        latitude: float
        longitude: float
        radius_km: float

@dataclass
class HazardEvent:
    id:str
    title:str
    magnitude:float
    longitude:float
    latitude:float
    timestamp:int




