from fastapi import FastAPI

from src.routers import timeslots

app = FastAPI()
app.include_router(timeslots.router)
