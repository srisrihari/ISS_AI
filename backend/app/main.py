from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from .utils.error_handling import add_exception_handlers

from app.routers import placement, search, waste, simulation, import_export, logs, auth, containers, items, emergency

app = FastAPI(title="Space Station Cargo Management System")

# Add exception handlers
add_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(placement.router, prefix="/api", tags=["Placement"])
app.include_router(search.router, prefix="/api", tags=["Search and Retrieval"])
app.include_router(waste.router, prefix="/api", tags=["Waste Management"])
app.include_router(simulation.router, prefix="/api", tags=["Time Simulation"])
app.include_router(import_export.router, prefix="/api", tags=["Import/Export"])
app.include_router(logs.router, prefix="/api", tags=["Logs"])
app.include_router(containers.router, prefix="/api", tags=["Containers"])
app.include_router(items.router, prefix="/api", tags=["Items"])
app.include_router(emergency.router, prefix="/api", tags=["Emergency"])

# Mount static files for frontend
if os.path.exists("../frontend/build"):
    app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
def api_health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
