# rpicam-vid --camera 0 -t 0 --libav-format h264 --libav-video-codec h264 --codec h264 --nopreview -o tcp://127.0.0.1:8888 --listen --inline
# rpicam-vid --camera 0 -t 0 --codec mjpeg --nopreview -o tcp://127.0.0.1:8888 --listen --inline
# rpicam-vid -t 0 --inline --libav-format h264 -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8000/}' :demux=h264


from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Mount the directory to serve static files
app.mount("/static", StaticFiles(directory="./static"), name="static")

@app.get("/", response_class=PlainTextResponse)
async def read_root():
    return "Hello, this is a static plain text response!"

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

@app.get("/stream")
async def stream_camera():
    logging.info("/stream endpoint accessed.")
    return StreamingResponse(generate_camera_frames(), media_type="video/h264")

@app.get("/camera")
async def serve_index():
    return FileResponse("index.html", media_type="text/html")

@app.get("/photo")
async def capture_photo():
    # Command to capture a photo
    subprocess.run(["rpicam-still", "--nopreview", "--immediate", "-o", "static/photo/output.jpeg"], check=True)

    # Get the current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # HTML content to display the image and current date/time
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Photo Capture</title>
    </head>
    <body>
        <h1>Photo Captured</h1>
        <p>Date: {current_datetime}</p>
        <img src="static/photo/output.jpeg" alt="Captured Photo" style="max-width:100%;height:auto;">
    </body>
    </html>
    """

    return PlainTextResponse(html_content, media_type="text/html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8443)
