from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import hashlib
import uuid
from src.models.user import db, User, UserRole
from src.models.project_report import ProjectReport, ProjectType, ReportStatus
from src.models.ndpr_compliance import NDPRConsent, RightToBeForgotten, NDPRAuditLog, ConsentStatus

ussd_bp = Blueprint('ussd', __name__)

# USSD session storage (in production, use Redis or database)
ussd_sessions = {}

class USSDSession:
    def __init__(self, phone_number, session_id):
        self.phone_number = phone_number
        self.session_id = session_id
        self.current_step = 'main_menu'
        self.data = {}
        self.created_at = datetime.utcnow()
    
    def set_step(self, step):
        self.current_step = step
    
    def set_data(self, key, value):
        self.data[key] = value
    
    def get_data(self, key, default=None):
        return self.data.get(key, default)

@ussd_bp.route('/session', methods=['POST'])
def handle_ussd_session():
    """Main USSD session handler for *347*# codes"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        session_id = data.get('session_id')
        text = data.get('text', '')
        service_code = data.get('service_code', '*347#')
        
        if not phone_number or not session_id:
            return jsonify({
                'response': 'END Invalid session. Please try again.',
                'session_active': False
            }), 400
        
        # Get or create session
        session_key = f"{phone_number}_{session_id}"
        session = ussd_sessions.get(session_key)
        
        if not session:
            session = USSDSession(phone_number, session_id)
            ussd_sessions[session_key] = session
        
        # Parse user input
        user_input = text.split('*')[-1] if text else ''
        
        # Route to appropriate handler
        if session.current_step == 'main_menu':
            response = handle_main_menu(session, user_input)
        elif session.current_step == 'report_project':
            response = handle_report_project(session, user_input)
        elif session.current_step == 'check_status':
            response = handle_check_status(session, user_input)
        elif session.current_step == 'consent_flow':
            response = handle_consent_flow(session, user_input)
        elif session.current_step == 'delete_data':
            response = handle_delete_data(session, user_input)
        else:
            response = handle_main_menu(session, user_input)
        
        # Clean up completed sessions
        if not response.get('session_active', True):
            ussd_sessions.pop(session_key, None)
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"USSD session error: {str(e)}")
        return jsonify({
            'response': 'END Service temporarily unavailable. Please try again later.',
            'session_active': False
        }), 500

def handle_main_menu(session, user_input):
    """Handle main menu navigation"""
    if not user_input:
        # First time access - show main menu
        return {
            'response': """CON Welcome to GovTracka!
Citizen-led transparency platform

1. Report a project
2. Check report status
3. Data consent info
4. Delete my data
5. About GovTracka

Choose option:""",
            'session_active': True
        }
    
    if user_input == '1':
        session.set_step('report_project')
        return {
            'response': """CON Report a Project

Select project type:
1. School
2. Road
3. Clinic/Hospital
4. Water project
5. Bridge
6. Market
7. Other

Choose type:""",
            'session_active': True
        }
    
    elif user_input == '2':
        session.set_step('check_status')
        return {
            'response': """CON Check Report Status

Enter your phone number to see your reports:

(Format: 08012345678)""",
            'session_active': True
        }
    
    elif user_input == '3':
        session.set_step('consent_flow')
        return {
            'response': """CON Data Consent Information

GovTracka processes your data to:
- Track government projects
- Fight corruption
- Improve transparency

Your data is stored securely in Nigeria.

1. Grant consent
2. View my consents
3. Withdraw consent

Choose:""",
            'session_active': True
        }
    
    elif user_input == '4':
        session.set_step('delete_data')
        return {
            'response': """CON Delete My Data

WARNING: This will permanently delete all your personal data from GovTracka.

Your project reports will remain public for transparency but will be anonymized.

1. Yes, delete my data
2. No, go back

Choose:""",
            'session_active': True
        }
    
    elif user_input == '5':
        return {
            'response': """END About GovTracka

GovTracka is a citizen-led platform for monitoring government projects and fighting corruption.

Features:
- Report project issues
- Verify project status
- Community voting
- NDPR compliant

Visit: www.govtracka.ng
Support: *347*0#""",
            'session_active': False
        }
    
    else:
        return {
            'response': """CON Invalid option. Please try again.

1. Report a project
2. Check report status
3. Data consent info
4. Delete my data
5. About GovTracka

Choose option:""",
            'session_active': True
        }

def handle_report_project(session, user_input):
    """Handle project reporting flow"""
    current_data = session.data
    
    if 'project_type' not in current_data:
        # Step 1: Project type selection
        project_types = {
            '1': 'school',
            '2': 'road', 
            '3': 'clinic',
            '4': 'water_project',
            '5': 'bridge',
            '6': 'market',
            '7': 'other'
        }
        
        if user_input in project_types:
            session.set_data('project_type', project_types[user_input])
            return {
                'response': """CON Project Name

Enter the name of the project:

(e.g., "Ikeja Primary School Block A")""",
                'session_active': True
            }
        else:
            return {
                'response': """CON Invalid selection.

Select project type:
1. School
2. Road
3. Clinic/Hospital
4. Water project
5. Bridge
6. Market
7. Other

Choose type:""",
                'session_active': True
            }
    
    elif 'project_name' not in current_data:
        # Step 2: Project name
        if user_input.strip():
            session.set_data('project_name', user_input.strip())
            return {
                'response': """CON Project Location

Enter the location/address:

(e.g., "Ikeja, Lagos State")""",
                'session_active': True
            }
        else:
            return {
                'response': """CON Project name cannot be empty.

Enter the name of the project:

(e.g., "Ikeja Primary School Block A")""",
                'session_active': True
            }
    
    elif 'location' not in current_data:
        # Step 3: Location
        if user_input.strip():
            session.set_data('location', user_input.strip())
            return {
                'response': """CON Project Description

Describe the issue:

1. Not started
2. Incomplete/abandoned
3. Poor quality
4. Overpriced
5. Ghost project
6. Other issue

Choose:""",
                'session_active': True
            }
        else:
            return {
                'response': """CON Location cannot be empty.

Enter the location/address:

(e.g., "Ikeja, Lagos State")""",
                'session_active': True
            }
    
    elif 'description' not in current_data:
        # Step 4: Description
        descriptions = {
            '1': 'Project has not been started despite budget allocation',
            '2': 'Project is incomplete or has been abandoned',
            '3': 'Project quality is very poor or substandard',
            '4': 'Project appears to be overpriced for the work done',
            '5': 'This appears to be a ghost project (fake/non-existent)',
            '6': 'Other issues with this project'
        }
        
        if user_input in descriptions:
            session.set_data('description', descriptions[user_input])
            return {
                'response': """CON Budget Information

Do you know the project budget?

1. Yes, I know the budget
2. No, I don't know
3. Skip this step

Choose:""",
                'session_active': True
            }
        else:
            return {
                'response': """CON Invalid selection.

Describe the issue:

1. Not started
2. Incomplete/abandoned
3. Poor quality
4. Overpriced
5. Ghost project
6. Other issue

Choose:""",
                'session_active': True
            }
    
    elif 'budget_known' not in current_data:
        # Step 5: Budget information
        if user_input == '1':
            session.set_data('budget_known', True)
            return {
                'response': """CON Enter Budget Amount

Enter the project budget in Naira:

(e.g., 50000000 for ₦50M)

Amount:""",
                'session_active': True
            }
        elif user_input in ['2', '3']:
            session.set_data('budget_known', False)
            session.set_data('budget', None)
            return submit_ussd_report(session)
        else:
            return {
                'response': """CON Invalid selection.

Do you know the project budget?

1. Yes, I know the budget
2. No, I don't know
3. Skip this step

Choose:""",
                'session_active': True
            }
    
    elif 'budget' not in current_data and current_data.get('budget_known'):
        # Step 6: Budget amount
        try:
            budget = int(user_input.strip())
            if budget > 0:
                session.set_data('budget', budget)
                return submit_ussd_report(session)
            else:
                raise ValueError("Budget must be positive")
        except ValueError:
            return {
                'response': """CON Invalid budget amount.

Enter the project budget in Naira:

(e.g., 50000000 for ₦50M)

Amount:""",
                'session_active': True
            }
    
    else:
        return submit_ussd_report(session)

def submit_ussd_report(session):
    """Submit the USSD project report"""
    try:
        # Get or create user
        phone_hash = hashlib.sha256(session.phone_number.encode()).hexdigest()
        user = User.query.filter_by(phone_number_hash=phone_hash).first()
        
        if not user:
            # Create anonymous user
            user = User(
                phone_number_hash=phone_hash,
                is_anonymous=True,
                role=UserRole.CITIZEN,
                preferred_contact_method='ussd'
            )
            user.anonymous_id = user.generate_anonymous_id()
            db.session.add(user)
            db.session.flush()
        
        # Parse location for state extraction
        location = session.get_data('location', '')
        state = None
        if 'lagos' in location.lower():
            state = 'Lagos'
        elif 'abuja' in location.lower():
            state = 'FCT'
        elif 'kano' in location.lower():
            state = 'Kano'
        # Add more state parsing logic as needed
        
        # Create project report
        report = ProjectReport(
            reporter_id=user.id,
            project_name=session.get_data('project_name'),
            project_type=ProjectType(session.get_data('project_type')),
            description=session.get_data('description'),
            location_name=location,
            state=state,
            reported_budget=session.get_data('budget', 0) * 100 if session.get_data('budget') else None,  # Convert to kobo
            submission_method='ussd'
        )
        
        # Generate blockchain hash
        report.generate_blockchain_hash()
        
        db.session.add(report)
        
        # Log submission
        audit_log = NDPRAuditLog(
            user_id=user.id,
            action='ussd_report_submitted',
            details={
                'report_id': report.id,
                'project_type': session.get_data('project_type'),
                'phone_hash': phone_hash[:8]  # Partial hash for tracking
            },
            legal_basis='NDPR_Section_2_5_Legitimate_Interest_Public_Transparency'
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return {
            'response': f"""END Report Submitted Successfully!

Report ID: {report.id[:8]}...
Project: {session.get_data('project_name')}
Status: Under Review

Your report will be verified by our community and NGO partners.

Thank you for fighting corruption!

Check status: *347*2#""",
            'session_active': False
        }
        
    except Exception as e:
        current_app.logger.error(f"USSD report submission error: {str(e)}")
        return {
            'response': """END Error submitting report.

Please try again later or use our website: www.govtracka.ng

For support: *347*0#""",
            'session_active': False
        }

def handle_check_status(session, user_input):
    """Handle report status checking"""
    if 'phone_verified' not in session.data:
        # Verify phone number format
        if len(user_input) == 11 and user_input.startswith('0'):
            phone_hash = hashlib.sha256(user_input.encode()).hexdigest()
            user = User.query.filter_by(phone_number_hash=phone_hash).first()
            
            if user:
                reports = ProjectReport.query.filter_by(reporter_id=user.id).order_by(
                    ProjectReport.created_at.desc()
                ).limit(5).all()
                
                if reports:
                    report_list = []
                    for i, report in enumerate(reports, 1):
                        status_emoji = {
                            'pending': '⏳',
                            'under_review': '🔍',
                            'verified': '✅',
                            'disputed': '❌',
                            'rejected': '🚫'
                        }
                        emoji = status_emoji.get(report.status.value, '📋')
                        report_list.append(f"{i}. {emoji} {report.project_name[:20]}...")
                    
                    return {
                        'response': f"""END Your Reports:

{chr(10).join(report_list)}

Legend:
⏳ Pending  🔍 Under Review
✅ Verified  ❌ Disputed

For details: www.govtracka.ng""",
                        'session_active': False
                    }
                else:
                    return {
                        'response': """END No reports found for this number.

To submit a report: *347*1#

Visit: www.govtracka.ng""",
                        'session_active': False
                    }
            else:
                return {
                    'response': """END No reports found for this number.

To submit a report: *347*1#

Visit: www.govtracka.ng""",
                    'session_active': False
                }
        else:
            return {
                'response': """CON Invalid phone number format.

Enter your phone number:

(Format: 08012345678)""",
                'session_active': True
            }

def handle_consent_flow(session, user_input):
    """Handle NDPR consent management"""
    if user_input == '1':
        # Grant consent
        phone_hash = hashlib.sha256(session.phone_number.encode()).hexdigest()
        user = User.query.filter_by(phone_number_hash=phone_hash).first()
        
        if not user:
            # Create user for consent
            user = User(
                phone_number_hash=phone_hash,
                is_anonymous=True,
                role=UserRole.CITIZEN,
                preferred_contact_method='ussd'
            )
            user.anonymous_id = user.generate_anonymous_id()
            db.session.add(user)
            db.session.flush()
        
        # Create consent
        consent = NDPRConsent(
            user_id=user.id,
            phone_number_hash=phone_hash,
            purpose='project_reporting',
            consent_text='USSD consent for GovTracka project reporting',
            consent_method='ussd'
        )
        consent.grant_consent()
        
        db.session.add(consent)
        db.session.commit()
        
        return {
            'response': """END Consent Granted!

You have consented to data processing for project reporting.

Your data will be:
- Stored securely in Nigeria
- Used only for transparency
- Anonymized when possible

Withdraw anytime: *347*9#""",
            'session_active': False
        }
    
    elif user_input == '2':
        # View consents
        phone_hash = hashlib.sha256(session.phone_number.encode()).hexdigest()
        user = User.query.filter_by(phone_number_hash=phone_hash).first()
        
        if user and user.consents:
            active_consents = [c for c in user.consents if c.is_valid()]
            if active_consents:
                consent_list = []
                for consent in active_consents:
                    consent_list.append(f"• {consent.purpose.value}: {consent.status.value}")
                
                return {
                    'response': f"""END Your Active Consents:

{chr(10).join(consent_list)}

To withdraw: *347*9#""",
                    'session_active': False
                }
        
        return {
            'response': """END No active consents found.

To grant consent: *347*3# then 1

Visit: www.govtracka.ng""",
            'session_active': False
        }
    
    elif user_input == '3':
        # Withdraw consent
        return {
            'response': """CON Withdraw Consent

This will withdraw all your consents and anonymize your data.

1. Yes, withdraw all consents
2. No, go back

Choose:""",
            'session_active': True
        }

def handle_delete_data(session, user_input):
    """Handle right to be forgotten requests"""
    if user_input == '1':
        # Confirm data deletion
        phone_hash = hashlib.sha256(session.phone_number.encode()).hexdigest()
        user = User.query.filter_by(phone_number_hash=phone_hash).first()
        
        if user:
            # Create deletion request
            deletion_request = RightToBeForgotten(
                user_id=user.id,
                phone_number_hash=phone_hash,
                request_method='ussd',
                request_reason='USSD data deletion request'
            )
            db.session.add(deletion_request)
            
            # Process deletion immediately
            user.anonymize()
            
            # Withdraw all consents
            for consent in user.consents:
                consent.withdraw_consent()
            
            deletion_request.status = 'completed'
            deletion_request.processed_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'response': """END Data Deleted Successfully!

Your personal data has been anonymized.

Your project reports remain public for transparency but are no longer linked to you.

Thank you for using GovTracka responsibly.""",
                'session_active': False
            }
        else:
            return {
                'response': """END No data found for this number.

Your data may already be deleted or you may not have an account.

For support: support@govtracka.ng""",
                'session_active': False
            }
    
    elif user_input == '2':
        # Go back to main menu
        session.set_step('main_menu')
        return handle_main_menu(session, '')
    
    else:
        return {
            'response': """CON Invalid selection.

1. Yes, delete my data
2. No, go back

Choose:""",
            'session_active': True
        }

@ussd_bp.route('/webhook/twilio', methods=['POST'])
def twilio_ussd_webhook():
    """Webhook for Twilio USSD integration"""
    try:
        # Twilio sends form data
        phone_number = request.form.get('From')
        text = request.form.get('Body', '')
        session_id = request.form.get('SessionId')
        service_code = request.form.get('ServiceCode', '*347#')
        
        # Convert to our format
        ussd_data = {
            'phone_number': phone_number,
            'text': text,
            'session_id': session_id,
            'service_code': service_code
        }
        
        # Process through our handler
        response = handle_ussd_session()
        
        # Convert back to Twilio format
        twilio_response = response.get_json()['response']
        
        return twilio_response, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        current_app.logger.error(f"Twilio webhook error: {str(e)}")
        return "END Service temporarily unavailable.", 500

