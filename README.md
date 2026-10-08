# Real-Time Geospatial Hazard Alert Engine

A lightweight Python backend service that continuously ingests seismic activity data from the USGS REST API and evaluates geographic proximity against monitored business assets.

## Architecture

- **`src/models.py`**: Domain models (`Asset`, `HazardEvent`) defined with Python dataclasses.
- **`src/ingestion.py`**: Ingestion client for real-time USGS GeoJSON earthquake feed.
- **`src/spatial_engine.py`**: Proximity engine utilizing great-circle Haversine distance over WGS84 coordinates (EPSG:4326) and normalized Esri geometry representations.
- **`src/alert_service.py`**: State-aware alert dispatcher featuring $O(1)$ compound-key deduplication.
- **`main.py`**: Orchestration pipeline evaluating $O(N \times M)$ asset-hazard proximity.

## Setup & Running

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py