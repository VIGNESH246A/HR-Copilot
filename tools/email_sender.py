"""
Email automation tool
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from config import settings


class EmailSender:
    """Send automated emails to candidates"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        
        # Email templates
        self.templates = {
            "application_received": {
                "subject": "Application Received - {position}",
                "body": """
Dear {candidate_name},

Thank you for applying for the {position} position at {company_name}.

We have received your application and our team is currently reviewing it. 
We will get back to you within {timeline} with next steps.

Best regards,
{company_name} HR Team
"""
            },
            "interview_invitation": {
                "subject": "Interview Invitation - {position}",
                "body": """
Dear {candidate_name},

We are pleased to invite you for an interview for the {position} position.

Interview Details:
- Date: {interview_date}
- Time: {interview_time}
- Location: {location}
- Interviewer: {interviewer}

Please confirm your attendance by replying to this email.

Best regards,
{company_name} HR Team
"""
            },
            "rejection": {
                "subject": "Update on Your Application - {position}",
                "body": """
Dear {candidate_name},

Thank you for your interest in the {position} position at {company_name}.

After careful consideration, we have decided to move forward with other candidates 
whose qualifications more closely match our current needs.

We appreciate the time you invested in the application process and encourage you 
to apply for future opportunities that match your skills and experience.

Best regards,
{company_name} HR Team
"""
            },
            "offer_letter": {
                "subject": "Job Offer - {position}",
                "body": """
Dear {candidate_name},

We are delighted to offer you the position of {position} at {company_name}.

Offer Details:
- Position: {position}
- Start Date: {start_date}
- Salary: {salary}
- Benefits: {benefits}

Please review the attached offer letter and let us know your decision by {response_deadline}.

We look forward to welcoming you to our team!

Best regards,
{company_name} HR Team
"""
            }
        }
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        html: bool = False
    ) -> bool:
        """Send email"""
        
        if not self._is_configured():
            print("⚠️  Email not configured. Simulating email send...")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {body[:200]}...")
            return True
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Attach body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                
                recipients = [to_email] + (cc or [])
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False
    
    def send_template_email(
        self,
        template_name: str,
        to_email: str,
        variables: Dict[str, Any],
        cc: Optional[List[str]] = None
    ) -> bool:
        """Send email using template"""
        
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.templates[template_name]
        
        # Replace variables in subject and body
        subject = template["subject"].format(**variables)
        body = template["body"].format(**variables)
        
        return self.send_email(to_email, subject, body, cc)
    
    def send_application_received(
        self,
        candidate_name: str,
        candidate_email: str,
        position: str,
        company_name: str,
        timeline: str = "5-7 business days"
    ) -> bool:
        """Send application received confirmation"""
        
        return self.send_template_email(
            "application_received",
            candidate_email,
            {
                "candidate_name": candidate_name,
                "position": position,
                "company_name": company_name,
                "timeline": timeline
            }
        )
    
    def send_interview_invitation(
        self,
        candidate_name: str,
        candidate_email: str,
        position: str,
        company_name: str,
        interview_date: str,
        interview_time: str,
        location: str,
        interviewer: str
    ) -> bool:
        """Send interview invitation"""
        
        return self.send_template_email(
            "interview_invitation",
            candidate_email,
            {
                "candidate_name": candidate_name,
                "position": position,
                "company_name": company_name,
                "interview_date": interview_date,
                "interview_time": interview_time,
                "location": location,
                "interviewer": interviewer
            }
        )
    
    def send_rejection(
        self,
        candidate_name: str,
        candidate_email: str,
        position: str,
        company_name: str
    ) -> bool:
        """Send rejection email"""
        
        return self.send_template_email(
            "rejection",
            candidate_email,
            {
                "candidate_name": candidate_name,
                "position": position,
                "company_name": company_name
            }
        )
    
    def send_offer_letter(
        self,
        candidate_name: str,
        candidate_email: str,
        position: str,
        company_name: str,
        start_date: str,
        salary: str,
        benefits: str,
        response_deadline: str
    ) -> bool:
        """Send offer letter"""
        
        return self.send_template_email(
            "offer_letter",
            candidate_email,
            {
                "candidate_name": candidate_name,
                "position": position,
                "company_name": company_name,
                "start_date": start_date,
                "salary": salary,
                "benefits": benefits,
                "response_deadline": response_deadline
            }
        )
    
    def _is_configured(self) -> bool:
        """Check if email is configured"""
        return all([
            self.smtp_host,
            self.smtp_port,
            self.smtp_user,
            self.smtp_password,
            self.from_email
        ])


# Global email sender instance
email_sender = EmailSender()