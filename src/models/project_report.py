from src.models.user import db
from datetime import datetime
import uuid
import hashlib
import json
from enum import Enum

class ProjectType(Enum):
    SCHOOL = "school"
    ROAD = "road"
    CLINIC = "clinic"
    HOSPITAL = "hospital"
    WATER_PROJECT = "water_project"
    BRIDGE = "bridge"
    MARKET = "market"
    OTHER = "other"

class ReportStatus(Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    REJECTED = "rejected"
    ESCALATED = "escalated"

class EvidenceType(Enum):
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"

class ProjectReport(db.Model):
    """Core project reporting model"""
    __tablename__ = 'project_report'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reporter_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    # Project details
    project_name = db.Column(db.String(200), nullable=False)
    project_type = db.Column(db.Enum(ProjectType), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Location data (geotagged)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_name = db.Column(db.String(200), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    lga = db.Column(db.String(100), nullable=True)  # Local Government Area
    
    # Financial information
    reported_budget = db.Column(db.BigInteger, nullable=True)  # In Naira (kobo)
    actual_cost_estimate = db.Column(db.BigInteger, nullable=True)
    contractor_name = db.Column(db.String(200), nullable=True)
    
    # Status and verification
    status = db.Column(db.Enum(ReportStatus), default=ReportStatus.PENDING)
    verification_score = db.Column(db.Float, default=0.0)  # AI-generated score 0-100
    community_votes = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    # Submission method tracking
    submission_method = db.Column(db.String(20), default='web')  # 'web', 'ussd', 'whatsapp'
    ussd_session_id = db.Column(db.String(100), nullable=True)
    
    # Blockchain simulation
    blockchain_hash = db.Column(db.String(64), nullable=True)
    blockchain_timestamp = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    evidence_files = db.relationship('ProjectEvidence', backref='report', lazy=True, cascade='all, delete-orphan')
    verifications = db.relationship('ReportVerification', backref='report', lazy=True, cascade='all, delete-orphan')
    ai_analysis = db.relationship('AIAnalysis', backref='report', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ProjectReport {self.project_name} - {self.status.value}>'
    
    def generate_blockchain_hash(self):
        """Generate blockchain hash for immutable record"""
        data_string = f"{self.id}{self.project_name}{self.latitude}{self.longitude}{self.created_at}"
        self.blockchain_hash = hashlib.sha256(data_string.encode()).hexdigest()
        self.blockchain_timestamp = datetime.utcnow()
    
    def calculate_verification_score(self):
        """Calculate AI-based verification score"""
        score = 0.0
        
        # Base score for having evidence
        if self.evidence_files:
            score += 30.0
        
        # Location verification
        if self.latitude and self.longitude:
            score += 20.0
        
        # Community validation
        if self.community_votes > 0:
            score += min(self.community_votes * 5, 25.0)
        
        # Professional verification
        verified_count = len([v for v in self.verifications if v.is_verified])
        score += min(verified_count * 15, 25.0)
        
        self.verification_score = min(score, 100.0)
        return self.verification_score
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'project_name': self.project_name,
            'project_type': self.project_type.value,
            'description': self.description,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'location_name': self.location_name,
                'state': self.state,
                'lga': self.lga
            },
            'financial': {
                'reported_budget': self.reported_budget,
                'actual_cost_estimate': self.actual_cost_estimate,
                'contractor_name': self.contractor_name
            },
            'status': self.status.value,
            'verification_score': self.verification_score,
            'community_votes': self.community_votes,
            'created_at': self.created_at.isoformat(),
            'submission_method': self.submission_method,
            'blockchain_hash': self.blockchain_hash,
            'evidence_count': len(self.evidence_files),
            'reporter_id': self.reporter.anonymous_id if self.reporter.is_anonymous else self.reporter.id
        }

class ProjectEvidence(db.Model):
    """Evidence files for project reports"""
    __tablename__ = 'project_evidence'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('project_report.id'), nullable=False)
    
    # File details
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    file_type = db.Column(db.Enum(EvidenceType), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    
    # File metadata
    file_metadata = db.Column(db.JSON, nullable=True)  # EXIF data, GPS, timestamp
    is_verified = db.Column(db.Boolean, default=False)
    ai_analysis_result = db.Column(db.JSON, nullable=True)
    
    # Privacy and security
    is_anonymized = db.Column(db.Boolean, default=False)
    encryption_key = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<ProjectEvidence {self.file_name} - {self.file_type.value}>'
    
    def extract_gps_data(self):
        """Extract GPS coordinates from image metadata"""
        if self.file_metadata and 'gps' in self.file_metadata:
            return {
                'latitude': self.file_metadata['gps'].get('latitude'),
                'longitude': self.file_metadata['gps'].get('longitude')
            }
        return None
    
    def anonymize_faces(self):
        """Mark evidence as having faces anonymized"""
        self.is_anonymized = True
        if not self.file_metadata:
            self.file_metadata = {}
        self.file_metadata['faces_anonymized'] = True

class ReportVerification(db.Model):
    """Professional verification of project reports"""
    __tablename__ = 'report_verification'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('project_report.id'), nullable=False)
    verifier_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    # Verification details
    is_verified = db.Column(db.Boolean, nullable=False)
    verification_notes = db.Column(db.Text, nullable=True)
    confidence_level = db.Column(db.Integer, nullable=True)  # 1-10 scale
    
    # Verifier information
    verifier_organization = db.Column(db.String(200), nullable=True)  # e.g., "BudgIT", "SERAP"
    verification_method = db.Column(db.String(100), nullable=True)  # e.g., "field_visit", "document_review"
    
    # Timestamps
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    verifier = db.relationship('User', backref='verifications')
    
    def __repr__(self):
        return f'<ReportVerification {self.report_id} - {self.is_verified}>'

class AIAnalysis(db.Model):
    """AI analysis results for project reports"""
    __tablename__ = 'ai_analysis'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('project_report.id'), nullable=False)
    
    # Analysis results
    anomaly_score = db.Column(db.Float, default=0.0)  # 0-100, higher = more suspicious
    fraud_indicators = db.Column(db.JSON, nullable=True)  # List of detected issues
    image_authenticity_score = db.Column(db.Float, nullable=True)
    
    # Specific checks
    budget_anomaly = db.Column(db.Boolean, default=False)
    location_mismatch = db.Column(db.Boolean, default=False)
    duplicate_project = db.Column(db.Boolean, default=False)
    
    # AI model information
    model_version = db.Column(db.String(50), nullable=True)
    analysis_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AIAnalysis {self.report_id} - Score: {self.anomaly_score}>'
    
    def add_fraud_indicator(self, indicator_type, description, confidence):
        """Add a fraud indicator to the analysis"""
        if not self.fraud_indicators:
            self.fraud_indicators = []
        
        self.fraud_indicators.append({
            'type': indicator_type,
            'description': description,
            'confidence': confidence,
            'detected_at': datetime.utcnow().isoformat()
        })

class CommunityVote(db.Model):
    """Community voting on project reports"""
    __tablename__ = 'community_vote'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('project_report.id'), nullable=False)
    voter_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    # Vote details
    vote_type = db.Column(db.String(20), nullable=False)  # 'support', 'dispute', 'additional_info'
    comment = db.Column(db.Text, nullable=True)
    
    # Voting method
    vote_method = db.Column(db.String(20), default='web')  # 'web', 'ussd', 'whatsapp'
    
    # Timestamps
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    voter = db.relationship('User', backref='votes')
    
    def __repr__(self):
        return f'<CommunityVote {self.vote_type} on {self.report_id}>'

