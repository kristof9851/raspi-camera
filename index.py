from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from src import stream, camera, photo, root  # Import modules directly from src

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Mount the directory to serve static files
app.mount("/static", StaticFiles(directory="./static"), name="static")

# Include routes
app.include_router(root.router)
app.include_router(stream.router)
app.include_router(camera.router)
app.include_router(photo.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8443)
