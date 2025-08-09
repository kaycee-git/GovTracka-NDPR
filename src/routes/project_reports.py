from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from src.models.user import db, User
from src.models.project_report import (
    ProjectReport, ProjectEvidence, ReportVerification, 
    AIAnalysis, CommunityVote, ProjectType, ReportStatus, EvidenceType
)
from src.models.ndpr_compliance import NDPRAuditLog

reports_bp = Blueprint('reports', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'pdf', 'doc', 'docx'}
UPLOAD_FOLDER = '/tmp/govtracka_uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@reports_bp.route('/submit', methods=['POST'])
def submit_project_report():
    """Submit a new project report with evidence"""
    try:
        ensure_upload_folder()
        
        # Get form data
        reporter_id = request.form.get('reporter_id')
        project_name = request.form.get('project_name')
        project_type = request.form.get('project_type')
        description = request.form.get('description')
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        location_name = request.form.get('location_name')
        state = request.form.get('state')
        lga = request.form.get('lga')
        reported_budget = request.form.get('reported_budget', type=int)
        contractor_name = request.form.get('contractor_name')
        submission_method = request.form.get('submission_method', 'web')
        
        # Validate required fields
        if not all([reporter_id, project_name, project_type, description]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate project type
        try:
            project_type_enum = ProjectType(project_type)
        except ValueError:
            return jsonify({
                'error': 'Invalid project type',
                'valid_types': [t.value for t in ProjectType]
            }), 400
        
        # Verify reporter exists
        reporter = User.query.get(reporter_id)
        if not reporter:
            return jsonify({'error': 'Reporter not found'}), 404
        
        # Create project report
        report = ProjectReport(
            reporter_id=reporter_id,
            project_name=project_name,
            project_type=project_type_enum,
            description=description,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            state=state,
            lga=lga,
            reported_budget=reported_budget * 100 if reported_budget else None,  # Convert to kobo
            contractor_name=contractor_name,
            submission_method=submission_method
        )
        
        # Generate blockchain hash for immutability
        report.generate_blockchain_hash()
        
        db.session.add(report)
        db.session.flush()  # Get the report ID
        
        # Handle file uploads
        uploaded_files = []
        files = request.files.getlist('evidence_files')
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                
                # Determine evidence type
                file_ext = filename.rsplit('.', 1)[1].lower()
                if file_ext in ['png', 'jpg', 'jpeg', 'gif']:
                    evidence_type = EvidenceType.PHOTO
                elif file_ext in ['mp4', 'mov', 'avi']:
                    evidence_type = EvidenceType.VIDEO
                elif file_ext in ['mp3', 'wav']:
                    evidence_type = EvidenceType.AUDIO
                else:
                    evidence_type = EvidenceType.DOCUMENT
                
                # Create evidence record
                evidence = ProjectEvidence(
                    report_id=report.id,
                    file_name=filename,
                    file_path=file_path,
                    file_size=os.path.getsize(file_path),
                    file_type=evidence_type,
                    mime_type=file.mimetype
                )
                
                # Simulate metadata extraction (GPS, timestamp)
                if evidence_type == EvidenceType.PHOTO and latitude and longitude:
                    evidence.file_metadata = {
                        'gps': {
                            'latitude': latitude,
                            'longitude': longitude
                        },
                        'timestamp': datetime.utcnow().isoformat(),
                        'camera_info': 'Simulated metadata'
                    }
                
                # Auto-anonymize faces (simulation)
                evidence.anonymize_faces()
                
                db.session.add(evidence)
                uploaded_files.append({
                    'filename': filename,
                    'type': evidence_type.value,
                    'size': evidence.file_size
                })
        
        # Calculate initial verification score
        report.calculate_verification_score()
        
        # Create AI analysis (simulation)
        ai_analysis = AIAnalysis(
            report_id=report.id,
            model_version='govtracka_v1.0'
        )
        
        # Simulate fraud detection
        if reported_budget and reported_budget > 1000000000:  # > 1 billion naira
            ai_analysis.budget_anomaly = True
            ai_analysis.add_fraud_indicator(
                'budget_anomaly',
                f'Unusually high budget: ₦{reported_budget:,}',
                0.8
            )
            ai_analysis.anomaly_score += 30
        
        if not latitude or not longitude:
            ai_analysis.location_mismatch = True
            ai_analysis.add_fraud_indicator(
                'missing_location',
                'No GPS coordinates provided',
                0.6
            )
            ai_analysis.anomaly_score += 20
        
        # Check for duplicate projects (simulation)
        similar_projects = ProjectReport.query.filter(
            ProjectReport.project_name.ilike(f'%{project_name}%'),
            ProjectReport.state == state,
            ProjectReport.id != report.id
        ).count()
        
        if similar_projects > 0:
            ai_analysis.duplicate_project = True
            ai_analysis.add_fraud_indicator(
                'potential_duplicate',
                f'Found {similar_projects} similar projects in {state}',
                0.7
            )
            ai_analysis.anomaly_score += 25
        
        db.session.add(ai_analysis)
        
        # Log report submission for NDPR compliance
        audit_log = NDPRAuditLog(
            user_id=reporter_id,
            action='project_report_submitted',
            details={
                'report_id': report.id,
                'project_type': project_type,
                'state': state,
                'submission_method': submission_method,
                'evidence_files_count': len(uploaded_files)
            },
            legal_basis='NDPR_Section_2_5_Legitimate_Interest_Public_Transparency'
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'report_id': report.id,
            'status': report.status.value,
            'verification_score': report.verification_score,
            'blockchain_hash': report.blockchain_hash,
            'uploaded_files': uploaded_files,
            'ai_analysis': {
                'anomaly_score': ai_analysis.anomaly_score,
                'fraud_indicators': ai_analysis.fraud_indicators
            },
            'message': 'Project report submitted successfully',
            'next_steps': [
                'Your report is under review',
                'Community members can vote on its accuracy',
                'NGO partners will verify the information',
                'You will be notified of any updates'
            ]
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Project report submission error: {str(e)}")
        return jsonify({'error': 'Failed to submit project report'}), 500

@reports_bp.route('/list', methods=['GET'])
def list_project_reports():
    """Get list of project reports with filtering"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        state = request.args.get('state')
        project_type = request.args.get('project_type')
        status = request.args.get('status')
        min_budget = request.args.get('min_budget', type=int)
        max_budget = request.args.get('max_budget', type=int)
        
        # Build query
        query = ProjectReport.query
        
        if state:
            query = query.filter(ProjectReport.state.ilike(f'%{state}%'))
        
        if project_type:
            try:
                project_type_enum = ProjectType(project_type)
                query = query.filter(ProjectReport.project_type == project_type_enum)
            except ValueError:
                pass
        
        if status:
            try:
                status_enum = ReportStatus(status)
                query = query.filter(ProjectReport.status == status_enum)
            except ValueError:
                pass
        
        if min_budget:
            query = query.filter(ProjectReport.reported_budget >= min_budget * 100)
        
        if max_budget:
            query = query.filter(ProjectReport.reported_budget <= max_budget * 100)
        
        # Order by creation date (newest first)
        query = query.order_by(ProjectReport.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        reports = []
        for report in pagination.items:
            report_data = report.to_dict()
            
            # Add summary statistics
            report_data['summary'] = {
                'evidence_files': len(report.evidence_files),
                'community_votes': report.community_votes,
                'verification_count': len(report.verifications),
                'ai_anomaly_score': report.ai_analysis[0].anomaly_score if report.ai_analysis else 0
            }
            
            reports.append(report_data)
        
        return jsonify({
            'reports': reports,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters_applied': {
                'state': state,
                'project_type': project_type,
                'status': status,
                'budget_range': f"₦{min_budget:,} - ₦{max_budget:,}" if min_budget or max_budget else None
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"List reports error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve reports'}), 500

@reports_bp.route('/<report_id>', methods=['GET'])
def get_project_report(report_id):
    """Get detailed information about a specific project report"""
    try:
        report = ProjectReport.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Get detailed report data
        report_data = report.to_dict()
        
        # Add evidence files
        report_data['evidence_files'] = [
            {
                'id': evidence.id,
                'filename': evidence.file_name,
                'type': evidence.file_type.value,
                'size': evidence.file_size,
                'uploaded_at': evidence.uploaded_at.isoformat(),
                'is_verified': evidence.is_verified,
                'has_gps_data': bool(evidence.extract_gps_data()),
                'is_anonymized': evidence.is_anonymized
            }
            for evidence in report.evidence_files
        ]
        
        # Add verifications
        report_data['verifications'] = [
            {
                'id': verification.id,
                'is_verified': verification.is_verified,
                'confidence_level': verification.confidence_level,
                'verifier_organization': verification.verifier_organization,
                'verification_method': verification.verification_method,
                'verified_at': verification.verified_at.isoformat(),
                'notes': verification.verification_notes
            }
            for verification in report.verifications
        ]
        
        # Add AI analysis
        if report.ai_analysis:
            ai_data = report.ai_analysis[0]
            report_data['ai_analysis'] = {
                'anomaly_score': ai_data.anomaly_score,
                'fraud_indicators': ai_data.fraud_indicators,
                'budget_anomaly': ai_data.budget_anomaly,
                'location_mismatch': ai_data.location_mismatch,
                'duplicate_project': ai_data.duplicate_project,
                'image_authenticity_score': ai_data.image_authenticity_score,
                'model_version': ai_data.model_version,
                'analysis_timestamp': ai_data.analysis_timestamp.isoformat()
            }
        
        # Add community votes summary
        votes = CommunityVote.query.filter_by(report_id=report_id).all()
        vote_summary = {
            'total_votes': len(votes),
            'support_votes': len([v for v in votes if v.vote_type == 'support']),
            'dispute_votes': len([v for v in votes if v.vote_type == 'dispute']),
            'additional_info_requests': len([v for v in votes if v.vote_type == 'additional_info'])
        }
        report_data['community_engagement'] = vote_summary
        
        # Log report view for analytics
        audit_log = NDPRAuditLog(
            action='project_report_viewed',
            details={
                'report_id': report_id,
                'project_type': report.project_type.value,
                'state': report.state
            },
            legal_basis='NDPR_Section_2_5_Legitimate_Interest_Public_Transparency'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify(report_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Get report error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve report'}), 500

@reports_bp.route('/<report_id>/vote', methods=['POST'])
def vote_on_report(report_id):
    """Community voting on project reports"""
    try:
        data = request.get_json()
        voter_id = data.get('voter_id')
        vote_type = data.get('vote_type')  # 'support', 'dispute', 'additional_info'
        comment = data.get('comment')
        vote_method = data.get('method', 'web')
        
        # Validate inputs
        if vote_type not in ['support', 'dispute', 'additional_info']:
            return jsonify({'error': 'Invalid vote type'}), 400
        
        # Check if report exists
        report = ProjectReport.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check if user exists
        voter = User.query.get(voter_id)
        if not voter:
            return jsonify({'error': 'Voter not found'}), 404
        
        # Check if user already voted
        existing_vote = CommunityVote.query.filter_by(
            report_id=report_id,
            voter_id=voter_id
        ).first()
        
        if existing_vote:
            return jsonify({'error': 'You have already voted on this report'}), 400
        
        # Create vote
        vote = CommunityVote(
            report_id=report_id,
            voter_id=voter_id,
            vote_type=vote_type,
            comment=comment,
            vote_method=vote_method
        )
        
        db.session.add(vote)
        
        # Update report community votes count
        if vote_type == 'support':
            report.community_votes += 1
        elif vote_type == 'dispute':
            report.community_votes -= 1
        
        # Recalculate verification score
        report.calculate_verification_score()
        
        # Log vote for NDPR compliance
        audit_log = NDPRAuditLog(
            user_id=voter_id,
            action='community_vote_cast',
            details={
                'report_id': report_id,
                'vote_type': vote_type,
                'method': vote_method
            },
            legal_basis='NDPR_Section_2_5_Legitimate_Interest_Public_Participation'
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vote recorded successfully',
            'vote_id': vote.id,
            'updated_score': report.verification_score,
            'community_votes': report.community_votes
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Vote on report error: {str(e)}")
        return jsonify({'error': 'Failed to record vote'}), 500

@reports_bp.route('/<report_id>/verify', methods=['POST'])
def verify_report(report_id):
    """Professional verification of project reports (NGO partners, moderators)"""
    try:
        data = request.get_json()
        verifier_id = data.get('verifier_id')
        is_verified = data.get('is_verified')
        verification_notes = data.get('notes')
        confidence_level = data.get('confidence_level', type=int)
        verifier_organization = data.get('organization')
        verification_method = data.get('method')
        
        # Check if report exists
        report = ProjectReport.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check if verifier exists and has permission
        verifier = User.query.get(verifier_id)
        if not verifier or not verifier.can_moderate_reports():
            return jsonify({'error': 'Unauthorized to verify reports'}), 403
        
        # Create verification record
        verification = ReportVerification(
            report_id=report_id,
            verifier_id=verifier_id,
            is_verified=is_verified,
            verification_notes=verification_notes,
            confidence_level=confidence_level,
            verifier_organization=verifier_organization,
            verification_method=verification_method
        )
        
        db.session.add(verification)
        
        # Update report status based on verification
        if is_verified:
            report.status = ReportStatus.VERIFIED
            report.verified_at = datetime.utcnow()
        else:
            report.status = ReportStatus.DISPUTED
        
        # Recalculate verification score
        report.calculate_verification_score()
        
        # Log verification for NDPR compliance
        audit_log = NDPRAuditLog(
            user_id=verifier_id,
            action='report_verification_completed',
            details={
                'report_id': report_id,
                'is_verified': is_verified,
                'organization': verifier_organization,
                'method': verification_method
            },
            legal_basis='NDPR_Section_2_5_Legitimate_Interest_Public_Verification'
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Verification recorded successfully',
            'verification_id': verification.id,
            'report_status': report.status.value,
            'updated_score': report.verification_score
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Verify report error: {str(e)}")
        return jsonify({'error': 'Failed to verify report'}), 500

@reports_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics for transparency feed"""
    try:
        # Basic statistics
        total_reports = ProjectReport.query.count()
        verified_reports = ProjectReport.query.filter_by(status=ReportStatus.VERIFIED).count()
        pending_reports = ProjectReport.query.filter_by(status=ReportStatus.PENDING).count()
        disputed_reports = ProjectReport.query.filter_by(status=ReportStatus.DISPUTED).count()
        
        # Financial impact (estimated savings from exposed fraud)
        high_anomaly_reports = db.session.query(ProjectReport).join(AIAnalysis).filter(
            AIAnalysis.anomaly_score > 70
        ).all()
        
        estimated_fraud_value = sum([
            report.reported_budget or 0 for report in high_anomaly_reports
        ]) / 100  # Convert from kobo to naira
        
        # State-wise breakdown
        state_stats = db.session.query(
            ProjectReport.state,
            db.func.count(ProjectReport.id).label('count'),
            db.func.sum(ProjectReport.reported_budget).label('total_budget')
        ).group_by(ProjectReport.state).all()
        
        state_breakdown = [
            {
                'state': stat.state,
                'reports_count': stat.count,
                'total_budget': (stat.total_budget or 0) / 100  # Convert to naira
            }
            for stat in state_stats if stat.state
        ]
        
        # Project type breakdown
        type_stats = db.session.query(
            ProjectReport.project_type,
            db.func.count(ProjectReport.id).label('count')
        ).group_by(ProjectReport.project_type).all()
        
        type_breakdown = [
            {
                'project_type': stat.project_type.value,
                'count': stat.count
            }
            for stat in type_stats
        ]
        
        # Recent activity
        recent_reports = ProjectReport.query.order_by(
            ProjectReport.created_at.desc()
        ).limit(5).all()
        
        recent_activity = [
            {
                'id': report.id,
                'project_name': report.project_name,
                'state': report.state,
                'status': report.status.value,
                'created_at': report.created_at.isoformat(),
                'verification_score': report.verification_score
            }
            for report in recent_reports
        ]
        
        dashboard_stats = {
            'overview': {
                'total_reports': total_reports,
                'verified_reports': verified_reports,
                'pending_reports': pending_reports,
                'disputed_reports': disputed_reports,
                'verification_rate': f"{(verified_reports/total_reports*100):.1f}%" if total_reports > 0 else "0%"
            },
            'financial_impact': {
                'estimated_fraud_exposed': estimated_fraud_value,
                'high_risk_reports': len(high_anomaly_reports),
                'potential_savings': estimated_fraud_value * 0.8  # Assume 80% recovery rate
            },
            'geographic_distribution': state_breakdown,
            'project_types': type_breakdown,
            'recent_activity': recent_activity,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify(dashboard_stats), 200
        
    except Exception as e:
        current_app.logger.error(f"Dashboard stats error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve dashboard statistics'}), 500

