from fastapi import APIRouter, HTTPException
from models import Sensor, SensorType
import time
import sqlite3

router = APIRouter(prefix="/sensors", tags=["sensors"])

def get_sensors_from_db(coop_id: str):
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()
    c.execute("SELECT * FROM sensors WHERE coop_id = ?", (coop_id,))
    rows = c.fetchall()
    conn.close()

    sensors = []
    for row in rows:
        sensors.append(Sensor(
            id=row[0],
            type=SensorType[row[2]],
            name=row[3],
            unit=row[4],
            current_value=row[5],
            min_value=row[6],
            max_value=row[7],
            warning_threshold=row[8],
            is_online=bool(row[9]),
            last_seen=row[10]
        ))
    return sensors

@router.get("/{coop_id}")
def get_sensors(coop_id: str):
    sensors = get_sensors_from_db(coop_id)
    if not sensors:
        raise HTTPException(status_code=404, detail="Курятник не найден")
    return sensors

# ============================================================
# 🔧 ESP32 БУДЕТ ОТПРАВЛЯТЬ ДАННЫЕ СЮДА
# ============================================================
@router.post("/{coop_id}/{sensor_id}")
def update_sensor(coop_id: str, sensor_id: str, value: float):
    now = int(time.time())
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()

    c.execute("""
        UPDATE sensors
        SET current_value = ?, last_seen = ?, is_online = 1
        WHERE id = ? AND coop_id = ?
    """, (value, now, sensor_id, coop_id))

    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Датчик не найден")

    c.execute("INSERT INTO sensor_history (sensor_id, coop_id, value, timestamp) VALUES (?, ?, ?, ?)",
              (sensor_id, coop_id, value, now))

    conn.commit()
    conn.close()

    return {"status": "ok", "message": "Датчик обновлён"}

# ============================================================
# 🔧 ПРИЛОЖЕНИЕ ЗАПРАШИВАЕТ СТАТУС ДАТЧИКОВ СЮДА
# ============================================================
@router.post("/check/{coop_id}")
def check_sensors(coop_id: str):
    sensors = get_sensors_from_db(coop_id)
    results = []
    for sensor in sensors:
        results.append({
            "sensorId": sensor.id,
            "isOnline": sensor.is_online
        })
    return results

@router.get("/history/{coop_id}/{sensor_id}")
def get_sensor_history(coop_id: str, sensor_id: str, days: int = 7):
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, value FROM sensor_history 
        WHERE coop_id = ? AND sensor_id = ? 
        AND timestamp >= strftime('%s', 'now', '-' || ? || ' days')
        ORDER BY timestamp ASC
    """, (coop_id, sensor_id, days))
    rows = c.fetchall()
    conn.close()
    return [{"timestamp": row[0], "value": row[1]} for row in rows]