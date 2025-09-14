#!/usr/bin/env python3
"""
Adaptive Resource Forecast AI - Main Entry Point

This script starts the FastAPI application server.
"""


import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Adaptive Resource Forecast AI...")
    print("📊 AI-powered software license management and cost optimization")
    print("🌐 Web Interface: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print("-" * 60)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
