from fastapi import APIRouter
import sqlite3
import time
from datetime import datetime, timedelta

router = APIRouter(prefix="/eggs", tags=["eggs"])

# ============================================================
# ДОБАВИТЬ ЯЙЦА (используется ESP32 или вручную)
# ============================================================
@router.post("/add")
def add_eggs(coop_id: str, count: int):
    """Добавить яйца (логируется в egg_history)"""
    now = int(time.time())
    
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()
    
    # Сохраняем в историю
    c.execute("""
        INSERT INTO egg_history (coop_id, count, timestamp)
        VALUES (?, ?, ?)
    """, (coop_id, count, now))
    
    # Обновляем датчик EGG_COUNT
    c.execute("""
        UPDATE sensors 
        SET current_value = current_value + ? 
        WHERE id = 'sensor_eggs' AND coop_id = ?
    """, (count, coop_id))
    
    conn.commit()
    conn.close()
    
    return {"status": "ok", "message": f"Добавлено {count} яиц"}


# ============================================================
# ПОЛУЧИТЬ СТАТИСТИКУ ПО ЯЙЦАМ (за N дней)
# ============================================================
@router.get("/stats/{coop_id}")
def get_stats(coop_id: str, days: int = 30):
    """
    Получить статистику по яйцам за последние N дней.
    По умолчанию 30 дней.
    """
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()
    
    # Получаем историю за N дней
    c.execute("""
        SELECT date(timestamp, 'unixepoch'), SUM(count)
        FROM egg_history
        WHERE coop_id = ?
        AND timestamp >= strftime('%s', 'now', '-' || ? || ' days')
        GROUP BY date(timestamp, 'unixepoch')
        ORDER BY date(timestamp, 'unixepoch') ASC
    """, (coop_id, days))
    
    rows = c.fetchall()
    conn.close()
    
    # Если данных нет, возвращаем пустой список
    if not rows:
        return []
    
    return [{"date": row[0], "count": row[1]} for row in rows]


# ============================================================
# СОБРАТЬ ЯЙЦА (при нажатии кнопки в приложении)
# ============================================================
@router.post("/collect")
def collect_eggs(coop_id: str):
    """
    Собрать все яйца.
    1. Логирует событие сбора в egg_history (с отрицательным значением)
    2. Обнуляет датчик EGG_COUNT
    """
    now = int(time.time())
    
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()
    
    # Получаем текущее количество яиц
    c.execute("""
        SELECT current_value FROM sensors 
        WHERE id = 'sensor_eggs' AND coop_id = ?
    """, (coop_id,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return {"status": "error", "message": "Датчик яиц не найден"}
    
    collected_count = int(row[0])
    
    if collected_count == 0:
        conn.close()
        return {"status": "ok", "message": "Нет яиц для сбора", "count": 0}
    
    # Логируем сбор (отрицательное значение, чтобы отличать от добавления)
    c.execute("""
        INSERT INTO egg_history (coop_id, count, timestamp)
        VALUES (?, ?, ?)
    """, (coop_id, -collected_count, now))
    
    # Обнуляем датчик
    c.execute("""
        UPDATE sensors 
        SET current_value = 0 
        WHERE id = 'sensor_eggs' AND coop_id = ?
    """, (coop_id,))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "ok", 
        "message": f"Собрано {collected_count} яиц",
        "count": collected_count
    }


# ============================================================
# ПОЛУЧИТЬ СТАТИСТИКУ ПО МЕСЯЦАМ (для годового графика)
# ============================================================
@router.get("/monthly/{coop_id}")
def get_monthly_stats(coop_id: str):
    """
    Получить статистику по месяцам (для годового графика).
    Возвращает данные за последние 12 месяцев.
    """
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()
    
    # Группируем по месяцам за последние 12 месяцев
    c.execute("""
        SELECT strftime('%Y-%m', date(timestamp, 'unixepoch')), SUM(count)
        FROM egg_history
        WHERE coop_id = ?
        AND timestamp >= strftime('%s', 'now', '-365 days')
        GROUP BY strftime('%Y-%m', date(timestamp, 'unixepoch'))
        ORDER BY strftime('%Y-%m', date(timestamp, 'unixepoch')) ASC
    """, (coop_id,))
    
    rows = c.fetchall()
    conn.close()
    
    return [{"month": row[0], "count": row[1]} for row in rows]