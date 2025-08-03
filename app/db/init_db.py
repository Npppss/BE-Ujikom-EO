from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal, Base
from app.db.models import User, Role, RefreshToken, PasswordResetToken, Event, EventRegistration, EventLike, EventComment, Attendance, EventStatus, EventCategory
from app.core.security import get_password_hash
from app.core.config import settings
from datetime import datetime, timedelta
import json

def create_default_roles(db: Session):
    """Create default roles with permissions"""
    
    # Admin role with all permissions
    admin_permissions = [
        "user:read", "user:create", "user:update", "user:delete",
        "role:read", "role:create", "role:update", "role:delete",
        "event:read", "event:create", "event:update", "event:delete",
        "event:approve", "event:publish",
        "attendance:read", "attendance:create", "attendance:update", "attendance:delete",
        "analytics:read", "analytics:export",
        "certificate:read", "certificate:create", "certificate:update", "certificate:delete"
    ]
    
    admin_role = Role(
        name="admin",
        description="Administrator with full access",
        permissions=json.dumps(admin_permissions)
    )
    
    # Organizer role with event management permissions
    organizer_permissions = [
        "event:read", "event:create", "event:update", "event:delete",
        "event:publish",
        "attendance:read", "attendance:create", "attendance:update",
        "analytics:read",
        "certificate:read", "certificate:create", "certificate:update"
    ]
    
    organizer_role = Role(
        name="organizer",
        description="Event organizer with event management access",
        permissions=json.dumps(organizer_permissions)
    )
    
    # User role with basic permissions
    user_permissions = [
        "event:read",
        "attendance:read"
    ]
    
    user_role = Role(
        name="user",
        description="Regular user with basic access",
        permissions=json.dumps(user_permissions)
    )
    
    db.add(admin_role)
    db.add(organizer_role)
    db.add(user_role)
    db.commit()
    
    return admin_role, organizer_role, user_role

def create_admin_user(db: Session, admin_role: Role):
    """Create default admin user"""
    
    admin_user = User(
        email="admin@eventorganizer.com",
        hashed_password=get_password_hash("admin123"),
        full_name="System Administrator",
        is_active=True,
        is_verified=True,  # Admin is pre-verified
        email_verification_token=None,
        email_verification_expires=None,
        role_id=admin_role.id
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    return admin_user

def create_sample_events(db: Session, organizer_user: User):
    """Create sample events for testing"""
    
    # Sample event 1
    event1 = Event(
        title="Tech Conference 2024",
        description="Annual technology conference featuring the latest innovations in AI, blockchain, and cloud computing.",
        short_description="Join us for the biggest tech event of the year!",
        category=EventCategory.TECHNOLOGY,
        status=EventStatus.PUBLISHED,
        start_date=datetime.now().date() + timedelta(days=30),
        end_date=datetime.now().date() + timedelta(days=30),
        start_time=datetime.strptime("09:00", "%H:%M").time(),
        end_time=datetime.strptime("17:00", "%H:%M").time(),
        location="Jakarta Convention Center",
        address="Jl. Gatot Subroto, Jakarta Selatan",
        city="Jakarta",
        country="Indonesia",
        is_online=False,
        max_capacity=500,
        price=250000,
        currency="IDR",
        is_free=False,
        flyer_url="https://example.com/tech-conference-flyer.jpg",
        organizer_id=organizer_user.id,
        organizer_name="Tech Events Indonesia",
        organizer_email="info@techevents.id",
        organizer_phone="+62-21-1234567",
        is_featured=True,
        allow_waitlist=True,
        require_approval=False,
        is_active=True,
        views_count=150,
        likes_count=45,
        shares_count=12,
        published_at=datetime.utcnow()
    )
    
    # Sample event 2
    event2 = Event(
        title="Startup Networking Night",
        description="Connect with fellow entrepreneurs, investors, and industry experts in an intimate networking setting.",
        short_description="Build meaningful connections in the startup ecosystem",
        category=EventCategory.BUSINESS,
        status=EventStatus.PUBLISHED,
        start_date=datetime.now().date() + timedelta(days=15),
        end_date=datetime.now().date() + timedelta(days=15),
        start_time=datetime.strptime("18:00", "%H:%M").time(),
        end_time=datetime.strptime("22:00", "%H:%M").time(),
        location="Co-working Space Jakarta",
        address="Jl. Sudirman No. 123, Jakarta Pusat",
        city="Jakarta",
        country="Indonesia",
        is_online=False,
        max_capacity=100,
        price=0,
        currency="IDR",
        is_free=True,
        flyer_url="https://example.com/startup-networking-flyer.jpg",
        organizer_id=organizer_user.id,
        organizer_name="Startup Community Jakarta",
        organizer_email="hello@startupjakarta.id",
        organizer_phone="+62-21-9876543",
        is_featured=False,
        allow_waitlist=True,
        require_approval=True,
        is_active=True,
        views_count=75,
        likes_count=23,
        shares_count=8,
        published_at=datetime.utcnow()
    )
    
    # Sample event 3 (Online)
    event3 = Event(
        title="Digital Marketing Masterclass",
        description="Learn advanced digital marketing strategies from industry experts in this comprehensive online workshop.",
        short_description="Master digital marketing in just 4 hours",
        category=EventCategory.EDUCATION,
        status=EventStatus.PUBLISHED,
        start_date=datetime.now().date() + timedelta(days=7),
        end_date=datetime.now().date() + timedelta(days=7),
        start_time=datetime.strptime("14:00", "%H:%M").time(),
        end_time=datetime.strptime("18:00", "%H:%M").time(),
        location="Online",
        is_online=True,
        online_url="https://zoom.us/j/123456789",
        max_capacity=200,
        price=150000,
        currency="IDR",
        is_free=False,
        flyer_url="https://example.com/digital-marketing-flyer.jpg",
        organizer_id=organizer_user.id,
        organizer_name="Digital Academy",
        organizer_email="info@digitalacademy.id",
        organizer_phone="+62-21-5555666",
        is_featured=True,
        allow_waitlist=True,
        require_approval=False,
        is_active=True,
        views_count=200,
        likes_count=67,
        shares_count=25,
        published_at=datetime.utcnow()
    )
    
    db.add(event1)
    db.add(event2)
    db.add(event3)
    db.commit()
    
    return [event1, event2, event3]

def init_db():
    """Initialize database with default data"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).count()
        if existing_roles == 0:
            print("Creating default roles...")
            admin_role, organizer_role, user_role = create_default_roles(db)
            print("✅ Default roles created")
        else:
            print("✅ Roles already exist")
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            organizer_role = db.query(Role).filter(Role.name == "organizer").first()
            user_role = db.query(Role).filter(Role.name == "user").first()
        
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == "admin@eventorganizer.com").first()
        if not existing_admin:
            print("Creating admin user...")
            admin_user = create_admin_user(db, admin_role)
            print("✅ Admin user created")
            print(f"   Email: {admin_user.email}")
            print(f"   Password: admin123")
        else:
            print("✅ Admin user already exists")
            admin_user = existing_admin
        
        # Check if sample events exist
        existing_events = db.query(Event).count()
        if existing_events == 0:
            print("Creating sample events...")
            # Check if organizer user already exists
            organizer_user = db.query(User).filter(User.email == "organizer@eventorganizer.com").first()
            if not organizer_user:
                # Create a sample organizer user
                organizer_user = User(
                    email="organizer@eventorganizer.com",
                    hashed_password=get_password_hash("organizer123"),
                    full_name="Sample Organizer",
                    is_active=True,
                    is_verified=True,
                    email_verification_token=None,
                    email_verification_expires=None,
                    role_id=organizer_role.id
                )
                db.add(organizer_user)
                db.commit()
                db.refresh(organizer_user)
                print("✅ Organizer user created")
            else:
                print("✅ Organizer user already exists")
            
            sample_events = create_sample_events(db, organizer_user)
            print("✅ Sample events created")
            print(f"   Created {len(sample_events)} sample events")
        else:
            print("✅ Sample events already exist")
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n📋 Default Credentials:")
        print("   Admin: admin@eventorganizer.com / admin123")
        print("   Organizer: organizer@eventorganizer.com / organizer123")
        print("\n🔗 API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 