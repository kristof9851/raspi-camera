from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import subprocess
import logging

router = APIRouter()

def generate_camera_frames():
    process = subprocess.Popen(
        [
            "libcamera-vid", "--inline", "-o", "-", "-t", "0", "--framerate", "24", "--width", "640", "--height", "480"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=10**8
    )

    try:
        while True:
            frame = process.stdout.read(1024)
            if not frame:
                break
            yield frame
    except Exception as e:
        logging.error(f"Error in generate_camera_frames: {e}")
    finally:
        process.terminate()
        process.wait()

        # Log stderr output for debugging
        libcamera_stderr = process.stderr.read().decode('utf-8')
        logging.debug(f"libcamera-vid stderr: {libcamera_stderr}")

        logging.debug("Process terminated.")

@router.get("/stream")
async def stream_camera():
    logging.info("/stream endpoint accessed.")
    return StreamingResponse(generate_camera_frames(), media_type="video/h264")
