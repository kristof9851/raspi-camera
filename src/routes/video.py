from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

router = APIRouter()
templates = Jinja2Templates(directory="templates")  # Directory for templates

@router.get("/video")
async def serve_video(request: Request):
    # Render the HTML template with context
    return templates.TemplateResponse("video.html", {"request": request})

# rpicam-vid --camera 0 -t 0 --libav-format h264 --libav-video-codec h264 --codec h264 --nopreview -o tcp://127.0.0.1:8888 --listen --inline
# rpicam-vid --camera 0 -t 0 --codec mjpeg --nopreview -o tcp://127.0.0.1:8888 --listen --inline
# rpicam-vid -t 0 --inline --libav-format h264 -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8000/}' :demux=h264
