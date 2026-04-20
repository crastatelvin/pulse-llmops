import json
from datetime import datetime
import aiosqlite
from settings import get_settings


def _db_path() -> str:
    return get_settings().db_path


async def init_db() -> None:
    async with aiosqlite.connect(_db_path()) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                latency_ms REAL NOT NULL,
                cost_usd REAL NOT NULL,
                error TEXT NOT NULL,
                success INTEGER NOT NULL,
                prompt_quality_score REAL NOT NULL,
                hallucination_risk REAL NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                value REAL NOT NULL,
                threshold REAL NOT NULL,
                resolved INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            )
            """
        )
        await db.execute("CREATE INDEX IF NOT EXISTS idx_calls_ts ON calls(timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_calls_model ON calls(model)")
        await db.commit()


async def insert_call(call: dict) -> None:
    ts = call.get("timestamp")
    if isinstance(ts, datetime):
        ts = ts.isoformat()
    if not ts:
        ts = datetime.utcnow().isoformat()
    async with aiosqlite.connect(_db_path()) as db:
        await db.execute(
            """
            INSERT INTO calls (
                session_id, model, prompt, response, input_tokens, output_tokens, total_tokens,
                latency_ms, cost_usd, error, success, prompt_quality_score, hallucination_risk,
                timestamp, metadata
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                call.get("session_id", "unknown"),
                call.get("model", "unknown"),
                call.get("prompt", "")[:2000],
                call.get("response", "")[:10000],
                int(call.get("input_tokens", 0)),
                int(call.get("output_tokens", 0)),
                int(call.get("total_tokens", 0)),
                float(call.get("latency_ms", 0)),
                float(call.get("cost_usd", 0)),
                call.get("error", "")[:500],
                1 if call.get("success", True) else 0,
                float(call.get("prompt_quality_score", 0)),
                float(call.get("hallucination_risk", 0)),
                ts,
                json.dumps(call.get("metadata", {})),
            ),
        )
        await db.commit()


async def get_calls(limit: int = 100, offset: int = 0) -> list[dict]:
    async with aiosqlite.connect(_db_path()) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM calls ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)
        ) as cursor:
            rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_metrics_summary() -> dict:
    async with aiosqlite.connect(_db_path()) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT COUNT(*) as total FROM calls") as c:
            total = (await c.fetchone())["total"]
        async with db.execute("SELECT COUNT(*) as failed FROM calls WHERE success=0") as c:
            failed = (await c.fetchone())["failed"]
        async with db.execute(
            "SELECT AVG(latency_ms) as avg_lat, MAX(latency_ms) as max_lat FROM calls WHERE success=1"
        ) as c:
            lat = await c.fetchone()
        async with db.execute("SELECT SUM(total_tokens) as tokens, SUM(cost_usd) as cost FROM calls") as c:
            usage = await c.fetchone()
    return {
        "total_calls": total,
        "failed_calls": failed,
        "success_calls": total - failed,
        "error_rate_pct": round((failed / total * 100) if total else 0, 2),
        "avg_latency_ms": round(lat["avg_lat"] or 0, 2),
        "max_latency_ms": round(lat["max_lat"] or 0, 2),
        "total_tokens": usage["tokens"] or 0,
        "total_cost_usd": round(usage["cost"] or 0, 6),
    }


async def get_timeseries(hours: int = 24) -> list[dict]:
    async with aiosqlite.connect(_db_path()) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT
                strftime('%Y-%m-%d %H:00', timestamp) as time_bucket,
                COUNT(*) as calls,
                AVG(latency_ms) as avg_latency,
                SUM(total_tokens) as tokens,
                SUM(cost_usd) as cost,
                SUM(CASE WHEN success=0 THEN 1 ELSE 0 END) as errors
            FROM calls
            WHERE timestamp >= datetime('now', ? || ' hours')
            GROUP BY strftime('%Y-%m-%d %H', timestamp)
            ORDER BY time_bucket ASC
            """,
            (f"-{hours}",),
        ) as cursor:
            rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_model_breakdown() -> list[dict]:
    async with aiosqlite.connect(_db_path()) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT
                model,
                COUNT(*) as calls,
                AVG(latency_ms) as avg_latency,
                SUM(total_tokens) as tokens,
                SUM(cost_usd) as cost,
                AVG(prompt_quality_score) as avg_quality
            FROM calls
            GROUP BY model
            ORDER BY calls DESC
            """
        ) as cursor:
            rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_call_by_id(call_id: int) -> dict:
    async with aiosqlite.connect(_db_path()) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM calls WHERE id=?", (call_id,)) as cursor:
            row = await cursor.fetchone()
    return dict(row) if row else {}


async def insert_alert(alert: dict) -> None:
    async with aiosqlite.connect(_db_path()) as db:
        await db.execute(
            """
            INSERT INTO alerts (type, message, severity, value, threshold, timestamp)
            VALUES (?,?,?,?,?,?)
            """,
            (
                alert["type"],
                alert["message"],
                alert["severity"],
                alert["value"],
                alert["threshold"],
                datetime.utcnow().isoformat(),
            ),
        )
        await db.commit()


async def get_active_alerts() -> list[dict]:
    async with aiosqlite.connect(_db_path()) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM alerts WHERE resolved=0 ORDER BY id DESC LIMIT 20"
        ) as cursor:
            rows = await cursor.fetchall()
    return [dict(row) for row in rows]
