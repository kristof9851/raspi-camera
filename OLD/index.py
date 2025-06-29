from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from src.routes import stream, video, photo, home, login, logout, dashboard
from src.database import fake_users_db
from src.sessions import sessions, SESSION_COOKIE_NAME, authenticate_user
from fastapi.responses import RedirectResponse, StreamingResponse, FileResponse
import socket

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Middleware to protect static files
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/static") or request.url.path in ["/photo", "/stream", "/video", "/dashboard"]:
            session_token = request.cookies.get(SESSION_COOKIE_NAME)
            if not session_token or session_token not in sessions:
                # Redirect to login page with an error message
                redirect_url = f"/?error=Not%20authenticated"
                return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
        response = await call_next(request)
        return response

app = FastAPI()

# Add middleware for static file protection
app.add_middleware(AuthMiddleware)

# Protect the /photo, /stream, /video, and /dashboard routers
app.include_router(photo.router, dependencies=[Depends(authenticate_user)])
app.include_router(stream.router, dependencies=[Depends(authenticate_user)])
app.include_router(video.router, dependencies=[Depends(authenticate_user)])
app.include_router(dashboard.router, dependencies=[Depends(authenticate_user)])

# Mount the directory to serve static files
app.mount("/static", StaticFiles(directory="/home/kristof/work/github.com/kristof9851/raspi-camera/static"), name="static")

# Include other routes without authentication
app.include_router(home.router)
app.include_router(login.router)
app.include_router(logout.router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8443 #,
        # ssl_certfile="/path/to/your/certificate.crt",  # Replace with your certificate file path
        # ssl_keyfile="/path/to/your/private.key"       # Replace with your private key file path
    )
