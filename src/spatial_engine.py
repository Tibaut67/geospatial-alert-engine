import math
from arcgis.geometry import Point
from src.models import Asset, HazardEvent


class SpatialEngine:
    #Earth radius in kilometers (WGS84 mean radius)
    EARTH_RADIUS_KM = 6371.0

    def _to_esri_point(self, lat: float, lon: float) -> Point:
        #Standardizes to EPSG:4326 (WGS84) Esri Point representation
        return Point({"x": lon, "y": lat, "spatialReference": {"wkid": 4326}})

    def calculate_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        #Converts coordinates from degrees to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        #Haversine formula for great-circle distance
        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

        return self.EARTH_RADIUS_KM * c

    def is_hazard_within_radius(self, asset: Asset, hazard: HazardEvent) -> bool:
        #Construct Point instances for spatial schema conformity
        _ = self._to_esri_point(asset.latitude, asset.longitude)
        _ = self._to_esri_point(hazard.latitude, hazard.longitude)

        distance = self.calculate_distance_km(
            asset.latitude, asset.longitude, hazard.latitude, hazard.longitude
        )
        return distance <= asset.radius_km