# Raspberry Pi Camera Server

This project turns a Raspberry Pi with a camera module into a video surveillance system. It records video in one-minute segments and provides a live video stream accessible through a web browser.

## Requirements

### Hardware
*   A Raspberry Pi (tested with Raspberry Pi 4 Model B)
*   A Raspberry Pi Camera Module (tested with Camera Module 3)

### Software
*   Python 3
*   pip
*   The Python libraries listed in `requirements.txt`:
    *   `flask`
    *   `picamera2`
    *   `PyYAML`

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv --system-site-packages venv
    source venv/bin/activate
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application is configured using the `config.yml` file.

```yaml
camera:
  resolution:
    width: 640
    height: 480
  recordings_folder: "recordings"
  chunk_size_seconds: 60
server:
  host: "0.0.0.0"
  port: 8000
```

*   **`camera.resolution`**: Sets the width and height of the video stream and recordings.
*   **`camera.recordings_folder`**: The directory where the video recordings will be saved.
*   **`camera.chunk_size_seconds`**: The duration of each recorded video segment in seconds.
*   **`server.host`**: The host address for the web server. `0.0.0.0` makes it accessible from other devices on the same network.
*   **`server.port`**: The port for the web server.

## How to Run

To start the server, run the following command from the project's root directory:

```bash
source venv/bin/activate
python3 index.py
```

The server will start, and you will see output in the console.

## Accessing the Live Stream

Once the server is running, you can access the live video stream by opening a web browser and navigating to:

`http://<your-pi-ip-address>:8000`

Replace `<your-pi-ip-address>` with the actual IP address of your Raspberry Pi. The recorded video segments will be saved in the `recordings` folder.

## Running as a Systemd Service

To ensure the server starts automatically on boot and runs reliably in the background, you can set it up as a `systemd` service.

1.  **Create the service file:**
    Create a file named `raspi-camera.service` in `/etc/systemd/system/` with the following content:

    ```ini
    [Unit]
    Description=Raspberry Pi Camera Server
    After=network.target

    [Service]
    User=kristof
    WorkingDirectory=/home/kristof/work/github.com/kristof9851/raspi-camera/
    ExecStart=/bin/bash -c "source /home/kristof/work/github.com/kristof9851/raspi-camera/venv/bin/activate && /home/kristof/work/github.com/kristof9851/raspi-camera/start.sh"
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```


2.  **Reload systemd daemon:**
    ```bash
    sudo systemctl daemon-reload
    ```

3.  **Enable the service to start on boot:**
    ```bash
    sudo systemctl enable raspi-camera.service
    ```

4.  **Start the service immediately:**
    ```bash
    sudo systemctl start raspi-camera.service
    ```

5.  **Check the service status (optional, but recommended):**
    ```bash
    sudo systemctl status raspi-camera.service
    ```