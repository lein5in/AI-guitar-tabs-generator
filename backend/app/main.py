from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title = "Fretify API",
    description = "AI powered guitar transcription API",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Fretify API! ",
        "version": "0.1.0",
        "docs" : "/docs"
    }           

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message" : "Fretify is running!"
    }

@app.get("/api/v1/info")
async def info():
    return {
        "name": "Fretify API",
        "version": "0.1.0",
        "endpoints": [
            "/",
            "/health",
            "/api/v1/info",
            "/docs"
        ]
    }