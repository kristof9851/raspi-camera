from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from src.sessions import authenticate_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard")
async def dashboard(request: Request, user: dict = Depends(authenticate_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": user["username"]})
