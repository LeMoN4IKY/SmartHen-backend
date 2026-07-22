from fastapi import APIRouter, HTTPException
from models import Coop

router = APIRouter(prefix="/coops", tags=["coops"])

coops_db = {
    "1": Coop(id="1", name="Курятник №1", serial="COOP-001"),
    "2": Coop(id="2", name="Курятник №2", serial="COOP-002")
}

user_coops = {
    "user_1": ["1", "2"]
}

@router.get("/list/{user_id}")
def get_coops(user_id: str):
    result = []
    for coop_id in user_coops.get(user_id, []):
        if coop_id in coops_db:
            result.append(coops_db[coop_id])
    return result

@router.post("/add")
def add_coop(user_id: str, serial: str):
    for coop in coops_db.values():
        if coop.serial == serial:
            if user_id not in user_coops:
                user_coops[user_id] = []
            if coop.id not in user_coops[user_id]:
                user_coops[user_id].append(coop.id)
            return {"status": "ok", "message": f"Курятник {coop.name} привязан"}
    raise HTTPException(status_code=404, detail="Курятник с таким QR-кодом не найден")

@router.post("/rename")
def rename_coop(coop_id: str, new_name: str):
    if coop_id in coops_db:
        coops_db[coop_id].name = new_name
        return {"status": "ok", "message": f"Курятник переименован в '{new_name}'"}
    raise HTTPException(status_code=404, detail="Курятник не найден")