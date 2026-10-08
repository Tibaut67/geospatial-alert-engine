from src.models import Asset
from src.models import HazardEvent


class AlertService:
    def __init__(self):
        self.sent_alerts = set()

    def dispatch_alert(self, asset: Asset, hazard: HazardEvent) -> bool:
        alert_key = (asset.id, hazard.id) #Compound key
        if alert_key in self.sent_alerts:
            return False
        else:
            self.sent_alerts.add(alert_key)
            print(f"[ALERT] {asset.name}: {hazard.title} at ({hazard.latitude}, {hazard.longitude})")
            return True
