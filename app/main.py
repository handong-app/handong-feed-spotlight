import logging

from fastapi import FastAPI

from app.api.router import api_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


app = FastAPI(title="Handong Feed Spotlight API")

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to Handong Feed Spotlight API"}
