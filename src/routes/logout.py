from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse
from src.sessions import SESSION_COOKIE_NAME, sessions

router = APIRouter()

@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response
