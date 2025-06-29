import os
from flask import Flask, Response, render_template, request, redirect, url_for, session, g
import io
from threading import Condition
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# The StreamingOutput class is a file-like object that captures the video stream.
class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    # Writes the given buffer to the frame and notifies all clients.
    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

# The Flask web server application.
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY environment variable not set. Please set it for security.")

# Initialize Limiter (will be configured in run_app)
limiter = None

# The output object that will hold the video stream.
output = StreamingOutput()

# Global camera object, set by run_app
global_camera = None

# Load authorized users from file
users = {}
try:
    with open('authorized.txt', 'r') as f:
        for line in f:
            username, hashed_password = line.strip().split(':', 1)
            users[username] = hashed_password
except FileNotFoundError:
    print("authorized.txt not found. Please create it with username:hashed_password entries.")

# Login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Apply rate limit dynamically
    if limiter:
        try:
            limiter.check()
        except Exception as e:
            return "Too many requests!", 429

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Basic input validation
        if not username or not password:
            return render_template('login.html', error='Username and password are required')

        if username in users and check_password_hash(users[username], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

# Error handler for rate limit exceeded
@app.errorhandler(429)
def ratelimit_handler(e):
    return "Too many requests!", 429

# Dashboard page route
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', camera_available=bool(global_camera))

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# The index page route (redirects to login if not authenticated, otherwise to dashboard).
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# Generates the video frames for the stream.
def gen_frames():
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# The video feed route.
@app.route('/camera')
def video_feed():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if not global_camera:
        return "Camera is currently offline or busy.", 503 # Service Unavailable
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Function to run the Flask app
def run_app(camera, host, port, threaded, config):
    global limiter
    global global_camera
    global_camera = camera # Set the global camera object

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[
            f"{config['server']['rate_limiting']['default']['per_day']} per day",
            f"{config['server']['rate_limiting']['default']['per_hour']} per hour"
        ],
        storage_uri="memory://",
    )
    limiter.limit(f"{config['server']['rate_limiting']['login']['calls']} per {config['server']['rate_limiting']['login']['period_seconds']} seconds")(login)

    # Start the camera streaming and recording only if camera is available.
    if camera:
        camera.start_streaming(output)
        camera.start_recording_segments()
    app.run(host=host, port=port, threaded=threaded)