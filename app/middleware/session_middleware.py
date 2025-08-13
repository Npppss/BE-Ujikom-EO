from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import verify_token
from app.core.config import ADMIN_SESSION_TIMEOUT_MINUTES, USER_SESSION_TIMEOUT_MINUTES
from datetime import datetime, timedelta
import json

class SessionTimeoutMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk mengelola session timeout berdasarkan role user
    - Admin dan user management: 5 menit
    - User biasa: 10 menit
    """
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Skip session check for public endpoints
        if self._is_public_endpoint(request.url.path):
            response = await call_next(request)
            return response
        
        # Check for authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            response = await call_next(request)
            return response
        
        try:
            # Extract token
            token = auth_header.split(" ")[1]
            
            # Verify token and get payload
            payload = verify_token(token, "access")
            if not payload:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid token"}
                )
            
            # Check if token is expired
            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token has no expiration"}
                )
            
            # Convert timestamp to datetime
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            current_datetime = datetime.utcnow()
            
            # Check if token is expired
            if current_datetime >= exp_datetime:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Session expired",
                        "code": "SESSION_EXPIRED",
                        "message": "Sesi Anda telah berakhir. Silakan login kembali."
                    }
                )
            
            # Add session info to request state
            request.state.session_info = {
                "user_id": payload.get("user_id"),
                "role": payload.get("role"),
                "expires_at": exp_datetime.isoformat(),
                "remaining_seconds": int((exp_datetime - current_datetime).total_seconds())
            }
            
            # Continue with the request
            response = await call_next(request)
            
            # Add session timeout headers
            role = payload.get("role", "user")
            timeout_minutes = ADMIN_SESSION_TIMEOUT_MINUTES if role in ["admin", "organizer"] else USER_SESSION_TIMEOUT_MINUTES
            
            response.headers["X-Session-Timeout-Minutes"] = str(timeout_minutes)
            response.headers["X-Session-Expires-At"] = exp_datetime.isoformat()
            response.headers["X-Session-Role"] = role
            
            return response
            
        except Exception as e:
            # If there's any error with token verification, continue without session info
            # This allows the endpoint to handle authentication errors
            response = await call_next(request)
            return response
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no authentication required)"""
        public_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
            "/api/v1/auth/verify-email",
            "/api/v1/auth/resend-verification",
            "/api/v1/auth/password-requirements",
            "/api/v1/auth/validate-password"
        ]
        
        return path in public_paths or path.startswith("/static/") or path.startswith("/media/")
