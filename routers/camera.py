from fastapi import APIRouter

router = APIRouter(prefix="/camera", tags=["camera"])

camera_state = {
    "is_on": False,
    "is_recording": False
}

@router.post("/start")
def start_camera():
    camera_state["is_on"] = True
    camera_state["is_recording"] = False
    return {"status": "ok", "message": "Камера включена"}

@router.post("/stop")
def stop_camera():
    camera_state["is_on"] = False
    camera_state["is_recording"] = False
    return {"status": "ok", "message": "Камера выключена"}

@router.post("/start_record")
def start_record():
    if not camera_state["is_on"]:
        return {"status": "error", "message": "Камера не включена"}
    camera_state["is_recording"] = True
    return {"status": "ok", "message": "Запись начата"}

@router.post("/stop_record")
def stop_record():
    if not camera_state["is_on"]:
        return {"status": "error", "message": "Камера не включена"}
    camera_state["is_recording"] = False
    return {"status": "ok", "message": "Запись остановлена"}

@router.get("/status")
def camera_status():
    return camera_state