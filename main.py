from src.models import Asset
from src.ingestion import USGSIngestionService
from src.spatial_engine import SpatialEngine
from src.alert_service import AlertService

def main():
    assets = [ #Monitored locations with ranges
        Asset(id="1", name="Anchorage Hub", latitude=61.2181, longitude=-149.9003, radius_km=300.0),
        Asset(id="2", name="Los Angeles Center", latitude=34.0522, longitude=-118.2437, radius_km=300.0),
        Asset(id="3", name="Tokyo Facility", latitude=35.6762, longitude=139.6503, radius_km=400.0),
    ]
    ingestion_service = USGSIngestionService() #Instantiates the network ingestion client to poll external REST endpoints
    spatial_engine = SpatialEngine() #Instantiates the geometric compute engine responsible for GIS calculations
    alert_service = AlertService() #Instantiates the business logic service that handles dispatching and deduplication

    print("Fetching active hazard events...")
    hazards = ingestion_service.get_recent_hazards()
    print(f"Retrieved {len(hazards)} hazards. Evaluating proximity...\n")

    #Cross-evaluates every incoming seismic event against every registered asset
    for asset in assets:
        for hazard in hazards:
            if spatial_engine.is_hazard_within_radius(asset, hazard):
                alert_service.dispatch_alert(asset, hazard)

if __name__ == "__main__":
    main()
