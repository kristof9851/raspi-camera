from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from src.sessions import authenticate_user

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(user: dict = Depends(authenticate_user)):
    return f"""
    <html>
        <body>
            <h1>Welcome, {user['username']}!</h1>
            <a href="/photo">Go to Photo Page</a>
            <a href="/logout">Logout</a>
        </body>
    </html>
    """
