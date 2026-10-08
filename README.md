# Real-Time Geospatial Hazard Alert Engine

A lightweight Python microservice that continuously ingests seismic activity from the USGS REST API and evaluates geographic proximity against monitored business facilities using geodesic spatial calculations.

## Overview

External cloud GIS geoprocessing calls often introduce network latency, authentication requirements, and rate limits that hinder real-time streaming pipelines. This engine implements an offline geospatial pipeline that:
- Ingests real-time seismic feeds from the USGS GeoJSON endpoints.
- Normalizes external payloads into strongly typed domain models.
- Calculates true great-circle distance over the WGS84 ellipsoid via the Haversine formula.
- Dispatches proximity alerts using an in-memory compound-key state tracker to eliminate duplicate notifications.

## Architecture & Module Breakdown

- `src/models.py`: Domain entities (`Asset`, `HazardEvent`) modeled with Python dataclasses to enforce clean boundaries between external JSON schemas and internal logic.
- `src/ingestion.py`: HTTP client that polls and parses USGS GeoJSON earthquake feeds.
- `src/spatial_engine.py`: Proximity math engine implementing great-circle distance over WGS84 coordinates (EPSG:4326), bypassing cloud GIS dependencies.
- `src/alert_service.py`: State-aware dispatcher maintaining an in-memory hash set of composite `(asset_id, hazard_id)` keys to achieve $O(1)$ alert deduplication.
- `main.py`: Main orchestration pipeline executing proximity checks across monitored facilities.

## Algorithmic & Design Decisions

### Local Geodesy vs. Cloud Buffering
Euclidean distance ($d = \sqrt{\Delta x^2 + \Delta y^2}$) introduces severe distortion on spherical coordinates. Instead of making synchronous REST calls to cloud GIS buffer tools, geodesic proximity is resolved locally via the Haversine formula:

$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$

This delivers sub-millisecond proximity checks with zero cloud service dependencies or credentials.

### $O(1)$ Alert Deduplication
To prevent alert fatigue in recurring poll loops, the alert engine tracks historical alerts using a compound key `(asset.id, hazard.id)`. Scoping by event and asset allows:
- A single earthquake to alert multiple distinct facilities.
- A facility to trigger alerts for distinct events.
- $O(1)$ lookup time per pair, avoiding $O(N)$ linear scans through previous alert histories.

### Scaling & Bottleneck Considerations
- **Current Complexity:** The evaluation loop compares $N$ assets against $M$ hazards, resulting in an $O(N \times M)$ brute-force sweep.
- **Production Path:** For large-scale asset monitoring ($N > 10^4$), the nested loop can be optimized to $O(M \log N)$ by indexing asset coordinates with a spatial tree structure (such as an R-tree or Quadtree) or delegating spatial indexing to PostGIS using `ST_DWithin`.

## Example Output

```text
[POLL] Fetching live seismic data from USGS...
[INGEST] Retrieved 42 seismic events.
[EVAL] Checking 3 monitored assets against hazard zones...

[ALERT DISPATCHED] Asset 'Redlands HQ' within 12.4 km of M4.2 Earthquake (ID: us7000abcd)
[ALERT DISPATCHED] Asset 'San Bernardino Facility' within 28.1 km of M4.2 Earthquake (ID: us7000abcd)
[SKIP] Duplicate alert suppressed for (Asset: Redlands HQ, Hazard: us7000abcd)