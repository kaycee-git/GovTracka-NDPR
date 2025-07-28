"""
Security Routes for GovTracka
Handles encryption, RBAC, biometric auth, and vulnerability scanning
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
import json
from datetime import datetime
import uuid

from src.services.security import (
    encryption_service, rbac_service, biometric_auth_service,
    vulnerability_scanner, data_purge_service
)
from src.models.user import db, User
from src.models.ndpr_compliance import NDPRAuditLog

security_bp = Blueprint('security', __name__, url_prefix='/api/security')

def require_permission(resource: str, action: str):
    """
    Decorator to check user permissions
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user from session or token
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Check permission
            if not rbac_service.check_permission(user.role, resource, action):
                # Log unauthorized access attempt
                audit_log = NDPRAuditLog(
                    action='unauthorized_access_attempt',
                    details={
                        'user_id': user_id,
                        'resource': resource,
                        'action': action,
                        'user_role': user.role
                    },
                    legal_basis='NDPR_Section_2_3_Security_Monitoring',
                    data_category='access_logs'
                )
                db.session.add(audit_log)
                db.session.commit()
                
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@security_bp.route('/encrypt', methods=['POST'])
@require_permission('data', 'encrypt')
def encrypt_data():
    """
    Encrypt sensitive data
    """
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'No content provided for encryption'}), 400
        
        content = data['content']
        user_key = data.get('user_key')
        
        # Encrypt the content
        encryption_result = encryption_service.encrypt_data(content, user_key)
        
        if 'error' in encryption_result:
            return jsonify({'error': encryption_result['error']}), 500
        
        # Log encryption activity
        audit_log = NDPRAuditLog(
            action='data_encryption',
            details={
                'encryption_method': encryption_result['encryption_method'],
                'data_size': len(content),
                'user_key_used': bool(user_key)
            },
            legal_basis='NDPR_Section_2_4_Data_Protection',
            data_category='encrypted_data'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'encrypted_data': encryption_result['encrypted_data'],
            'encryption_method': encryption_result['encryption_method'],
            'timestamp': encryption_result['timestamp']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/decrypt', methods=['POST'])
@require_permission('data', 'decrypt')
def decrypt_data():
    """
    Decrypt sensitive data
    """
    try:
        data = request.get_json()
        
        if not data or 'encrypted_data' not in data:
            return jsonify({'error': 'No encrypted data provided'}), 400
        
        encrypted_data = data['encrypted_data']
        user_key = data.get('user_key')
        
        # Decrypt the content
        decryption_result = encryption_service.decrypt_data(encrypted_data, user_key)
        
        if not decryption_result['success']:
            return jsonify({'error': decryption_result['error']}), 500
        
        # Log decryption activity
        audit_log = NDPRAuditLog(
            action='data_decryption',
            details={
                'user_key_used': bool(user_key),
                'success': decryption_result['success']
            },
            legal_basis='NDPR_Section_2_4_Data_Protection',
            data_category='decrypted_data'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'decrypted_data': decryption_result['decrypted_data'],
            'timestamp': decryption_result['timestamp']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/permissions/<user_id>', methods=['GET'])
@require_permission('user', 'view_permissions')
def get_user_permissions(user_id):
    """
    Get user permissions based on role
    """
    try:
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        permissions = rbac_service.get_user_permissions(user.role)
        
        # Log permission query
        audit_log = NDPRAuditLog(
            action='permission_query',
            details={
                'target_user_id': user_id,
                'user_role': user.role,
                'permissions_count': len(permissions)
            },
            legal_basis='NDPR_Section_2_3_Access_Control',
            data_category='permission_data'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'user_id': user_id,
            'role': user.role,
            'permissions': permissions,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/biometric/challenge', methods=['POST'])
@require_permission('auth', 'biometric')
def create_biometric_challenge():
    """
    Create biometric authentication challenge for admin users
    """
    try:
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        
        # Only allow for admin and super_admin roles
        if user.role not in ['admin', 'super_admin']:
            return jsonify({'error': 'Biometric auth only available for admin users'}), 403
        
        challenge = biometric_auth_service.generate_biometric_challenge(user_id)
        
        # Log biometric challenge creation
        audit_log = NDPRAuditLog(
            action='biometric_challenge_created',
            details={
                'challenge_id': challenge['challenge_id'],
                'user_role': user.role
            },
            legal_basis='NDPR_Section_2_3_Authentication',
            data_category='biometric_auth'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify(challenge)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/biometric/verify', methods=['POST'])
def verify_biometric():
    """
    Verify biometric authentication response
    """
    try:
        data = request.get_json()
        
        if not data or 'challenge_id' not in data or 'biometric_data' not in data:
            return jsonify({'error': 'Missing challenge_id or biometric_data'}), 400
        
        challenge_id = data['challenge_id']
        biometric_data = data['biometric_data']
        
        verification_result = biometric_auth_service.verify_biometric_response(
            challenge_id, biometric_data
        )
        
        # Log biometric verification attempt
        audit_log = NDPRAuditLog(
            action='biometric_verification',
            details={
                'challenge_id': challenge_id,
                'success': verification_result['success']
            },
            legal_basis='NDPR_Section_2_3_Authentication',
            data_category='biometric_auth'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        if verification_result['success']:
            # Store auth token in session
            session['biometric_auth_token'] = verification_result['auth_token']
            session['biometric_auth_expires'] = verification_result['expires_in']
        
        return jsonify(verification_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/scan/input', methods=['POST'])
def scan_input():
    """
    Scan user input for security vulnerabilities
    """
    try:
        data = request.get_json()
        
        if not data or 'input_data' not in data:
            return jsonify({'error': 'No input data provided for scanning'}), 400
        
        input_data = data['input_data']
        input_type = data.get('input_type', 'general')
        
        scan_result = vulnerability_scanner.scan_input(input_data, input_type)
        
        # Log vulnerability scan
        audit_log = NDPRAuditLog(
            action='vulnerability_scan',
            details={
                'input_type': input_type,
                'vulnerabilities_found': scan_result['vulnerabilities_found'],
                'risk_level': scan_result['risk_level']
            },
            legal_basis='NDPR_Section_2_3_Security_Monitoring',
            data_category='security_scans'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify(scan_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/scan/file', methods=['POST'])
def scan_file():
    """
    Scan uploaded file for security issues
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided for scanning'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = file.filename
        file_content = file.read()
        
        scan_result = vulnerability_scanner.scan_file_upload(filename, file_content)
        
        # Log file scan
        audit_log = NDPRAuditLog(
            action='file_security_scan',
            details={
                'filename': filename,
                'file_size': len(file_content),
                'issues_found': scan_result['issues_found'],
                'risk_level': scan_result['risk_level']
            },
            legal_basis='NDPR_Section_2_3_Security_Monitoring',
            data_category='file_scans'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify(scan_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/purge/schedule', methods=['POST'])
@require_permission('data', 'schedule_purge')
def schedule_data_purge():
    """
    Schedule data purge based on retention policy
    """
    try:
        data = request.get_json()
        
        if not data or 'data_type' not in data:
            return jsonify({'error': 'No data type specified'}), 400
        
        data_type = data['data_type']
        user_id = data.get('user_id')
        
        purge_result = data_purge_service.schedule_data_purge(data_type, user_id)
        
        if not purge_result.get('scheduled'):
            return jsonify({'error': purge_result.get('error')}), 400
        
        # Log purge scheduling
        audit_log = NDPRAuditLog(
            action='data_purge_scheduled',
            details={
                'data_type': data_type,
                'target_user_id': user_id,
                'job_id': purge_result['purge_job']['job_id']
            },
            legal_basis='NDPR_Section_2_5_Data_Retention',
            data_category='data_purge'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify(purge_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/purge/immediate', methods=['POST'])
@require_permission('data', 'immediate_purge')
def execute_immediate_purge():
    """
    Execute immediate data purge (right to be forgotten)
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'data_types' not in data:
            return jsonify({'error': 'Missing user_id or data_types'}), 400
        
        user_id = data['user_id']
        data_types = data['data_types']
        
        if not isinstance(data_types, list):
            return jsonify({'error': 'data_types must be a list'}), 400
        
        purge_result = data_purge_service.execute_immediate_purge(user_id, data_types)
        
        # Log immediate purge
        audit_log = NDPRAuditLog(
            action='immediate_data_purge',
            details={
                'target_user_id': user_id,
                'data_types': data_types,
                'records_purged': purge_result['purged_records'],
                'success': purge_result['success']
            },
            legal_basis='NDPR_Section_2_6_Right_To_Be_Forgotten',
            data_category='data_purge'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify(purge_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/audit/logs', methods=['GET'])
@require_permission('audit', 'view')
def get_audit_logs():
    """
    Get security audit logs
    """
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        action_filter = request.args.get('action')
        
        # Build query
        query = NDPRAuditLog.query
        
        if action_filter:
            query = query.filter(NDPRAuditLog.action.contains(action_filter))
        
        # Get logs with pagination
        logs = query.order_by(NDPRAuditLog.created_at.desc()).offset(offset).limit(limit).all()
        
        audit_data = []
        for log in logs:
            audit_data.append({
                'id': log.id,
                'action': log.action,
                'details': json.loads(log.details) if log.details else {},
                'legal_basis': log.legal_basis,
                'data_category': log.data_category,
                'created_at': log.created_at.isoformat()
            })
        
        # Log audit log access
        audit_log = NDPRAuditLog(
            action='audit_logs_accessed',
            details={
                'logs_retrieved': len(audit_data),
                'action_filter': action_filter
            },
            legal_basis='NDPR_Section_2_3_Audit_Trail',
            data_category='audit_access'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'logs': audit_data,
            'total_retrieved': len(audit_data),
            'offset': offset,
            'limit': limit,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_bp.route('/health', methods=['GET'])
def security_health_check():
    """
    Health check for security services
    """
    try:
        # Test encryption service
        test_data = "test_encryption_data"
        encryption_test = encryption_service.encrypt_data(test_data)
        encryption_healthy = 'encrypted_data' in encryption_test
        
        # Test RBAC service
        rbac_test = rbac_service.check_permission('citizen', 'report', 'create')
        rbac_healthy = rbac_test is True
        
        # Test vulnerability scanner
        vuln_test = vulnerability_scanner.scan_input("test input")
        vuln_healthy = 'safe' in vuln_test
        
        # Test data purge service
        purge_test = data_purge_service.schedule_data_purge('user_data')
        purge_healthy = purge_test.get('scheduled', False)
        
        overall_health = all([encryption_healthy, rbac_healthy, vuln_healthy, purge_healthy])
        
        return jsonify({
            'status': 'healthy' if overall_health else 'degraded',
            'services': {
                'encryption': 'healthy' if encryption_healthy else 'unhealthy',
                'rbac': 'healthy' if rbac_healthy else 'unhealthy',
                'vulnerability_scanner': 'healthy' if vuln_healthy else 'unhealthy',
                'data_purge': 'healthy' if purge_healthy else 'unhealthy',
                'biometric_auth': 'healthy'  # Always healthy in simulation
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

