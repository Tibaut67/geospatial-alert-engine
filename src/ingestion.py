from src.models import HazardEvent
import requests


class USGSIngestionService:
    FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson" #REST endpoint
    def get_recent_hazards(self) -> list[HazardEvent]:
        response = requests.get(self.FEED_URL) #Sends HTTP GET request
        response.raise_for_status() #security measure against missing or broken data

        data = response.json() #parses data into dictionaries
        features = data.get("features", [])
        hazards = []

        for feature in features:
            coords = feature["geometry"]["coordinates"]
            props = feature["properties"]

            hazard = HazardEvent( #translates dictionaries into dataclass instances
                id=feature["id"],
                title=props.get("title","Unknown"),
                magnitude=float(props.get("mag") or 0.0),
                longitude=float(coords[0]),
                latitude=float(coords[1]),
                timestamp=int(props.get("time", 0)),
            )
        hazards.append(hazard)

        return hazards
