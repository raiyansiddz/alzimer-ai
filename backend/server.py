from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Import routers
from api.v1.endpoints import auth, users, test_sessions, cognitive_tests, speech_tests, behavioral_tests, reports, progress
from api.v1.endpoints import enhanced_cognitive_tests, enhanced_speech_tests
from api.v1.endpoints import comprehensive_cognitive_tests, comprehensive_speech_tests, comprehensive_behavioral_tests
from api.v1.endpoints import audio_cognitive_tests
from core.database.connection import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Dementia Detection System API",
    description="Comprehensive cognitive assessment system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(test_sessions.router, prefix="/api/test-sessions", tags=["test-sessions"])
app.include_router(cognitive_tests.router, prefix="/api/cognitive-tests", tags=["cognitive-tests"])
app.include_router(enhanced_cognitive_tests.router, prefix="/api/cognitive-tests", tags=["enhanced-cognitive-tests"])
app.include_router(speech_tests.router, prefix="/api/speech-tests", tags=["speech-tests"])
app.include_router(enhanced_speech_tests.router, prefix="/api/speech-tests", tags=["enhanced-speech-tests"])
app.include_router(comprehensive_cognitive_tests.router, prefix="/api/cognitive-tests", tags=["comprehensive-cognitive-tests"])
app.include_router(comprehensive_speech_tests.router, prefix="/api/speech-tests", tags=["comprehensive-speech-tests"])
app.include_router(behavioral_tests.router, prefix="/api/behavioral-tests", tags=["behavioral-tests"])
app.include_router(comprehensive_behavioral_tests.router, prefix="/api/behavioral-tests", tags=["comprehensive-behavioral-tests"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(audio_cognitive_tests.router, prefix="/api/cognitive-tests", tags=["audio-cognitive-tests"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Dementia Detection System API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
