from database import insert_alert, get_metrics_summary
from settings import get_settings


async def check_alerts(call: dict, broadcast_fn):
    settings = get_settings()
    alerts_fired = []

    if call.get("latency_ms", 0) > settings.latency_alert_ms:
        alert = {
            "type": "HIGH_LATENCY",
            "message": f"Call latency {call['latency_ms']:.0f}ms exceeded threshold {settings.latency_alert_ms:.0f}ms",
            "severity": "warning",
            "value": call["latency_ms"],
            "threshold": settings.latency_alert_ms,
        }
        await insert_alert(alert)
        await broadcast_fn({"event": "alert", "alert": alert})
        alerts_fired.append(alert)

    if not call.get("success", True):
        alert = {
            "type": "CALL_FAILED",
            "message": f"AI call failed: {call.get('error', 'Unknown error')[:100]}",
            "severity": "error",
            "value": 1,
            "threshold": 0,
        }
        await insert_alert(alert)
        await broadcast_fn({"event": "alert", "alert": alert})
        alerts_fired.append(alert)

    summary = await get_metrics_summary()
    if summary["total_cost_usd"] > settings.daily_cost_alert_usd:
        alert = {
            "type": "COST_THRESHOLD",
            "message": f"Cumulative cost ${summary['total_cost_usd']:.4f} exceeded ${settings.daily_cost_alert_usd:.2f}",
            "severity": "warning",
            "value": summary["total_cost_usd"],
            "threshold": settings.daily_cost_alert_usd,
        }
        await insert_alert(alert)
        await broadcast_fn({"event": "alert", "alert": alert})
        alerts_fired.append(alert)

    return alerts_fired
