import time
from src.models import Asset, HazardEvent
from src.spatial_engine import SpatialEngine
from src.alert_service import AlertService
from src.ingestion import USGSIngestionService

def run_benchmarks():
    engine = SpatialEngine()
    alerts = AlertService()
    ingestion = USGSIngestionService()

    # 1. Live USGS ingestion latency
    t0 = time.perf_counter()
    live_hazards = ingestion.get_recent_hazards()
    ingest_ms = (time.perf_counter() - t0) * 1000
    print(f"Live USGS Fetch: {len(live_hazards)} events parsed in {ingest_ms:.2f} ms")

    # 2. Spatial proximity evaluation throughput (1,000 assets x 1,000 events = 1,000,000 checks)
    assets = [
        Asset(id=f"A{i}", name=f"Site {i}", latitude=34.0 + (i % 50) * 0.1, longitude=-118.0 - (i % 50) * 0.1, radius_km=300.0)
        for i in range(1000)
    ]
    hazards = [
        HazardEvent(id=f"H{j}", title="Quake", magnitude=4.5, longitude=-118.5 + (j % 50) * 0.1, latitude=34.5 + (j % 50) * 0.1, timestamp=1700000000)
        for j in range(1000)
    ]

    t0 = time.perf_counter()
    matches = 0
    for a in assets:
        for h in hazards:
            if engine.is_hazard_within_radius(a, h):
                matches += 1
    total_sec = time.perf_counter() - t0
    checks = len(assets) * len(hazards)
    us_per_check = (total_sec / checks) * 1_000_000
    checks_per_sec = checks / total_sec
    print(f"Spatial Checks: {checks:,} evaluations in {total_sec:.3f}s ({us_per_check:.2f} us/check, {checks_per_sec:,.0f} checks/sec, {matches:,} matches)")

    # 3. Alert deduplication speed (100,000 duplicate lookups)
    sample_asset, sample_hazard = assets[0], hazards[0]
    alerts.dispatch_alert(sample_asset, sample_hazard)
    t0 = time.perf_counter()
    for _ in range(100_000):
        alerts.dispatch_alert(sample_asset, sample_hazard)
    dedup_ms = (time.perf_counter() - t0) * 1000
    print(f"Deduplication: 100,000 duplicate checks suppressed in {dedup_ms:.2f} ms")

if __name__ == "__main__":
    run_benchmarks()