# raspi-camera

## Install


## picamera2 installation
https://forums.raspberrypi.com/viewtopic.php?t=361758

## Set up as systemd service
Create file: `/lib/systemd/system/my.service`
```
[Unit]
Description=MyService
After=multi-user.target

[Service]
Type=idle
ExecStart=/home/kristof/work/github.com/kristof9851/raspi-camera/venv/bin/python /home/kristof/work/github.com/kristof9851/raspi-camera/index.py

[Install]
WantedBy=multi-user.target
```