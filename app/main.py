import dotenv

dotenv.load_dotenv()

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate, Params
from http import HTTPStatus
from pydantic import ValidationError



from routers import status, users
from database.engine import create_db_and_tables

app = FastAPI()
app.include_router(status.router)
app.include_router(users.router)

add_pagination(app)

@app.exception_handler(HTTPException)
async def http_user_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"{exc.detail}"},
    )
@app.exception_handler(ValidationError)
async def handle_validation_error( request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={"message": "invalid data"}
    )

if __name__ == "__main__":
    create_db_and_tables()
    uvicorn.run(app, host="0.0.0.0", port=8000)