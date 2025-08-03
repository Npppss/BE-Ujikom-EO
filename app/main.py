from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, user, attendance, event, certificate

app = FastAPI(
    title="Event Organizer API",
    description="A comprehensive event management system with authentication, attendance tracking, and analytics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1")
app.include_router(event.router, prefix="/api/v1")
app.include_router(certificate.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "message": "Event Organizer API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

