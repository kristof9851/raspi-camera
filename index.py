from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from src.routes import stream, camera, photo, root, login, logout, dashboard
from src.database import fake_users_db
from src.sessions import sessions, SESSION_COOKIE_NAME, authenticate_user

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Middleware to protect static files
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/static"):
            session_token = request.cookies.get(SESSION_COOKIE_NAME)
            if not session_token or session_token not in sessions:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )
        response = await call_next(request)
        return response

app = FastAPI()

# Add middleware for static file protection
app.add_middleware(AuthMiddleware)

# Protect the /photo, /stream, /camera, and /dashboard routers
app.include_router(photo.router, dependencies=[Depends(authenticate_user)])
app.include_router(stream.router, dependencies=[Depends(authenticate_user)])
app.include_router(camera.router, dependencies=[Depends(authenticate_user)])
app.include_router(dashboard.router, dependencies=[Depends(authenticate_user)])

# Mount the directory to serve static files
app.mount("/static", StaticFiles(directory="./static"), name="static")

# Include other routes without authentication
app.include_router(root.router)
app.include_router(login.router)
app.include_router(logout.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8443)
