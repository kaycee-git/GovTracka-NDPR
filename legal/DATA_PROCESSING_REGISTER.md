# GovTracka Data Processing Register
## GAID Article 4.2 Compliance Document

**Document Version:** 1.0  
**Date:** July 26, 2025  
**Data Controller:** GovTracka Nigeria Limited  
**NDPC Registration:** NDPC/DC/2025/0847  
**DPO:** Dr. Adebayo Ogundimu (dpo@govtracka.ng)  

---

## Processing Activity 1: User Registration and Account Management

**Purpose:** Enable citizen participation in transparency platform  
**Legal Basis:** Consent (NDPA 2023 Section 11)  
**Data Categories:**
- Personal identifiers (name, email, phone number)
- Authentication credentials (hashed passwords)
- Account preferences and settings
- Registration timestamp and IP address

**Data Subjects:** Nigerian citizens, NGO representatives, government officials  
**Recipients:** Internal staff (customer support, technical team)  
**Third Country Transfers:** None  
**Retention Period:** Account lifetime + 90 days post-deletion  
**Security Measures:**
- PBKDF2 password hashing with salt
- AES-256 encryption for stored data
- TLS 1.3 for data transmission
- Role-based access controls

**Data Subject Rights:** Full rights package (access, rectification, erasure, portability, objection)

---

## Processing Activity 2: Project Reporting and Evidence Collection

**Purpose:** Collect citizen reports on government project irregularities  
**Legal Basis:** Legitimate Interest (NDPA 2023 Section 12) - Public transparency  
**Data Categories:**
- Project information (name, location, budget, contractor)
- Evidence files (photos, videos, audio recordings)
- GPS coordinates and timestamps
- Reporter identification (pseudonymized)
- Report metadata and status

**Data Subjects:** Citizen reporters, project stakeholders  
**Recipients:** 
- Internal: Verification team, AI analysis systems
- External: Community moderators, NGO partners (anonymized data only)

**Third Country Transfers:** Limited - Anonymized images to AI processing services with SCCs  
**Retention Period:** 7 years for legal evidence purposes  
**Security Measures:**
- End-to-end encryption for sensitive evidence
- Blockchain anchoring for evidence integrity
- Automatic face anonymization in photos
- GPS coordinate obfuscation (100m radius)

**Data Subject Rights:** Access, rectification, restricted erasure (evidence preservation), objection

---

## Processing Activity 3: Community Verification and Voting

**Purpose:** Enable community-driven verification of project reports  
**Legal Basis:** Consent (NDPA 2023 Section 11)  
**Data Categories:**
- Voting records and preferences
- Community comments and discussions
- Verification scores and ratings
- Moderator actions and decisions
- User interaction patterns

**Data Subjects:** Community members, moderators, NGO partners  
**Recipients:** Internal verification team, public (aggregated statistics only)  
**Third Country Transfers:** None  
**Retention Period:** 5 years for transparency and accountability  
**Security Measures:**
- Pseudonymization of user identities
- Encrypted storage of voting records
- Access controls for moderator functions
- Audit trails for all verification actions

**Data Subject Rights:** Full rights package with community impact considerations

---

## Processing Activity 4: USSD Communications and Mobile Access

**Purpose:** Provide mobile phone access to platform features  
**Legal Basis:** Legitimate Interest (NDPA 2023 Section 12) - Digital inclusion  
**Data Categories:**
- Phone numbers and carrier information
- USSD session data and menu selections
- SMS message content and delivery status
- Voice recording transcriptions
- Session timestamps and duration

**Data Subjects:** Mobile phone users (primarily feature phone users)  
**Recipients:** 
- Internal: USSD development team, customer support
- External: Telecommunications service providers

**Third Country Transfers:** None  
**Retention Period:** 2 years for service improvement and dispute resolution  
**Security Measures:**
- SMS encryption where supported by carriers
- Session token authentication
- Automatic session expiry (15 minutes)
- Secure API connections with telco providers

**Data Subject Rights:** Access, rectification, erasure, objection (with service impact notice)

---

## Processing Activity 5: AI Analysis and Fraud Detection

**Purpose:** Automated analysis of reports for fraud indicators and verification  
**Legal Basis:** Consent (NDPA 2023 Section 11) with opt-out option  
**Data Categories:**
- Anonymized image and video content
- Text analysis results and sentiment scores
- Anomaly detection scores and patterns
- AI model training data (anonymized)
- Algorithm decision logs

**Data Subjects:** Report submitters (anonymized)  
**Recipients:** 
- Internal: AI development team, verification specialists
- External: AI service providers (anonymized data only)

**Third Country Transfers:** Yes - Anonymized data to certified AI processors with SCCs  
**Retention Period:** 3 years for model improvement and accuracy validation  
**Security Measures:**
- Complete data anonymization before processing
- Encrypted API connections to AI services
- Regular algorithm bias testing
- Human oversight of AI decisions

**Data Subject Rights:** Access to AI decision logic, objection to automated processing, human review

---

## Processing Activity 6: Security Monitoring and Audit Logging

**Purpose:** Maintain platform security and regulatory compliance  
**Legal Basis:** Legal Obligation (NDPA 2023 Section 13) - Security requirements  
**Data Categories:**
- User access logs and authentication events
- System security events and alerts
- Administrative actions and changes
- Error logs and performance metrics
- Incident response records

**Data Subjects:** All platform users and administrators  
**Recipients:** Internal security team, DPO, external auditors (anonymized)  
**Third Country Transfers:** None  
**Retention Period:** 7 years for legal and regulatory requirements  
**Security Measures:**
- Immutable log storage with cryptographic integrity
- Encrypted log transmission and storage
- Access controls limited to security personnel
- Regular log integrity verification

**Data Subject Rights:** Limited access (security considerations), rectification where appropriate

---

## Processing Activity 7: Analytics and Platform Improvement

**Purpose:** Understand platform usage and improve user experience  
**Legal Basis:** Consent (NDPA 2023 Section 11) - Optional with granular controls  
**Data Categories:**
- Aggregated usage statistics
- Feature adoption metrics
- Performance and error analytics
- User journey and interaction patterns
- A/B testing results

**Data Subjects:** Consenting platform users  
**Recipients:** Internal product development team, senior management  
**Third Country Transfers:** None  
**Retention Period:** 2 years for trend analysis and product planning  
**Security Measures:**
- Data aggregation and anonymization
- Differential privacy techniques
- Consent-based data collection only
- Regular data minimization reviews

**Data Subject Rights:** Full rights package, easy consent withdrawal

---

## Processing Activity 8: Communication and Notifications

**Purpose:** Send important updates and notifications to users  
**Legal Basis:** Mixed - Legitimate Interest for security/legal notices, Consent for marketing  
**Data Categories:**
- Email addresses and communication preferences
- Notification delivery status and engagement
- Message content and templates
- Unsubscribe requests and preferences
- Communication frequency and timing

**Data Subjects:** All registered users  
**Recipients:** Internal communications team, email service providers  
**Third Country Transfers:** Limited - Email delivery through certified providers with SCCs  
**Retention Period:** 
- Security/Legal notices: 3 years
- Marketing communications: Until consent withdrawal
- Unsubscribe requests: Permanent (compliance)

**Security Measures:**
- Encrypted email transmission (TLS)
- Secure email service provider contracts
- Anti-spam and anti-phishing measures
- Bounce and delivery tracking

**Data Subject Rights:** Full rights package, easy unsubscribe mechanisms

---

## Data Sharing and Joint Processing

### Internal Data Sharing
All internal data sharing follows the principle of least privilege and is documented in access control matrices. Staff access is role-based and regularly audited.

### External Data Sharing
1. **NGO Partners:** Aggregated, anonymized statistics only
2. **Government Agencies:** No direct sharing; public transparency reports available
3. **Academic Researchers:** Anonymized datasets with explicit user consent
4. **Service Providers:** Minimal data necessary for service delivery only

### Joint Processing Arrangements
Currently no joint processing arrangements. Any future arrangements will be documented with appropriate data sharing agreements and DPIA assessments.

---

## Regular Review and Updates

**Review Frequency:** Quarterly or upon significant system changes  
**Last Review:** July 26, 2025  
**Next Review:** October 26, 2025  
**Review Authority:** Dr. Adebayo Ogundimu (DPO)  

**Change Log:**
- v1.0 (July 26, 2025): Initial register creation for NDPA compliance

---

**Document Prepared By:** Dr. Adebayo Ogundimu, DPO  
**Approved By:** Kelechi Odenigbo, CEO  
**NDPC Filing Date:** July 26, 2025  
**Document Classification:** Internal/Regulatory  

*This register is maintained in compliance with GAID Article 4.2 and is available for inspection by the Nigeria Data Protection Commission upon request.*

