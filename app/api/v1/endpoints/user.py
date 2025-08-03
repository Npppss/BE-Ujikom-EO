from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.auth import UserOut, UserUpdate, RoleCreate, RoleOut
from app.services.auth_service import auth_service
from app.core.dependencies import get_current_active_user, require_permission, require_role
from app.db.models import User, Role

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/", response_model=List[UserOut])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("user:read")),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
        for user in users
    ]

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:read")),
    db: Session = Depends(get_db)
):
    """Get specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at
    )

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_permission("user:update")),
    db: Session = Depends(get_db)
):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role_id is not None:
        # Check if role exists
        role = db.query(Role).filter(Role.id == user_update.role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        user.role_id = user_update.role_id
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(user)
    
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at
    )

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:delete")),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

# Role management endpoints
@router.get("/roles/", response_model=List[RoleOut])
def get_roles(
    current_user: User = Depends(require_permission("role:read")),
    db: Session = Depends(get_db)
):
    """Get all roles"""
    roles = db.query(Role).all()
    return [
        RoleOut(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=role.permissions.split(',') if role.permissions else [],
            created_at=role.created_at
        )
        for role in roles
    ]

@router.post("/roles/", response_model=RoleOut)
def create_role(
    role: RoleCreate,
    current_user: User = Depends(require_permission("role:create")),
    db: Session = Depends(get_db)
):
    """Create new role"""
    existing_role = db.query(Role).filter(Role.name == role.name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role with this name already exists")
    
    new_role = Role(
        name=role.name,
        description=role.description,
        permissions=','.join(role.permissions) if role.permissions else ""
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return RoleOut(
        id=new_role.id,
        name=new_role.name,
        description=new_role.description,
        permissions=role.permissions,
        created_at=new_role.created_at
    )

@router.put("/roles/{role_id}", response_model=RoleOut)
def update_role(
    role_id: int,
    role_update: RoleCreate,
    current_user: User = Depends(require_permission("role:update")),
    db: Session = Depends(get_db)
):
    """Update role"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if name is being changed and if it conflicts
    if role_update.name != role.name:
        existing_role = db.query(Role).filter(Role.name == role_update.name).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="Role with this name already exists")
    
    role.name = role_update.name
    role.description = role_update.description
    role.permissions = ','.join(role_update.permissions) if role_update.permissions else ""
    
    db.commit()
    db.refresh(role)
    
    return RoleOut(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role_update.permissions,
        created_at=role.created_at
    )

@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    current_user: User = Depends(require_permission("role:delete")),
    db: Session = Depends(get_db)
):
    """Delete role"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if role is being used by any user
    users_with_role = db.query(User).filter(User.role_id == role_id).count()
    if users_with_role > 0:
        raise HTTPException(status_code=400, detail="Cannot delete role that is assigned to users")
    
    db.delete(role)
    db.commit()
    
    return {"message": "Role deleted successfully"}
