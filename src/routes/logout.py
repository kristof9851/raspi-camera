from fastapi import APIRouter, Response
from src.sessions import SESSION_COOKIE_NAME

router = APIRouter()

@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"message": "Logged out successfully"}
