from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import subprocess
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

router = APIRouter()
templates = Jinja2Templates(directory="/home/kristof/work/github.com/kristof9851/raspi-camera/templates")  # Directory for templates

@router.get("/photo")
async def capture_photo(request: Request):
    photo_path = "static/photo/output.jpeg" 

    # Command to capture a photo
    subprocess.run(["rpicam-still", "--nopreview", "--vflip", "--immediate", "-o", photo_path], check=True)

    # Get the current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Render the HTML template with context
    return templates.TemplateResponse("photo.html", {"request": request, "photo_path": photo_path, "current_datetime": current_datetime})
