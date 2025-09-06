from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, user, attendance, event, certificate, export, mobile, analytics, payment
from app.middleware import SessionTimeoutMiddleware
from app.services.websocket_manager import websocket_handler

app = FastAPI(
    title="Event Organizer API",
    description="API untuk sistem manajemen event dan sertifikat",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
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
app.include_router(mobile.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(payment.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Event Organizer API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time notifications"""
    try:
        # Validate user authentication (you might want to implement proper token validation)
        await websocket_handler.handle_websocket(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close()

