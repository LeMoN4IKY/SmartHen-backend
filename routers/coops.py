from fastapi import APIRouter, HTTPException
from models import Coop
import sqlite3

router = APIRouter(prefix="/coops", tags=["coops"])

@router.get("/list/{user_id}")
def get_coops(user_id: str):
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()
    c.execute("SELECT id, name, serial FROM coops WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append(Coop(id=row[0], name=row[1], serial=row[2]))
    return result

@router.post("/add")
def add_coop(user_id: str, serial: str):
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()

    c.execute("SELECT id, name, serial FROM coops WHERE serial = ?", (serial,))
    existing = c.fetchone()

    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Курятник с таким QR-кодом не найден")

    c.execute("UPDATE coops SET user_id = ? WHERE serial = ?", (user_id, serial))
    conn.commit()
    conn.close()

    return {"status": "ok", "message": f"Курятник {existing[1]} привязан"}

@router.post("/rename")
def rename_coop(coop_id: str, new_name: str):
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()
    c.execute("UPDATE coops SET name = ? WHERE id = ?", (new_name, coop_id))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Курятник не найден")
    conn.commit()
    conn.close()
    return {"status": "ok", "message": f"Курятник переименован в '{new_name}'"}