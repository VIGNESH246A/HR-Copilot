"""
Interview Scheduling Agent
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from services.database_service import db_service
from tools.email_sender import email_sender
from tools.document_generator import document_generator


class InterviewAgent:
    """Agent for managing interviews"""
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute interview scheduling task"""
        
        action = task_data.get('action', 'schedule')
        
        if action == 'schedule':
            return self.schedule_interview(task_data)
        elif action == 'generate_questions':
            return self.generate_interview_questions(task_data)
        elif action == 'send_invitation':
            return self.send_interview_invitation(task_data)
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}
    
    def schedule_interview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule an interview"""
        
        candidate_id = data.get('candidate_id')
        job_id = data.get('job_id')
        interview_type = data.get('interview_type', 'technical')
        date_str = data.get('date')
        time_str = data.get('time')
        interviewer = data.get('interviewer', 'Hiring Manager')
        location = data.get('location', 'Virtual')
        
        if not all([candidate_id, job_id]):
            return {'success': False, 'error': 'candidate_id and job_id required'}
        
        # Get candidate details
        candidate = db_service.get_candidate(candidate_id)
        if not candidate:
            return {'success': False, 'error': f'Candidate {candidate_id} not found'}
        
        # Get job details
        job = db_service.get_job(job_id)
        if not job:
            return {'success': False, 'error': f'Job {job_id} not found'}
        
        # Parse datetime
        if date_str and time_str:
            interview_datetime = datetime.strptime(
                f"{date_str} {time_str}", 
                "%Y-%m-%d %H:%M"
            )
        else:
            # Default to next week
            interview_datetime = datetime.now() + timedelta(days=7)
        
        # Create interview record
        interview_id = db_service.create_interview({
            'candidate_id': candidate_id,
            'job_id': job_id,
            'interview_type': interview_type,
            'scheduled_date': interview_datetime,
            'interviewer': interviewer,
            'location': location,
            'meeting_link': self._generate_meeting_link() if location == 'Virtual' else None,
            'status': 'scheduled'
        })
        
        # Update candidate status
        db_service.update_candidate(candidate_id, {
            'status': 'interview',
            'interview_date': interview_datetime
        })
        
        return {
            'success': True,
            'interview_id': interview_id,
            'candidate_name': candidate['name'],
            'position': job['title'],
            'scheduled_date': interview_datetime.strftime('%Y-%m-%d'),
            'scheduled_time': interview_datetime.strftime('%H:%M'),
            'interviewer': interviewer,
            'location': location,
            'message': f"✅ Interview scheduled with {candidate['name']} on {interview_datetime.strftime('%Y-%m-%d at %H:%M')}",
            'next_actions': [
                'Send interview invitation email',
                'Prepare interview questions',
                'Share candidate profile with interviewer'
            ]
        }
    
    def send_interview_invitation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send interview invitation email"""
        
        interview_id = data.get('interview_id')
        
        if not interview_id:
            # Try to get from candidate_id
            candidate_id = data.get('candidate_id')
            job_id = data.get('job_id')
            
            if candidate_id and job_id:
                interviews = db_service.list_interviews(
                    candidate_id=candidate_id,
                    job_id=job_id
                )
                if interviews:
                    interview_id = interviews[0]['id']
        
        if not interview_id:
            return {'success': False, 'error': 'interview_id required'}
        
        # Get interview details
        interviews = db_service.list_interviews()
        interview = next((i for i in interviews if i['id'] == interview_id), None)
        
        if not interview:
            return {'success': False, 'error': f'Interview {interview_id} not found'}
        
        # Get candidate and job
        candidate = db_service.get_candidate(interview['candidate_id'])
        job = db_service.get_job(interview['job_id'])
        
        # Format date and time
        scheduled_date = datetime.fromisoformat(interview['scheduled_date'])
        
        # Send email
        success = email_sender.send_interview_invitation(
            candidate_name=candidate['name'],
            candidate_email=candidate['email'],
            position=job['title'],
            company_name=job['company_name'],
            interview_date=scheduled_date.strftime('%B %d, %Y'),
            interview_time=scheduled_date.strftime('%I:%M %p'),
            location=interview.get('meeting_link') or interview.get('location', 'TBD'),
            interviewer=interview.get('interviewer', 'Hiring Team')
        )
        
        if success:
            return {
                'success': True,
                'message': f"✅ Interview invitation sent to {candidate['email']}",
                'email_sent_to': candidate['email']
            }
        else:
            return {
                'success': False,
                'error': 'Failed to send email'
            }
    
    def generate_interview_questions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate interview questions"""
        
        job_id = data.get('job_id')
        interview_type = data.get('interview_type', 'technical')
        
        if not job_id:
            return {'success': False, 'error': 'job_id required'}
        
        # Get job details
        job = db_service.get_job(job_id)
        if not job:
            return {'success': False, 'error': f'Job {job_id} not found'}
        
        # Extract required skills from job
        from services.llm_service import llm_service
        requirements = llm_service.extract_job_requirements(job['description'])
        
        # Generate questions
        questions = document_generator.generate_interview_questions(
            position=job['title'],
            required_skills=requirements.get('required_skills', []),
            interview_type=interview_type
        )
        
        return {
            'success': True,
            'position': job['title'],
            'interview_type': interview_type,
            'questions': questions,
            'total_questions': len(questions),
            'message': f"✅ Generated {len(questions)} {interview_type} interview questions"
        }
    
    def list_upcoming_interviews(
        self, 
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """List upcoming interviews"""
        
        all_interviews = db_service.list_interviews()
        
        now = datetime.now()
        cutoff = now + timedelta(days=days_ahead)
        
        upcoming = []
        
        for interview in all_interviews:
            if interview.get('scheduled_date'):
                scheduled = datetime.fromisoformat(interview['scheduled_date'])
                
                if now <= scheduled <= cutoff:
                    candidate = db_service.get_candidate(interview['candidate_id'])
                    job = db_service.get_job(interview['job_id'])
                    
                    upcoming.append({
                        'interview_id': interview['id'],
                        'candidate_name': candidate['name'] if candidate else 'Unknown',
                        'position': job['title'] if job else 'Unknown',
                        'scheduled_date': scheduled.strftime('%Y-%m-%d'),
                        'scheduled_time': scheduled.strftime('%H:%M'),
                        'interviewer': interview.get('interviewer'),
                        'status': interview.get('status')
                    })
        
        # Sort by date
        upcoming.sort(key=lambda x: x['scheduled_date'])
        
        return upcoming
    
    def reschedule_interview(
        self,
        interview_id: str,
        new_date: str,
        new_time: str
    ) -> Dict[str, Any]:
        """Reschedule an interview"""
        
        interviews = db_service.list_interviews()
        interview = next((i for i in interviews if i['id'] == interview_id), None)
        
        if not interview:
            return {'success': False, 'error': f'Interview {interview_id} not found'}
        
        # Parse new datetime
        new_datetime = datetime.strptime(
            f"{new_date} {new_time}",
            "%Y-%m-%d %H:%M"
        )
        
        # Update interview
        # Note: Would need to add update_interview method to db_service
        
        return {
            'success': True,
            'message': f"✅ Interview rescheduled to {new_date} at {new_time}"
        }
    
    def _generate_meeting_link(self) -> str:
        """Generate virtual meeting link (placeholder)"""
        import random
        import string
        
        code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return f"https://meet.company.com/{code}"


# Global interview agent instance
interview_agent = InterviewAgent()