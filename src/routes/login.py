from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from src.database import fake_users_db
from src.sessions import sessions, SESSION_COOKIE_NAME
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.post("/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    print(user)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    # Create a session token
    session_token = form_data.username
    sessions[session_token] = user
    response.set_cookie(key=SESSION_COOKIE_NAME, value=session_token, httponly=True)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER, headers=response.headers)
