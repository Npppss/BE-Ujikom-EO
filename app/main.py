from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, user, attendance, event, certificate, export
from app.middleware import SessionTimeoutMiddleware

app = FastAPI(
    title="Event Organizer API",
    description="API untuk sistem manajemen event dan sertifikat",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session timeout middleware
app.add_middleware(SessionTimeoutMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1")
app.include_router(event.router, prefix="/api/v1")
app.include_router(certificate.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Event Organizer API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

