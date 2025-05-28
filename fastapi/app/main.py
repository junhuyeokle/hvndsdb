from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import database

# nessesary to import all models to register them with SQLAlchemy
import entities

from exception import (
    CustomException,
    custom_exception_handler,
    validation_exception_handler,
)
from routers.deblur_gs_router import deblur_gs_router
from routers.unity_router import unity_router
from routers.building_router import building_router
from routers.user_router import user_router
from routers.general_router import general_router

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
app.include_router(general_router, prefix="/api/general")

app.include_router(unity_router, prefix="/ws/unity")
app.include_router(deblur_gs_router, prefix="/ws/deblur_gs")

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
