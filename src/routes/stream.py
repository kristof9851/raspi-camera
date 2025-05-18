import io
from threading import Condition
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from fastapi.requests import Request
import subprocess
import logging

router = APIRouter()

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


async def mjpeg_stream(request: Request):
    print("mjpeg_stream starting...")

    try:
        output = StreamingOutput()
        picam2.start_recording(MJPEGEncoder(), FileOutput(output))
        while True:
            if await request.is_disconnected():
                print("Client disconnected")
                break

            with output.condition:
                output.condition.wait()
                frame = output.frame
            
            yield (b'--FRAME\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n\r\n' +
                   frame + b'\r\n')
    finally:
        print("Finally...")
        picam2.stop_recording()

    print("mjpeg_stream finished")

@router.get("/stream")
async def stream_camera(request: Request):
    return StreamingResponse(mjpeg_stream(request), media_type="multipart/x-mixed-replace; boundary=FRAME")
