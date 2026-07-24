from fastapi import APIRouter
from models import Subscription
import sqlite3

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.get("/status/{user_id}")
def get_subscription(user_id: str):
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()
    c.execute("SELECT tariff, status, expires_at FROM subscriptions WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return Subscription(tariff=row[0], status=row[1], expires_at=row[2])
    return {"tariff": "none", "status": "inactive", "expires_at": 0}

@router.post("/update")
def update_subscription(user_id: str, tariff: str):
    if tariff not in ["basic", "optimum", "premium"]:
        return {"status": "error", "message": "Некорректный тариф"}

    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO subscriptions (user_id, tariff, status, expires_at)
        VALUES (?, ?, 'active', ?)
    """, (user_id, tariff, 1720000000))
    conn.commit()
    conn.close()

    return {"status": "ok", "message": f"Тариф '{tariff}' подключён"}