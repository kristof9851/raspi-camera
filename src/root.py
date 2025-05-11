from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.get("/", response_class=PlainTextResponse)
async def read_root():
    return "Hello, this is a static plain text response!"
