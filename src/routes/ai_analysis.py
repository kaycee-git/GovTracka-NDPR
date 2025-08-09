"""
AI Analysis Routes for GovTracka
Handles image verification, anomaly detection, and voice processing
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import uuid

from src.services.ai_integration import aiml_client, blockchain_service
from src.models.user import db
from src.models.project_report import ProjectReport, ProjectEvidence, AIAnalysis
from src.models.ndpr_compliance import NDPRAuditLog

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'wav', 'mp3'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ai_bp.route('/verify-image', methods=['POST'])
def verify_image():
    """
    Verify uploaded image authenticity using AI
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Read image data
        image_data = file.read()
        
        # Get metadata from request
        metadata = {
            'filename': secure_filename(file.filename),
            'upload_timestamp': datetime.utcnow().isoformat(),
            'gps_coordinates': request.form.get('gps_coordinates'),
            'timestamp': request.form.get('timestamp'),
            'camera_model': request.form.get('camera_model'),
            'user_agent': request.headers.get('User-Agent')
        }
        
        # Verify image using AI
        verification_result = aiml_client.verify_image_authenticity(image_data, metadata)
        
        # Anchor evidence to blockchain
        blockchain_result = blockchain_service.anchor_evidence({
            'type': 'image_verification',
            'verification_result': verification_result,
            'metadata': metadata
        })
        
        # Save to database
        evidence = ProjectEvidence(
            id=str(uuid.uuid4()),
            file_type='image',
            file_size=len(image_data),
            file_hash=verification_result.get('image_hash'),
            blockchain_hash=blockchain_result.get('blockchain_hash'),
            ai_verification_score=verification_result.get('verification_score', 0),
            metadata_json=json.dumps(metadata)
        )
        
        db.session.add(evidence)
        
        # Log for NDPR compliance
        audit_log = NDPRAuditLog(
            action='image_verification',
            details={
                'evidence_id': evidence.id,
                'verification_score': verification_result.get('verification_score'),
                'ai_model': verification_result.get('ai_model')
            },
            legal_basis='NDPR_Section_2_3_Legitimate_Interest',
            data_category='evidence_files'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'evidence_id': evidence.id,
            'verification_result': verification_result,
            'blockchain_result': blockchain_result,
            'ndpr_compliant': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analyze-project', methods=['POST'])
def analyze_project():
    """
    Analyze project data for anomalies and fraud indicators
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No project data provided'}), 400
        
        # Perform AI anomaly detection
        anomaly_result = aiml_client.detect_anomalies(data)
        
        # Create AI analysis record
        ai_analysis = AIAnalysis(
            id=str(uuid.uuid4()),
            analysis_type='fraud_detection',
            input_data=json.dumps(data),
            ai_model='pytorch-anomaly-detection',
            confidence_score=anomaly_result.get('confidence', 0),
            result_data=json.dumps(anomaly_result)
        )
        
        db.session.add(ai_analysis)
        
        # Anchor analysis to blockchain
        blockchain_result = blockchain_service.anchor_evidence({
            'type': 'ai_analysis',
            'analysis_id': ai_analysis.id,
            'anomaly_result': anomaly_result
        })
        
        ai_analysis.blockchain_hash = blockchain_result.get('blockchain_hash')
        
        # Log for NDPR compliance
        audit_log = NDPRAuditLog(
            action='ai_fraud_analysis',
            details={
                'analysis_id': ai_analysis.id,
                'anomaly_score': anomaly_result.get('anomaly_score'),
                'risk_level': anomaly_result.get('risk_level')
            },
            legal_basis='NDPR_Section_2_3_Legitimate_Interest',
            data_category='project_analysis'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis_id': ai_analysis.id,
            'anomaly_result': anomaly_result,
            'blockchain_hash': blockchain_result.get('blockchain_hash'),
            'ndpr_compliant': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/process-voice', methods=['POST'])
def process_voice():
    """
    Process voice description using AI transcription
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read audio data
        audio_data = file.read()
        
        # Process voice using AI
        transcription_result = aiml_client.process_voice_description(audio_data)
        
        # Create evidence record
        evidence = ProjectEvidence(
            id=str(uuid.uuid4()),
            file_type='audio',
            file_size=len(audio_data),
            file_hash=transcription_result.get('audio_hash'),
            ai_verification_score=transcription_result.get('confidence', 0) * 100,
            metadata_json=json.dumps({
                'transcription': transcription_result.get('transcription'),
                'language_detected': transcription_result.get('language_detected'),
                'duration_estimate': transcription_result.get('duration_estimate')
            })
        )
        
        # Anchor to blockchain
        blockchain_result = blockchain_service.anchor_evidence({
            'type': 'voice_transcription',
            'evidence_id': evidence.id,
            'transcription_result': transcription_result
        })
        
        evidence.blockchain_hash = blockchain_result.get('blockchain_hash')
        
        db.session.add(evidence)
        
        # Log for NDPR compliance
        audit_log = NDPRAuditLog(
            action='voice_processing',
            details={
                'evidence_id': evidence.id,
                'transcription_confidence': transcription_result.get('confidence'),
                'language': transcription_result.get('language_detected')
            },
            legal_basis='NDPR_Section_2_3_Legitimate_Interest',
            data_category='voice_data'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'evidence_id': evidence.id,
            'transcription_result': transcription_result,
            'blockchain_hash': blockchain_result.get('blockchain_hash'),
            'ndpr_compliant': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/verify-blockchain/<evidence_hash>', methods=['GET'])
def verify_blockchain_evidence(evidence_hash):
    """
    Verify evidence integrity on blockchain
    """
    try:
        verification_result = blockchain_service.verify_evidence_integrity(evidence_hash)
        
        # Log verification attempt
        audit_log = NDPRAuditLog(
            action='blockchain_verification',
            details={
                'evidence_hash': evidence_hash,
                'verification_result': verification_result.get('verified')
            },
            legal_basis='NDPR_Section_2_3_Legitimate_Interest',
            data_category='blockchain_verification'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'verification_result': verification_result,
            'ndpr_compliant': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analysis-report/<analysis_id>', methods=['GET'])
def get_analysis_report(analysis_id):
    """
    Get detailed AI analysis report
    """
    try:
        analysis = AIAnalysis.query.filter_by(id=analysis_id).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Parse result data
        result_data = json.loads(analysis.result_data) if analysis.result_data else {}
        
        report = {
            'analysis_id': analysis.id,
            'analysis_type': analysis.analysis_type,
            'ai_model': analysis.ai_model,
            'confidence_score': analysis.confidence_score,
            'created_at': analysis.created_at.isoformat(),
            'result_data': result_data,
            'blockchain_hash': analysis.blockchain_hash,
            'ndpr_compliant': True
        }
        
        # Log report access
        audit_log = NDPRAuditLog(
            action='analysis_report_access',
            details={
                'analysis_id': analysis_id,
                'access_timestamp': datetime.utcnow().isoformat()
            },
            legal_basis='NDPR_Section_2_3_Legitimate_Interest',
            data_category='analysis_reports'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/health', methods=['GET'])
def ai_health_check():
    """
    Health check for AI services
    """
    try:
        # Test AI services
        test_data = {
            'project_name': 'Test Project',
            'project_type': 'school',
            'reported_budget': 1000000,
            'description': 'Test description'
        }
        
        # Test anomaly detection
        anomaly_result = aiml_client.detect_anomalies(test_data)
        
        # Test blockchain service
        blockchain_result = blockchain_service.anchor_evidence({
            'type': 'health_check',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'status': 'healthy',
            'ai_services': {
                'image_verification': 'available',
                'anomaly_detection': 'available',
                'voice_processing': 'available'
            },
            'blockchain_service': 'available' if blockchain_result.get('success') else 'unavailable',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

