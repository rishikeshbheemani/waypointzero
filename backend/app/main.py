from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="Voyager AI",
    description="Autonomous Multi-Agent Travel Planning System",
    version="0.1.0"
)

app.include_router(health_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Voyager AI!"
    }