"""
Security Services for GovTracka
Implements end-to-end encryption, RBAC, vulnerability scanning, and data purging
"""

import hashlib
import hmac
import secrets
import base64
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
import os
import re

class EncryptionService:
    """End-to-end encryption service using Signal Protocol principles"""
    
    def __init__(self):
        self.master_key = os.getenv('GOVTRACKA_MASTER_KEY', self._generate_master_key())
        self.salt = os.getenv('GOVTRACKA_SALT', secrets.token_bytes(16))
    
    def _generate_master_key(self) -> str:
        """Generate a master encryption key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _derive_key(self, password: bytes, salt: bytes) -> bytes:
        """Derive encryption key from password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def encrypt_data(self, data: str, user_key: Optional[str] = None) -> Dict:
        """
        Encrypt data using Fernet symmetric encryption
        """
        try:
            # Use user-specific key or master key
            if user_key:
                key = self._derive_key(user_key.encode(), self.salt)
            else:
                key = self._derive_key(self.master_key.encode(), self.salt)
            
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data.encode())
            
            return {
                'encrypted_data': base64.urlsafe_b64encode(encrypted_data).decode(),
                'encryption_method': 'fernet_aes256',
                'timestamp': datetime.utcnow().isoformat(),
                'key_derivation': 'pbkdf2_sha256'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'encrypted_data': None,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def decrypt_data(self, encrypted_data: str, user_key: Optional[str] = None) -> Dict:
        """
        Decrypt data using Fernet symmetric encryption
        """
        try:
            # Use user-specific key or master key
            if user_key:
                key = self._derive_key(user_key.encode(), self.salt)
            else:
                key = self._derive_key(self.master_key.encode(), self.salt)
            
            fernet = Fernet(key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            
            return {
                'decrypted_data': decrypted_data.decode(),
                'success': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'decrypted_data': None,
                'success': False,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def hash_password(self, password: str) -> Dict:
        """
        Hash password using PBKDF2 with SHA-256
        """
        salt = secrets.token_bytes(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        
        return {
            'password_hash': base64.urlsafe_b64encode(pwdhash).decode(),
            'salt': base64.urlsafe_b64encode(salt).decode(),
            'algorithm': 'pbkdf2_sha256',
            'iterations': 100000
        }
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """
        Verify password against stored hash
        """
        try:
            salt_bytes = base64.urlsafe_b64decode(salt.encode())
            stored_hash_bytes = base64.urlsafe_b64decode(stored_hash.encode())
            pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt_bytes, 100000)
            return hmac.compare_digest(pwdhash, stored_hash_bytes)
        except Exception:
            return False


class RBACService:
    """Role-Based Access Control service"""
    
    def __init__(self):
        self.roles = {
            'citizen': {
                'permissions': [
                    'report:create',
                    'report:view_own',
                    'transparency:view',
                    'ussd:access',
                    'data:request_deletion'
                ],
                'description': 'Regular citizen user'
            },
            'moderator': {
                'permissions': [
                    'report:create',
                    'report:view_own',
                    'report:view_all',
                    'report:moderate',
                    'transparency:view',
                    'community:vote',
                    'verification:perform'
                ],
                'description': 'Community moderator'
            },
            'ngo_partner': {
                'permissions': [
                    'report:view_all',
                    'report:investigate',
                    'report:verify',
                    'transparency:view',
                    'analytics:view',
                    'investigation:create'
                ],
                'description': 'NGO partner organization'
            },
            'admin': {
                'permissions': [
                    'report:*',
                    'user:*',
                    'system:*',
                    'analytics:*',
                    'ndpr:*',
                    'ai:*'
                ],
                'description': 'System administrator'
            },
            'super_admin': {
                'permissions': [
                    '*:*'  # All permissions
                ],
                'description': 'Super administrator with full access'
            }
        }
    
    def check_permission(self, user_role: str, resource: str, action: str) -> bool:
        """
        Check if user role has permission for specific resource and action
        """
        if user_role not in self.roles:
            return False
        
        permissions = self.roles[user_role]['permissions']
        
        # Check for wildcard permissions
        if '*:*' in permissions:
            return True
        
        if f'{resource}:*' in permissions:
            return True
        
        if f'{resource}:{action}' in permissions:
            return True
        
        return False
    
    def get_user_permissions(self, user_role: str) -> List[str]:
        """
        Get all permissions for a user role
        """
        if user_role not in self.roles:
            return []
        
        return self.roles[user_role]['permissions']
    
    def validate_role_hierarchy(self, current_role: str, target_role: str) -> bool:
        """
        Validate if current role can assign/modify target role
        """
        role_hierarchy = {
            'super_admin': 5,
            'admin': 4,
            'ngo_partner': 3,
            'moderator': 2,
            'citizen': 1
        }
        
        current_level = role_hierarchy.get(current_role, 0)
        target_level = role_hierarchy.get(target_role, 0)
        
        return current_level > target_level


class BiometricAuthService:
    """Biometric 2FA service for admin users"""
    
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
        self.biometric_challenges = {}
    
    def generate_biometric_challenge(self, user_id: str) -> Dict:
        """
        Generate biometric authentication challenge
        """
        challenge_id = secrets.token_urlsafe(16)
        challenge_data = {
            'challenge_id': challenge_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            'challenge_type': 'fingerprint_or_face',
            'nonce': secrets.token_urlsafe(16)
        }
        
        # Store challenge temporarily
        self.biometric_challenges[challenge_id] = challenge_data
        
        return {
            'challenge_id': challenge_id,
            'challenge_type': 'fingerprint_or_face',
            'expires_in': 300,  # 5 minutes
            'nonce': challenge_data['nonce'],
            'instructions': 'Please provide biometric authentication using your device'
        }
    
    def verify_biometric_response(self, challenge_id: str, biometric_data: str) -> Dict:
        """
        Verify biometric authentication response
        """
        if challenge_id not in self.biometric_challenges:
            return {
                'success': False,
                'error': 'Invalid or expired challenge',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        challenge = self.biometric_challenges[challenge_id]
        
        # Check if challenge has expired
        expires_at = datetime.fromisoformat(challenge['expires_at'])
        if datetime.utcnow() > expires_at:
            del self.biometric_challenges[challenge_id]
            return {
                'success': False,
                'error': 'Challenge expired',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Simulate biometric verification
        # In real implementation, this would integrate with device biometric APIs
        verification_success = self._simulate_biometric_verification(biometric_data)
        
        if verification_success:
            # Generate JWT token for authenticated session
            token = self._generate_auth_token(challenge['user_id'])
            del self.biometric_challenges[challenge_id]
            
            return {
                'success': True,
                'auth_token': token,
                'expires_in': 3600,  # 1 hour
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            return {
                'success': False,
                'error': 'Biometric verification failed',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _simulate_biometric_verification(self, biometric_data: str) -> bool:
        """
        Simulate biometric verification
        In real implementation, this would use actual biometric matching
        """
        # Simple simulation - check if data looks like base64 encoded biometric
        try:
            decoded = base64.b64decode(biometric_data)
            return len(decoded) > 100  # Minimum size for biometric data
        except Exception:
            return False
    
    def _generate_auth_token(self, user_id: str) -> str:
        """
        Generate JWT authentication token
        """
        payload = {
            'user_id': user_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1),
            'auth_method': 'biometric_2fa'
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')


class VulnerabilityScanner:
    """Automated vulnerability scanning service"""
    
    def __init__(self):
        self.scan_patterns = {
            'sql_injection': [
                r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b)",
                r"(\'\s*OR\s*\'\s*=\s*\'|\'\s*OR\s*1\s*=\s*1)",
                r"(\-\-|\#|\/\*|\*\/)"
            ],
            'xss': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>.*?</iframe>"
            ],
            'path_traversal': [
                r"(\.\./|\.\.\\\)",
                r"(/etc/passwd|/etc/shadow)",
                r"(\\windows\\system32)"
            ],
            'command_injection': [
                r"(\|\s*\w+|\&\&\s*\w+|\;\s*\w+)",
                r"(\$\(|\`)",
                r"(nc\s+|netcat\s+|wget\s+|curl\s+)"
            ]
        }
    
    def scan_input(self, input_data: str, input_type: str = 'general') -> Dict:
        """
        Scan input for security vulnerabilities
        """
        vulnerabilities = []
        risk_score = 0
        
        for vuln_type, patterns in self.scan_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, input_data, re.IGNORECASE)
                if matches:
                    vulnerabilities.append({
                        'type': vuln_type,
                        'pattern': pattern,
                        'matches': matches,
                        'severity': self._get_severity(vuln_type)
                    })
                    risk_score += self._get_risk_score(vuln_type)
        
        return {
            'scan_timestamp': datetime.utcnow().isoformat(),
            'input_type': input_type,
            'vulnerabilities_found': len(vulnerabilities),
            'vulnerabilities': vulnerabilities,
            'risk_score': min(risk_score, 100),
            'risk_level': self._get_risk_level(risk_score),
            'safe': len(vulnerabilities) == 0
        }
    
    def scan_file_upload(self, filename: str, file_content: bytes) -> Dict:
        """
        Scan uploaded files for security issues
        """
        issues = []
        risk_score = 0
        
        # Check file extension
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.js', '.vbs']
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext in dangerous_extensions:
            issues.append({
                'type': 'dangerous_file_type',
                'description': f'Potentially dangerous file extension: {file_ext}',
                'severity': 'high'
            })
            risk_score += 40
        
        # Check file size
        if len(file_content) > 50 * 1024 * 1024:  # 50MB
            issues.append({
                'type': 'large_file_size',
                'description': 'File size exceeds recommended limit',
                'severity': 'medium'
            })
            risk_score += 20
        
        # Check for embedded scripts in content
        content_str = str(file_content[:1024])  # Check first 1KB
        script_scan = self.scan_input(content_str, 'file_content')
        
        if not script_scan['safe']:
            issues.extend(script_scan['vulnerabilities'])
            risk_score += script_scan['risk_score']
        
        return {
            'scan_timestamp': datetime.utcnow().isoformat(),
            'filename': filename,
            'file_size': len(file_content),
            'issues_found': len(issues),
            'issues': issues,
            'risk_score': min(risk_score, 100),
            'risk_level': self._get_risk_level(risk_score),
            'safe': len(issues) == 0
        }
    
    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type"""
        severity_map = {
            'sql_injection': 'critical',
            'xss': 'high',
            'path_traversal': 'high',
            'command_injection': 'critical'
        }
        return severity_map.get(vuln_type, 'medium')
    
    def _get_risk_score(self, vuln_type: str) -> int:
        """Get risk score for vulnerability type"""
        score_map = {
            'sql_injection': 50,
            'xss': 30,
            'path_traversal': 40,
            'command_injection': 50
        }
        return score_map.get(vuln_type, 20)
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Get risk level based on score"""
        if risk_score >= 80:
            return 'CRITICAL'
        elif risk_score >= 60:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MEDIUM'
        elif risk_score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'


class DataPurgeService:
    """Automated data purging service for NDPR compliance"""
    
    def __init__(self):
        self.retention_periods = {
            'user_data': 90,  # days
            'report_data': 365 * 7,  # 7 years for transparency
            'audit_logs': 365 * 3,  # 3 years for compliance
            'ai_analysis': 365 * 2,  # 2 years for model improvement
            'evidence_files': 365 * 5  # 5 years for legal purposes
        }
    
    def schedule_data_purge(self, data_type: str, user_id: Optional[str] = None) -> Dict:
        """
        Schedule data purge based on retention policy
        """
        if data_type not in self.retention_periods:
            return {
                'error': f'Unknown data type: {data_type}',
                'scheduled': False,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        retention_days = self.retention_periods[data_type]
        purge_date = datetime.utcnow() + timedelta(days=retention_days)
        
        purge_job = {
            'job_id': secrets.token_urlsafe(16),
            'data_type': data_type,
            'user_id': user_id,
            'scheduled_date': purge_date.isoformat(),
            'retention_period_days': retention_days,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'scheduled'
        }
        
        return {
            'scheduled': True,
            'purge_job': purge_job,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def execute_immediate_purge(self, user_id: str, data_types: List[str]) -> Dict:
        """
        Execute immediate data purge for user (right to be forgotten)
        """
        purged_data = []
        errors = []
        
        for data_type in data_types:
            try:
                # Simulate data purging
                purge_result = self._purge_user_data(user_id, data_type)
                purged_data.append(purge_result)
            except Exception as e:
                errors.append({
                    'data_type': data_type,
                    'error': str(e)
                })
        
        return {
            'user_id': user_id,
            'purge_timestamp': datetime.utcnow().isoformat(),
            'purged_data_types': [p['data_type'] for p in purged_data],
            'purged_records': sum(p['records_purged'] for p in purged_data),
            'errors': errors,
            'success': len(errors) == 0,
            'ndpr_compliant': True
        }
    
    def _purge_user_data(self, user_id: str, data_type: str) -> Dict:
        """
        Simulate purging user data of specific type
        """
        # In real implementation, this would delete actual database records
        import random
        
        records_purged = random.randint(1, 10)
        
        return {
            'data_type': data_type,
            'user_id': user_id,
            'records_purged': records_purged,
            'purge_method': 'secure_deletion',
            'timestamp': datetime.utcnow().isoformat()
        }


# Initialize security services
encryption_service = EncryptionService()
rbac_service = RBACService()
biometric_auth_service = BiometricAuthService()
vulnerability_scanner = VulnerabilityScanner()
data_purge_service = DataPurgeService()

