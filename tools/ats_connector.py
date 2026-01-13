"""
ATS (Applicant Tracking System) Integration
"""
from typing import Dict, Any, List, Optional
import requests
from config import settings


class ATSConnector:
    """Connect to external ATS platforms"""
    
    def __init__(self):
        self.api_key = settings.ATS_API_KEY
        self.api_url = settings.ATS_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def is_configured(self) -> bool:
        """Check if ATS is configured"""
        return bool(self.api_key and self.api_url)
    
    def post_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post job to ATS"""
        
        if not self.is_configured():
            return {
                'success': False,
                'error': 'ATS not configured'
            }
        
        try:
            response = requests.post(
                f"{self.api_url}/jobs",
                json=job_data,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            return {
                'success': True,
                'ats_job_id': response.json().get('id'),
                'message': 'Job posted to ATS successfully'
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'ATS API error: {str(e)}'
            }
    
    def update_job(
        self,
        ats_job_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update job in ATS"""
        
        if not self.is_configured():
            return {'success': False, 'error': 'ATS not configured'}
        
        try:
            response = requests.put(
                f"{self.api_url}/jobs/{ats_job_id}",
                json=updates,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            return {
                'success': True,
                'message': 'Job updated in ATS'
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'ATS API error: {str(e)}'
            }
    
    def close_job(self, ats_job_id: str) -> Dict[str, Any]:
        """Close job in ATS"""
        
        return self.update_job(ats_job_id, {'status': 'closed'})
    
    def sync_candidates(
        self,
        job_id: str,
        ats_job_id: str
    ) -> Dict[str, Any]:
        """Sync candidates from ATS"""
        
        if not self.is_configured():
            return {'success': False, 'error': 'ATS not configured'}
        
        try:
            response = requests.get(
                f"{self.api_url}/jobs/{ats_job_id}/candidates",
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            candidates = response.json()
            
            return {
                'success': True,
                'candidates': candidates,
                'total': len(candidates)
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'ATS API error: {str(e)}'
            }
    
    def push_candidate_status(
        self,
        ats_job_id: str,
        candidate_email: str,
        status: str
    ) -> Dict[str, Any]:
        """Update candidate status in ATS"""
        
        if not self.is_configured():
            return {'success': False, 'error': 'ATS not configured'}
        
        try:
            response = requests.post(
                f"{self.api_url}/jobs/{ats_job_id}/candidates/status",
                json={
                    'email': candidate_email,
                    'status': status
                },
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            return {
                'success': True,
                'message': 'Candidate status updated in ATS'
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'ATS API error: {str(e)}'
            }
    
    def get_job_boards(self) -> List[Dict[str, Any]]:
        """Get available job boards for posting"""
        
        if not self.is_configured():
            # Return mock data for development
            return [
                {'id': 'linkedin', 'name': 'LinkedIn', 'enabled': False},
                {'id': 'indeed', 'name': 'Indeed', 'enabled': False},
                {'id': 'glassdoor', 'name': 'Glassdoor', 'enabled': False},
                {'id': 'monster', 'name': 'Monster', 'enabled': False}
            ]
        
        try:
            response = requests.get(
                f"{self.api_url}/job-boards",
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException:
            return []
    
    def post_to_job_board(
        self,
        ats_job_id: str,
        board_id: str
    ) -> Dict[str, Any]:
        """Post job to specific job board"""
        
        if not self.is_configured():
            return {
                'success': False,
                'error': 'ATS not configured'
            }
        
        try:
            response = requests.post(
                f"{self.api_url}/jobs/{ats_job_id}/post/{board_id}",
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            return {
                'success': True,
                'message': f'Job posted to {board_id}'
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Job board posting error: {str(e)}'
            }


# Global ATS connector instance
ats_connector = ATSConnector()