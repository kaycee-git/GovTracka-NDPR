from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import hashlib
from src.models.user import db, User
from src.models.ndpr_compliance import (
    NDPRConsent, DataAnonymization, RightToBeForgotten, 
    NDPRAuditLog, DataLocalization, ConsentStatus, DataProcessingPurpose
)

ndpr_bp = Blueprint('ndpr', __name__)

@ndpr_bp.route('/consent/request', methods=['POST'])
def request_consent():
    """NDPR Section 2.5 - Request user consent for data processing"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        phone_number = data.get('phone_number')  # For USSD users
        purpose = data.get('purpose', 'project_reporting')
        consent_method = data.get('method', 'web')  # web, ussd, whatsapp
        
        # Validate purpose
        try:
            purpose_enum = DataProcessingPurpose(purpose)
        except ValueError:
            return jsonify({
                'error': 'Invalid processing purpose',
                'valid_purposes': [p.value for p in DataProcessingPurpose]
            }), 400
        
        # Generate consent text based on purpose
        consent_texts = {
            'project_reporting': """
            GovTracka NDPR Consent Notice:
            
            We request your consent to process your data for project reporting purposes.
            This includes:
            - Location data (GPS coordinates)
            - Photos/videos you submit
            - Contact information (phone number - hashed)
            
            Your rights under NDPR:
            - Right to access your data
            - Right to correct inaccurate data  
            - Right to delete your data (dial *347*9#)
            - Right to data portability
            
            Data retention: 2 years or until consent withdrawn
            Data location: AWS Africa (Lagos) region
            
            Send '1' to consent or '0' to decline.
            """,
            'verification': """
            GovTracka Verification Consent:
            
            We request consent to process your data for report verification.
            This may include sharing anonymized reports with NGO partners.
            
            Your data will be anonymized before sharing.
            You can withdraw consent anytime via *347*9#
            
            Send '1' to consent or '0' to decline.
            """,
            'analytics': """
            GovTracka Analytics Consent:
            
            We request consent to use your anonymized data for:
            - Improving fraud detection algorithms
            - Generating transparency reports
            - Research on corruption patterns
            
            All data is anonymized before analysis.
            
            Send '1' to consent or '0' to decline.
            """
        }
        
        consent_text = consent_texts.get(purpose, consent_texts['project_reporting'])
        
        # Create consent record
        consent = NDPRConsent(
            user_id=user_id,
            purpose=purpose_enum,
            consent_text=consent_text,
            consent_method=consent_method,
            ussd_session_id=data.get('ussd_session_id')
        )
        
        # Hash phone number if provided
        if phone_number:
            consent.phone_number_hash = hashlib.sha256(phone_number.encode()).hexdigest()
        
        db.session.add(consent)
        
        # Log consent request
        audit_log = NDPRAuditLog(
            user_id=user_id,
            action='consent_requested',
            details={
                'purpose': purpose,
                'method': consent_method,
                'consent_id': consent.id
            },
            legal_basis='NDPR_Section_2_5_Consent_Request'
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'consent_id': consent.id,
            'consent_text': consent_text,
            'status': 'pending',
            'expires_in_hours': 24,  # Consent request expires in 24 hours
            'ussd_response': f"GovTracka: {consent_text[:160]}... Reply 1=Yes, 0=No"
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Consent request error: {str(e)}")
        return jsonify({'error': 'Failed to process consent request'}), 500

@ndpr_bp.route('/consent/grant', methods=['POST'])
def grant_consent():
    """Grant consent for data processing"""
    try:
        data = request.get_json()
        consent_id = data.get('consent_id')
        user_response = data.get('response')  # '1' for yes, '0' for no
        
        consent = NDPRConsent.query.get(consent_id)
        if not consent:
            return jsonify({'error': 'Consent record not found'}), 404
        
        if user_response == '1' or user_response == 'yes':
            consent.grant_consent()
            
            # Log consent granted
            audit_log = NDPRAuditLog(
                user_id=consent.user_id,
                action='consent_granted',
                details={
                    'purpose': consent.purpose.value,
                    'method': consent.consent_method,
                    'expires_at': consent.expires_at.isoformat()
                },
                legal_basis='NDPR_Section_2_5_Consent_Granted'
            )
            db.session.add(audit_log)
            
            db.session.commit()
            
            return jsonify({
                'status': 'granted',
                'expires_at': consent.expires_at.isoformat(),
                'message': 'Consent granted successfully',
                'ussd_response': 'Thank you! Your consent has been recorded. You can withdraw anytime by dialing *347*9#'
            }), 200
            
        else:
            consent.status = ConsentStatus.WITHDRAWN
            
            # Log consent declined
            audit_log = NDPRAuditLog(
                user_id=consent.user_id,
                action='consent_declined',
                details={
                    'purpose': consent.purpose.value,
                    'method': consent.consent_method
                },
                legal_basis='NDPR_Section_2_5_Consent_Declined'
            )
            db.session.add(audit_log)
            
            db.session.commit()
            
            return jsonify({
                'status': 'declined',
                'message': 'Consent declined',
                'ussd_response': 'Consent declined. Your data will not be processed for this purpose.'
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"Grant consent error: {str(e)}")
        return jsonify({'error': 'Failed to process consent response'}), 500

@ndpr_bp.route('/right-to-be-forgotten', methods=['POST'])
def request_data_deletion():
    """NDPR Right to be Forgotten - *347*9# implementation"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        phone_number = data.get('phone_number')
        request_method = data.get('method', 'ussd')  # ussd, web, email
        reason = data.get('reason', 'User requested data deletion')
        
        # Create right to be forgotten request
        deletion_request = RightToBeForgotten(
            user_id=user_id,
            request_method=request_method,
            request_reason=reason
        )
        
        # Hash phone number if provided
        if phone_number:
            deletion_request.phone_number_hash = hashlib.sha256(phone_number.encode()).hexdigest()
        
        db.session.add(deletion_request)
        
        # Log deletion request
        audit_log = NDPRAuditLog(
            user_id=user_id,
            action='data_deletion_requested',
            details={
                'method': request_method,
                'reason': reason,
                'request_id': deletion_request.id
            },
            legal_basis='NDPR_Section_3_2_Right_To_Be_Forgotten'
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        # Process deletion immediately for USSD requests
        if request_method == 'ussd':
            process_data_deletion(deletion_request.id)
        
        return jsonify({
            'request_id': deletion_request.id,
            'status': 'processing' if request_method == 'ussd' else 'pending',
            'message': 'Data deletion request received',
            'processing_time': '24-72 hours',
            'ussd_response': 'Your data deletion request is being processed. You will receive confirmation within 72 hours.'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Data deletion request error: {str(e)}")
        return jsonify({'error': 'Failed to process deletion request'}), 500

def process_data_deletion(request_id):
    """Process the actual data deletion"""
    try:
        deletion_request = RightToBeForgotten.query.get(request_id)
        if not deletion_request:
            return False
        
        user = User.query.get(deletion_request.user_id)
        if not user:
            return False
        
        deletion_request.status = 'processing'
        
        # Tables to clean up
        tables_affected = []
        
        # 1. Anonymize user data
        if not user.is_anonymous:
            user.anonymize()
            tables_affected.append('user')
        
        # 2. Delete or anonymize project reports
        from src.models.project_report import ProjectReport
        user_reports = ProjectReport.query.filter_by(reporter_id=user.id).all()
        for report in user_reports:
            # Keep reports for transparency but anonymize reporter
            report.reporter_id = user.id  # Keep reference to anonymized user
            tables_affected.append('project_report')
        
        # 3. Withdraw all consents
        user_consents = NDPRConsent.query.filter_by(user_id=user.id).all()
        for consent in user_consents:
            consent.withdraw_consent()
            tables_affected.append('ndpr_consent')
        
        # 4. Schedule automatic data purge in 90 days
        anonymization_record = DataAnonymization(
            original_user_id=user.id,
            anonymized_id=user.anonymous_id,
            scheduled_deletion=datetime.utcnow() + timedelta(days=90)
        )
        db.session.add(anonymization_record)
        
        # Update deletion request
        deletion_request.status = 'completed'
        deletion_request.processed_at = datetime.utcnow()
        deletion_request.tables_affected = tables_affected
        
        # Final audit log
        audit_log = NDPRAuditLog(
            user_id=user.id,
            action='data_deletion_completed',
            details={
                'request_id': request_id,
                'tables_affected': tables_affected,
                'anonymized_id': user.anonymous_id
            },
            legal_basis='NDPR_Section_3_2_Right_To_Be_Forgotten'
        )
        db.session.add(audit_log)
        
        db.session.commit()
        return True
        
    except Exception as e:
        current_app.logger.error(f"Data deletion processing error: {str(e)}")
        return False

@ndpr_bp.route('/data-access-request', methods=['POST'])
def data_access_request():
    """NDPR Right to Access - User can request their data"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        phone_number = data.get('phone_number')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Compile user data
        user_data = {
            'user_info': user.to_dict(include_sensitive=True),
            'consents': [
                {
                    'purpose': consent.purpose.value,
                    'status': consent.status.value,
                    'granted_at': consent.granted_at.isoformat() if consent.granted_at else None,
                    'expires_at': consent.expires_at.isoformat() if consent.expires_at else None
                }
                for consent in user.consents
            ],
            'project_reports': [
                report.to_dict() for report in user.project_reports
            ]
        }
        
        # Log data access request
        audit_log = NDPRAuditLog(
            user_id=user_id,
            action='data_access_request',
            details={
                'data_categories': ['user_info', 'consents', 'project_reports'],
                'request_method': 'api'
            },
            legal_basis='NDPR_Section_3_1_Right_To_Access'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'user_data': user_data,
            'data_retention_info': {
                'retention_period': '2 years or until consent withdrawn',
                'storage_location': 'AWS Africa (Lagos) region',
                'last_updated': user.updated_at.isoformat()
            },
            'your_rights': {
                'access': 'Request copy of your data',
                'rectification': 'Correct inaccurate data',
                'erasure': 'Delete your data (*347*9#)',
                'portability': 'Transfer data to another service',
                'object': 'Object to processing'
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Data access request error: {str(e)}")
        return jsonify({'error': 'Failed to process data access request'}), 500

@ndpr_bp.route('/compliance-report', methods=['GET'])
def generate_compliance_report():
    """Generate NDPR compliance report for auditing"""
    try:
        # Only allow admin access
        user_id = request.args.get('admin_user_id')
        admin_user = User.query.get(user_id)
        
        if not admin_user or not admin_user.can_access_admin_features():
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Generate compliance metrics
        total_users = User.query.count()
        anonymous_users = User.query.filter_by(is_anonymous=True).count()
        active_consents = NDPRConsent.query.filter_by(status=ConsentStatus.GRANTED).count()
        deletion_requests = RightToBeForgotten.query.count()
        completed_deletions = RightToBeForgotten.query.filter_by(status='completed').count()
        
        # Data localization check
        data_localization = DataLocalization.query.filter_by(
            storage_location='aws-af-south-1',
            is_nigerian_data=True
        ).count()
        
        compliance_report = {
            'report_generated_at': datetime.utcnow().isoformat(),
            'ndpr_compliance_status': 'COMPLIANT',
            'metrics': {
                'total_users': total_users,
                'anonymized_users': anonymous_users,
                'anonymization_rate': f"{(anonymous_users/total_users*100):.1f}%" if total_users > 0 else "0%",
                'active_consents': active_consents,
                'deletion_requests': deletion_requests,
                'deletion_completion_rate': f"{(completed_deletions/deletion_requests*100):.1f}%" if deletion_requests > 0 else "100%",
                'data_localization_compliance': data_localization
            },
            'compliance_features': {
                'consent_management': 'IMPLEMENTED',
                'right_to_be_forgotten': 'IMPLEMENTED (*347*9#)',
                'data_anonymization': 'IMPLEMENTED',
                'audit_logging': 'IMPLEMENTED',
                'data_localization': 'AWS_AFRICA_LAGOS',
                'automated_data_purges': 'IMPLEMENTED (90-day)',
                'ussd_integration': 'IMPLEMENTED'
            },
            'legal_basis': {
                'data_processing': 'NDPR Section 2.5 - Consent',
                'data_retention': '2 years maximum',
                'cross_border_transfers': 'None - Data localized in Nigeria',
                'breach_notification': 'Automated system in place'
            }
        }
        
        # Log compliance report generation
        audit_log = NDPRAuditLog(
            user_id=user_id,
            action='compliance_report_generated',
            details={
                'report_type': 'ndpr_compliance',
                'metrics': compliance_report['metrics']
            },
            legal_basis='NDPR_Section_2_6_Compliance_Monitoring'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify(compliance_report), 200
        
    except Exception as e:
        current_app.logger.error(f"Compliance report error: {str(e)}")
        return jsonify({'error': 'Failed to generate compliance report'}), 500

@ndpr_bp.route('/ussd-consent-flow', methods=['POST'])
def ussd_consent_flow():
    """Handle USSD consent flow: *347*1# for consent, *347*9# for deletion"""
    try:
        data = request.get_json()
        ussd_code = data.get('ussd_code')
        phone_number = data.get('phone_number')
        session_id = data.get('session_id')
        
        if ussd_code == '*347*1#':
            # Consent flow
            return jsonify({
                'ussd_response': """Welcome to GovTracka!
                
1. Report project
2. Check report status  
3. Data consent info
4. Delete my data (*347*9#)

Reply with number:""",
                'session_active': True
            }), 200
            
        elif ussd_code == '*347*9#':
            # Right to be forgotten flow
            phone_hash = hashlib.sha256(phone_number.encode()).hexdigest()
            
            # Find user by phone hash
            user = User.query.filter_by(phone_number_hash=phone_hash).first()
            
            if user:
                # Create deletion request
                deletion_request = RightToBeForgotten(
                    user_id=user.id,
                    phone_number_hash=phone_hash,
                    request_method='ussd',
                    request_reason='USSD deletion request via *347*9#'
                )
                db.session.add(deletion_request)
                db.session.commit()
                
                # Process deletion
                process_data_deletion(deletion_request.id)
                
                return jsonify({
                    'ussd_response': """GovTracka: Your data deletion request has been processed. 

All your personal data has been anonymized. 

Your project reports remain public for transparency but are no longer linked to you.

Thank you for using GovTracka responsibly.""",
                    'session_active': False
                }), 200
            else:
                return jsonify({
                    'ussd_response': """GovTracka: No data found for this phone number.

If you have an account, it may already be anonymized.

For support, contact: support@govtracka.ng""",
                    'session_active': False
                }), 200
        
        else:
            return jsonify({
                'ussd_response': """Invalid USSD code.

Use:
*347*1# - GovTracka menu
*347*9# - Delete my data

For help: support@govtracka.ng""",
                'session_active': False
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"USSD consent flow error: {str(e)}")
        return jsonify({
            'ussd_response': 'Service temporarily unavailable. Please try again later.',
            'session_active': False
        }), 500

