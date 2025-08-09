import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS

# Import all models to ensure they are registered with SQLAlchemy
from src.models.user import db, User, UserRole
from src.models.ndpr_compliance import (
    NDPRConsent, DataAnonymization, RightToBeForgotten, 
    NDPRAuditLog, DataLocalization
)
from src.models.project_report import (
    ProjectReport, ProjectEvidence, ReportVerification, 
    AIAnalysis, CommunityVote
)

# Import routes
from src.routes.user import user_bp
from src.routes.ndpr_compliance import ndpr_bp
from src.routes.project_reports import reports_bp
from src.routes.ussd import ussd_bp
from src.routes.ai_analysis import ai_bp
from src.routes.security import security_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# NDPR Compliance: Enhanced security configuration
app.config['SECRET_KEY'] = 'GovTracka_NDPR_Compliant_2024_#$%^&*'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Enable CORS for frontend-backend interaction
CORS(app, origins=['*'], supports_credentials=True)

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(ndpr_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(ussd_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(security_bp)

# Database configuration with NDPR compliance
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize database
db.init_app(app)

# Create admin user on first run
def create_admin_user():
    """Create super admin user as specified in requirements"""
    admin_email = "odenigbokelechi2@gmail.com"
    existing_admin = User.query.filter_by(email=admin_email).first()
    
    if not existing_admin:
        admin_user = User(
            email=admin_email,
            username="super_admin",
            role=UserRole.SUPER_ADMIN,
            is_verified=True,
            is_active=True,
            data_retention_consent=True
        )
        
        # Log admin creation for NDPR compliance
        audit_log = NDPRAuditLog(
            user_id=admin_user.id,
            action='admin_user_created',
            details={
                'role': 'super_admin',
                'email': admin_email,
                'creation_method': 'system_initialization'
            },
            legal_basis='NDPR_Section_2_3_Legitimate_Interest'
        )
        
        db.session.add(admin_user)
        db.session.add(audit_log)
        db.session.commit()
        print(f"✅ Super admin user created: {admin_email}")

with app.app_context():
    db.create_all()
    create_admin_user()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend files with NDPR compliance headers"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    # Add NDPR compliance headers
    def add_ndpr_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        return response

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        response = send_from_directory(static_folder_path, path)
        return add_ndpr_headers(response)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            response = send_from_directory(static_folder_path, 'index.html')
            return add_ndpr_headers(response)
        else:
            return "index.html not found", 404

@app.errorhandler(404)
def not_found(error):
    """NDPR compliant 404 handler"""
    return {"error": "Resource not found", "ndpr_notice": "No personal data was processed in this request"}, 404

@app.errorhandler(500)
def internal_error(error):
    """NDPR compliant error handler with audit logging"""
    audit_log = NDPRAuditLog(
        action='system_error',
        details={'error_type': '500_internal_server_error'},
        legal_basis='NDPR_Section_2_6_Security_Incident'
    )
    db.session.add(audit_log)
    db.session.commit()
    
    return {"error": "Internal server error", "ndpr_notice": "Error logged for security compliance"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
