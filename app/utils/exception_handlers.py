from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from http import HTTPStatus
from fastapi.exceptions import RequestValidationError

async def http_user_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"{exc.detail}"},
    )