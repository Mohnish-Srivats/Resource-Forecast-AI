from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from .api.routes import router
from .api.chat_routes import router as chat_router

# Create FastAPI application
app = FastAPI(
    title="Adaptive Resource Forecast AI",
    description="AI-powered software license management and cost optimization platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Include API routes
app.include_router(router)
app.include_router(chat_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Adaptive Resource Forecast AI is running"}

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "features": [
            "License utilization analysis",
            "Cost forecasting",
            "Renewal recommendations",
            "AP team reports",
            "Procurement reports"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
