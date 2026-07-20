from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import sensors, camera, coops, subscription

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

@app.get("/")
def root():
    return {"message": "SmartHen API is running"}