from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def read_home(request: Request):  # Renamed function
    error_message = request.query_params.get("error", "")
    return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})
