from fastapi import APIRouter, HTTPException
from models import Sensor, SensorType

router = APIRouter(prefix="/sensors", tags=["sensors"])

sensors_db = {
    "1": [
        Sensor(id="sensor_water", type=SensorType.WATER, name="Вода", unit="%", current_value=65.0),
        Sensor(id="sensor_feed", type=SensorType.FEED, name="Корм", unit="%", current_value=42.0),
        Sensor(id="sensor_temp", type=SensorType.TEMPERATURE, name="Температура", unit="°C", current_value=22.5, min_value=-10, max_value=50, warning_threshold=19),
        Sensor(id="sensor_heating", type=SensorType.HEATING, name="Отопление", unit="", current_value=0.0, min_value=0, max_value=1),
        Sensor(id="sensor_air", type=SensorType.AIR_QUALITY, name="Загрязнение воздуха", unit="%", current_value=35.0),
        Sensor(id="sensor_eggs", type=SensorType.EGG_COUNT, name="Накоплено яиц", unit="шт", current_value=28.0, max_value=20, warning_threshold=15)
    ],
    "2": [
        Sensor(id="sensor_water", type=SensorType.WATER, name="Вода", unit="%", current_value=80.0),
        Sensor(id="sensor_feed", type=SensorType.FEED, name="Корм", unit="%", current_value=55.0),
        Sensor(id="sensor_temp", type=SensorType.TEMPERATURE, name="Температура", unit="°C", current_value=18.0, min_value=-10, max_value=50, warning_threshold=19),
        Sensor(id="sensor_heating", type=SensorType.HEATING, name="Отопление", unit="", current_value=1.0, min_value=0, max_value=1),
        Sensor(id="sensor_air", type=SensorType.AIR_QUALITY, name="Загрязнение воздуха", unit="%", current_value=45.0),
        Sensor(id="sensor_eggs", type=SensorType.EGG_COUNT, name="Накоплено яиц", unit="шт", current_value=12.0, max_value=20, warning_threshold=15)
    ]
}

@router.get("/{coop_id}")
def get_sensors(coop_id: str):
    if coop_id not in sensors_db:
        raise HTTPException(status_code=404, detail="Курятник не найден")
    return sensors_db[coop_id]

@router.post("/{coop_id}/{sensor_id}")
def update_sensor(coop_id: str, sensor_id: str, value: float):
    if coop_id not in sensors_db:
        raise HTTPException(status_code=404, detail="Курятник не найден")
    
    for sensor in sensors_db[coop_id]:
        if sensor.id == sensor_id:
            sensor.current_value = value
            if sensor.type == SensorType.TEMPERATURE:
                for s in sensors_db[coop_id]:
                    if s.type == SensorType.HEATING:
                        s.current_value = 1.0 if value < 19 else 0.0
            return {"status": "ok", "message": "Датчик обновлён"}
    
    raise HTTPException(status_code=404, detail="Датчик не найден")

@router.post("/check/{coop_id}")
def check_sensors(coop_id: str):
    if coop_id not in sensors_db:
        raise HTTPException(status_code=404, detail="Курятник не найден")
    
    results = []
    for sensor in sensors_db[coop_id]:
        results.append({
            "sensorId": sensor.id,
            "isOnline": True
        })
    return results