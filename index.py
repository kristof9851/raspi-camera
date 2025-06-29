
import yaml
import logging
from camera import Camera
from server import app, output, run_app
import picamera2

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

print("Application index.py is starting...")


# Main entry point for the application.
if __name__ == '__main__':
    # Load the configuration from the config.yml file.
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)

    camera = None
    try:
        # Create a camera object with the loaded configuration.
        camera = Camera(config)
    except RuntimeError as e:
        logging.error(f"Failed to initialize camera: {e}. The camera stream and recording will not be available.")

    # Start the web server.
    try:
        run_app(camera, host=config['server']['host'], port=config['server']['port'], threaded=True, config=config)
    except KeyboardInterrupt:
        # Stop the camera recording when the server is stopped.
        if camera:
            camera.stop_recording()
