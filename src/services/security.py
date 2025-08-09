import os
from datetime import datetime

class SecurityService:
    # ... other methods ...

    def scan_file(self, filename, file_content):
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

        # Scan entire file (stream for large files)
        chunk_size = 4096
        full_scan = ""
        if len(file_content) > 5 * 1024 * 1024:  # >5MB, use streaming
            for i in range(0, len(file_content), chunk_size):
                full_scan += str(file_content[i:i+chunk_size])
        else:
            full_scan = str(file_content)

        script_scan = self.scan_input(full_scan, 'file_content')
        if not script_scan['safe']:
            issues.extend(script_scan['vulnerabilities'])
            risk_score += script_scan['risk_score']

        # Quarantine logic for flagged files
        if len(issues) > 0:
            self.quarantine_file(filename, file_content, issues)

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

    def quarantine_file(self, filename, file_content, issues):
        # Quarantine stub — implement actual storage and alert logic as needed
        # For now, just log the event
        print(f"File {filename} quarantined due to: {issues}")