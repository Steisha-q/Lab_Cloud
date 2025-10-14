from fastapi import FastAPI
from core import router as common_routes
from storage.router import router as storage_router

app = FastAPI(
    title="Lab3 FastAPI Project",
    description="Lab project with FastAPI and Swagger UI",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "FastAPI Azure Blob Storage Service Running"}


app.include_router(common_routes.router)

app.include_router(storage_router)