from fastapi import APIRouter
from models import Subscription

router = APIRouter(prefix="/subscription", tags=["subscription"])

subscriptions_db = {
    "user_1": Subscription(tariff="basic", status="active", expires_at=1720000000),
    "user_2": Subscription(tariff="optimum", status="active", expires_at=1720000000)
}

@router.get("/status/{user_id}")
def get_subscription(user_id: str):
    if user_id in subscriptions_db:
        return subscriptions_db[user_id]
    return {"tariff": "none", "status": "inactive", "expires_at": 0}

@router.post("/update")
def update_subscription(user_id: str, tariff: str):
    if tariff not in ["basic", "optimum", "premium"]:
        return {"status": "error", "message": "Некорректный тариф"}
    subscriptions_db[user_id] = Subscription(tariff=tariff, status="active", expires_at=1720000000)
    return {"status": "ok", "message": f"Тариф '{tariff}' подключён"}