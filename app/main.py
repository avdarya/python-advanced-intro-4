from contextlib import asynccontextmanager

import dotenv
from app.utils.exception_handlers import http_user_exception_handler, handle_validation_error

dotenv.load_dotenv()

import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi_pagination import add_pagination
from fastapi.exceptions import RequestValidationError

from app.database.engine import create_db_and_tables
from app.routers import status, users

@asynccontextmanager
async def lifespan(application: FastAPI):
    print("On startup")
    create_db_and_tables()
    add_pagination(application)
    yield
    print("On shutdown")
app = FastAPI(lifespan=lifespan)
app.include_router(status.router)
app.include_router(users.router)

app.add_exception_handler(HTTPException, http_user_exception_handler)
app.add_exception_handler(RequestValidationError, handle_validation_error)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)