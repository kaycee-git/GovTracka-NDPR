from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import uuid
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    CITIZEN = "citizen"
    MODERATOR = "moderator"
    NGO_PARTNER = "ngo_partner"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    
    # NDPR Compliance fields
    phone_number_hash = db.Column(db.String(64), nullable=True)  # Hashed for privacy
    is_anonymous = db.Column(db.Boolean, default=False)
    anonymous_id = db.Column(db.String(20), nullable=True, unique=True)  # e.g., User_8F3E
    
    # User management
    role = db.Column(db.Enum(UserRole), default=UserRole.CITIZEN)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # USSD/WhatsApp integration
    ussd_session_active = db.Column(db.Boolean, default=False)
    preferred_contact_method = db.Column(db.String(20), default='web')  # 'web', 'ussd', 'whatsapp'
    
    # Privacy settings
    data_retention_consent = db.Column(db.Boolean, default=False)
    marketing_consent = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.anonymous_id or self.username or self.id}>'
    
    def anonymize(self):
        """Anonymize user data for NDPR compliance"""
        if not self.is_anonymous:
            # Generate anonymous ID
            self.anonymous_id = self.generate_anonymous_id()
            
            # Clear personal data
            original_email = self.email
            original_username = self.username
            
            self.email = None
            self.username = None
            self.is_anonymous = True
            self.updated_at = datetime.utcnow()
            
            # Log anonymization
            from src.models.ndpr_compliance import NDPRAuditLog
            audit_log = NDPRAuditLog(
                user_id=self.id,
                action='user_anonymized',
                details={
                    'original_email_hash': hashlib.sha256(original_email.encode()).hexdigest() if original_email else None,
                    'original_username_hash': hashlib.sha256(original_username.encode()).hexdigest() if original_username else None,
                    'anonymous_id': self.anonymous_id
                },
                legal_basis='NDPR_Section_2_5_Data_Minimization'
            )
            db.session.add(audit_log)
    
    def generate_anonymous_id(self):
        """Generate anonymous ID like User_8F3E"""
        hash_obj = hashlib.sha256(str(self.id).encode())
        hash_hex = hash_obj.hexdigest()
        return f"User_{hash_hex[:4].upper()}"
    
    def hash_phone_number(self, phone_number):
        """Hash phone number for privacy"""
        if phone_number:
            self.phone_number_hash = hashlib.sha256(phone_number.encode()).hexdigest()
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary with privacy controls"""
        base_dict = {
            'id': self.anonymous_id or self.id,
            'role': self.role.value,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'preferred_contact_method': self.preferred_contact_method
        }
        
        if include_sensitive and not self.is_anonymous:
            base_dict.update({
                'username': self.username,
                'email': self.email,
                'actual_id': self.id
            })
        
        return base_dict
    
    def can_access_admin_features(self):
        """Check if user has admin privileges"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def can_moderate_reports(self):
        """Check if user can moderate project reports"""
        return self.role in [UserRole.MODERATOR, UserRole.NGO_PARTNER, UserRole.ADMIN, UserRole.SUPER_ADMIN]
