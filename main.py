from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import sensors, camera, coops, subscription, eggs
import threading
import time
import sqlite3

app = FastAPI(title="SmartHen API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensors.router)
app.include_router(camera.router)
app.include_router(coops.router)
app.include_router(subscription.router)
app.include_router(eggs.router)  # ← ДОБАВЛЕНО

@app.get("/")
def root():
    return {"message": "SmartHen API is running"}

# ============================================================
# ФОНОВАЯ ПРОВЕРКА ДАТЧИКОВ
# ============================================================
def health_check():
    while True:
        time.sleep(60)
        try:
            now = int(time.time())
            conn = sqlite3.connect("smarthen.db")
            c = conn.cursor()
            c.execute("UPDATE sensors SET is_online = 0 WHERE last_seen < ?", (now - 300,))
            conn.commit()
            conn.close()
        except Exception as e:
            print("health_check error:", e)

threading.Thread(target=health_check, daemon=True).start()

# ============================================================
# ИНИЦИАЛИЗАЦИЯ БД
# ============================================================
def init_db():
    conn = sqlite3.connect("smarthen.db")
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS sensors (
            id TEXT,
            coop_id TEXT,
            type TEXT,
            name TEXT,
            unit TEXT,
            current_value REAL,
            min_value REAL,
            max_value REAL,
            warning_threshold REAL,
            is_online INTEGER,
            last_seen INTEGER,
            PRIMARY KEY (id, coop_id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS sensor_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT,
            coop_id TEXT,
            value REAL,
            timestamp INTEGER
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS coops (
            id TEXT PRIMARY KEY,
            name TEXT,
            serial TEXT,
            user_id TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id TEXT PRIMARY KEY,
            tariff TEXT,
            status TEXT,
            expires_at INTEGER
        )
    ''')

    # ===== НОВАЯ ТАБЛИЦА ДЛЯ ЯИЦ =====
    c.execute('''
        CREATE TABLE IF NOT EXISTS eggs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coop_id TEXT,
            date TEXT,
            count INTEGER
        )
    ''')

     # ===== НОВАЯ ТАБЛИЦА ДЛЯ ИСТОРИИ ЯИЦ =====
    c.execute('''
        CREATE TABLE IF NOT EXISTS egg_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coop_id TEXT,
            count INTEGER,
            timestamp INTEGER
        )
    ''')

    # ===== ТЕСТОВЫЕ ДАННЫЕ ДЛЯ ЯИЦ =====
    import time
    import random
    now = int(time.time())
    
    # Проверяем, есть ли данные в egg_history
    c.execute("SELECT COUNT(*) FROM egg_history")
    if c.fetchone()[0] == 0:
        # Добавляем данные за последние 7 дней
        for day in range(7, 0, -1):
            ts = now - (day * 86400)
            count = random.randint(5, 20)
            c.execute("""
                INSERT INTO egg_history (coop_id, count, timestamp)
                VALUES (?, ?, ?)
            """, ("1", count, ts))

    # ===== ТЕСТОВЫЕ ДАННЫЕ ДЛЯ ТЕМПЕРАТУРЫ =====
    c.execute("SELECT COUNT(*) FROM sensor_history WHERE sensor_id = 'sensor_temp'")
    if c.fetchone()[0] == 0:
        # Добавляем температуру за последние 7 дней (каждые 6 часов)
        for hour in range(0, 7 * 24, 6):
            ts = now - (hour * 3600)
            # Случайная температура от 18 до 25 градусов
            temp = 18 + random.random() * 7
            c.execute("""
                INSERT INTO sensor_history (sensor_id, coop_id, value, timestamp)
                VALUES (?, ?, ?, ?)
            """, ("sensor_temp", "1", round(temp, 1), ts))


    # Тестовые датчики (если нет)
    c.execute("SELECT COUNT(*) FROM sensors")
    if c.fetchone()[0] == 0:
        now = int(time.time())
        c.execute("INSERT INTO coops (id, name, serial, user_id) VALUES ('1', 'Курятник №1', 'COOP-001', 'user_1')")
        c.execute("INSERT INTO coops (id, name, serial, user_id) VALUES ('2', 'Курятник №2', 'COOP-002', 'user_1')")

        sensors = [
            ("sensor_water", "1", "WATER", "Вода", "%", 65.0, 0, 100, 20, 1, now),
            ("sensor_feed", "1", "FEED", "Корм", "%", 42.0, 0, 100, 20, 1, now),
            ("sensor_temp", "1", "TEMPERATURE", "Температура", "°C", 22.5, -10, 50, 19, 1, now),
            ("sensor_heating", "1", "HEATING", "Отопление", "", 0.0, 0, 1, 20, 1, now),
            ("sensor_air", "1", "AIR_QUALITY", "Загрязнение воздуха", "%", 35.0, 0, 100, 20, 1, now),
            ("sensor_eggs", "1", "EGG_COUNT", "Накоплено яиц", "шт", 28.0, 0, 20, 15, 1, now),
        ]
        for s in sensors:
            c.execute('''
                INSERT INTO sensors (id, coop_id, type, name, unit, current_value, min_value, max_value, warning_threshold, is_online, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', s)

    conn.commit()
    conn.close()

init_db()