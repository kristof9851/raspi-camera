
import time
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder, H264Encoder
from picamera2.outputs import FileOutput
from libcamera import controls
from threading import Thread
import datetime
import yaml
import os
import glob
import subprocess
import logging

# The Camera class handles all camera-related functionality.
class Camera:
    # Initializes the camera with the given configuration.
    def __init__(self, config):
        self.picam2 = Picamera2()
        self.video_config = self.picam2.create_video_configuration(main={"size": (config['camera']['resolution']['width'], config['camera']['resolution']['height'])})
        self.picam2.configure(self.video_config)
        self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        self.output = None
        self.config = config
        self.ffmpeg_process = None

    # Starts recording the video stream to the given output.
    def start_streaming(self, output):
        logging.info("Starting web streaming...")
        self.output = output
        encoder = JpegEncoder()
        self.picam2.start_recording(encoder, FileOutput(self.output))
        logging.info("Started web streaming.")

    # Starts recording the video to a file in chunks using FFmpeg.
    def start_recording_segments(self):
        logging.info("Starting to record video segments...")
        self.recordings_folder = self.config['camera']['recordings_folder']
        os.makedirs(self.recordings_folder, exist_ok=True)

        # FFmpeg command to segment H264 stream
        # -i pipe:0 reads from stdin
        # -c:v copy copies the video stream without re-encoding
        # -map 0:v:0 selects the video stream from input
        # -f segment uses the segment muxer
        # -segment_time sets the duration of each segment
        # -reset_timestamps 1 resets timestamps at the start of each segment
        # -strftime 1 enables strftime in output filename
        # output_%Y-%m-%d_%H-%M-%S.h264 is the output filename pattern
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", "pipe:0",
            "-c:v", "copy",
            "-map", "0:v:0",
            "-f", "segment",
            "-segment_time", str(self.config['camera']['chunk_size_seconds']),
            "-reset_timestamps", "1",
            "-strftime", "1",
            os.path.join(self.recordings_folder, "%Y-%m-%d_%H-%M-%S.h264")
        ]

        self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(f"FFmpeg process started with command: {' '.join(ffmpeg_cmd)}")

        # Start picamera2 H264 encoder and pipe output to FFmpeg stdin
        h264_encoder = H264Encoder()
        self.picam2.start_encoder(h264_encoder, FileOutput(self.ffmpeg_process.stdin))
        logging.info("Picamera2 H264 encoder started, piping to FFmpeg.")

        # Thread to manage maximum number of video chunks
        def manage_chunks():
            logging.info("FFmpeg chunk management thread started.")
            while True:
                logging.info("Sleeping...")
                time.sleep(self.config['camera']['chunk_size_seconds'])
                video_files = sorted(glob.glob(os.path.join(self.recordings_folder, "*.h264")), key=os.path.getmtime)
                if len(video_files) > self.config['camera']['max_chunks']:
                    logging.info(f"Found {len(video_files)} video chunks, exceeding max of {self.config['camera']['max_chunks']}. Deleting oldest...")
                    for i in range(len(video_files) - self.config['camera']['max_chunks']):
                        os.remove(video_files[i])
                        logging.info(f"Deleted old video chunk: {video_files[i]}")

        self.chunk_management_thread = Thread(target=manage_chunks)
        self.chunk_management_thread.daemon = True
        self.chunk_management_thread.start()

    # Stops the camera recording.
    def stop_recording(self):
        if hasattr(self, 'picam2') and self.picam2.started:
            self.picam2.stop_recording()
            logging.info("Camera recording stopped.")
        if self.ffmpeg_process:
            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait()
            logging.info("FFmpeg process stopped.")
