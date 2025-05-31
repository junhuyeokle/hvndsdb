from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import utils.database as database

# necessary to import all models to register them with SQLAlchemy
import entities

from utils.exception import (
    CustomException,
    custom_exception_handler,
    validation_exception_handler,
)
from routers.analyzer_router import analyzer_router
from routers.deblur_gs_router import deblur_gs_router
from routers.unity_router import unity_router
from routers.building_router import building_router
from routers.user_router import user_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    database.init_engine()
    database.Base.metadata.create_all(bind=database.engine)


app.include_router(user_router, prefix="/api/user")
app.include_router(building_router, prefix="/api/building")
app.include_router(analyzer_router, prefix="/api/analyzer")

app.include_router(unity_router, prefix="/ws/unity")
app.include_router(deblur_gs_router, prefix="/ws/deblur_gs")

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
