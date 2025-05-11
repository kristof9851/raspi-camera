from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/camera")
async def serve_index():
    return FileResponse("index.html", media_type="text/html")

# rpicam-vid --camera 0 -t 0 --libav-format h264 --libav-video-codec h264 --codec h264 --nopreview -o tcp://127.0.0.1:8888 --listen --inline
# rpicam-vid --camera 0 -t 0 --codec mjpeg --nopreview -o tcp://127.0.0.1:8888 --listen --inline
# rpicam-vid -t 0 --inline --libav-format h264 -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8000/}' :demux=h264
