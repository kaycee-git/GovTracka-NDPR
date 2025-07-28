from src.models.user import db
from datetime import datetime, timedelta
import hashlib
import uuid
from enum import Enum

class ConsentStatus(Enum):
    PENDING = "pending"
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"

class DataProcessingPurpose(Enum):
    PROJECT_REPORTING = "project_reporting"
    VERIFICATION = "verification"
    ANALYTICS = "analytics"
    COMMUNICATION = "communication"

class NDPRConsent(db.Model):
    """NDPR Section 2.5 - Consent Management"""
    __tablename__ = 'ndpr_consent'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    phone_number_hash = db.Column(db.String(64), nullable=True)  # Hashed phone for USSD users
    
    # Consent details
    purpose = db.Column(db.Enum(DataProcessingPurpose), nullable=False)
    status = db.Column(db.Enum(ConsentStatus), default=ConsentStatus.PENDING)
    consent_text = db.Column(db.Text, nullable=False)
    
    # Timestamps
    granted_at = db.Column(db.DateTime, nullable=True)
    withdrawn_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # USSD consent tracking
    ussd_session_id = db.Column(db.String(100), nullable=True)
    consent_method = db.Column(db.String(20), default='web')  # 'web', 'ussd', 'whatsapp'
    
    def __repr__(self):
        return f'<NDPRConsent {self.id} - {self.purpose.value} - {self.status.value}>'
    
    def grant_consent(self):
        """Grant consent with automatic expiry (2 years as per NDPR)"""
        self.status = ConsentStatus.GRANTED
        self.granted_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(days=730)  # 2 years
        self.updated_at = datetime.utcnow()
    
    def withdraw_consent(self):
        """Withdraw consent - triggers right to be forgotten"""
        self.status = ConsentStatus.WITHDRAWN
        self.withdrawn_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def is_valid(self):
        """Check if consent is currently valid"""
        if self.status != ConsentStatus.GRANTED:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            self.status = ConsentStatus.EXPIRED
            return False
        return True

class DataAnonymization(db.Model):
    """NDPR Section 2.5 - Data Anonymization Records"""
    __tablename__ = 'data_anonymization'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_user_id = db.Column(db.String(36), nullable=False)
    anonymized_id = db.Column(db.String(20), nullable=False, unique=True)  # e.g., User_8F3E
    
    # Anonymization details
    anonymization_method = db.Column(db.String(50), default='hash_truncate')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Data retention
    retention_period_days = db.Column(db.Integer, default=90)
    scheduled_deletion = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<DataAnonymization {self.anonymized_id}>'
    
    @staticmethod
    def generate_anonymous_id(user_id):
        """Generate anonymous ID like User_8F3E"""
        hash_obj = hashlib.sha256(str(user_id).encode())
        hash_hex = hash_obj.hexdigest()
        return f"User_{hash_hex[:4].upper()}"

class RightToBeForgotten(db.Model):
    """NDPR Right to be Forgotten Implementation"""
    __tablename__ = 'right_to_be_forgotten'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)
    phone_number_hash = db.Column(db.String(64), nullable=True)  # For USSD requests
    
    # Request details
    request_method = db.Column(db.String(20), nullable=False)  # 'web', 'ussd', 'email'
    request_reason = db.Column(db.Text, nullable=True)
    
    # Processing status
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    # Data deletion tracking
    tables_affected = db.Column(db.JSON, nullable=True)  # List of tables where data was deleted
    backup_reference = db.Column(db.String(100), nullable=True)  # For legal compliance
    
    def __repr__(self):
        return f'<RightToBeForgotten {self.id} - {self.status}>'
    
    def process_deletion(self):
        """Process the right to be forgotten request"""
        self.status = 'processing'
        self.processed_at = datetime.utcnow()
        # Implementation would include actual data deletion logic

class NDPRAuditLog(db.Model):
    """NDPR Compliance Audit Trail"""
    __tablename__ = 'ndpr_audit_log'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Compliance fields
    legal_basis = db.Column(db.String(100), nullable=True)  # NDPR legal basis for processing
    data_category = db.Column(db.String(50), nullable=True)  # Type of data processed
    
    def __repr__(self):
        return f'<NDPRAuditLog {self.action} at {self.timestamp}>'

class DataLocalization(db.Model):
    """AWS Lagos Region Data Localization Tracking"""
    __tablename__ = 'data_localization'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    data_type = db.Column(db.String(50), nullable=False)  # 'user_data', 'project_reports', 'images'
    storage_location = db.Column(db.String(100), default='aws-af-south-1')  # AWS Africa (Cape Town)
    
    # Compliance tracking
    is_nigerian_data = db.Column(db.Boolean, default=True)
    cross_border_transfer = db.Column(db.Boolean, default=False)
    transfer_legal_basis = db.Column(db.String(200), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DataLocalization {self.data_type} in {self.storage_location}>'

