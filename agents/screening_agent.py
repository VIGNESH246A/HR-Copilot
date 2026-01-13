"""
Resume Screening Agent
"""
from typing import Dict, Any, List, Optional
from services.llm_service import llm_service
from services.database_service import db_service
from tools.resume_parser import resume_parser
from tools.document_generator import document_generator
from models.schemas import ScreeningResult, CandidateStatus
import uuid


class ScreeningAgent:
    """Agent for screening and evaluating candidates"""
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute screening task"""
        
        job_id = task_data.get('job_id')
        resume_path = task_data.get('resume_path')
        candidate_email = task_data.get('candidate_email')
        
        if not job_id:
            return {'success': False, 'error': 'job_id required'}
        
        if not resume_path:
            return {'success': False, 'error': 'resume_path required'}
        
        # Get job requirements
        job = db_service.get_job(job_id)
        if not job:
            return {'success': False, 'error': f'Job {job_id} not found'}
        
        # Parse resume
        try:
            resume_data = resume_parser.parse_resume(resume_path)
        except Exception as e:
            return {'success': False, 'error': f'Failed to parse resume: {str(e)}'}
        
        # Extract job requirements
        job_requirements = llm_service.extract_job_requirements(job['description'])
        
        # Compare candidate to job
        screening_result = llm_service.compare_candidate_to_job(
            resume_data,
            job_requirements
        )
        
        # Create candidate record
        candidate_id = str(uuid.uuid4())
        
        db_service.create_candidate({
            'id': candidate_id,
            'name': resume_data.get('candidate_name', 'Unknown'),
            'email': candidate_email or resume_data.get('email', 'unknown@email.com'),
            'phone': resume_data.get('phone'),
            'resume_path': resume_path,
            'parsed_data': resume_data,
            'job_id': job_id,
            'status': self._determine_status(screening_result['match_score']),
            'match_score': screening_result['match_score']
        })
        
        # Generate screening report
        report = document_generator.generate_screening_report(
            resume_data,
            job_requirements,
            screening_result
        )
        
        return {
            'success': True,
            'candidate_id': candidate_id,
            'screening_result': screening_result,
            'report': report,
            'message': f"✅ Screened candidate: {resume_data.get('candidate_name')} (Match: {screening_result['match_score']}%)",
            'next_actions': self._get_next_actions(screening_result)
        }
    
    def batch_screen(
        self, 
        job_id: str, 
        resume_paths: List[str]
    ) -> Dict[str, Any]:
        """Screen multiple resumes"""
        
        results = []
        
        for resume_path in resume_paths:
            result = self.execute({
                'job_id': job_id,
                'resume_path': resume_path
            })
            results.append(result)
        
        # Sort by match score
        successful_results = [r for r in results if r['success']]
        successful_results.sort(
            key=lambda x: x['screening_result']['match_score'], 
            reverse=True
        )
        
        return {
            'success': True,
            'total_screened': len(results),
            'successful': len(successful_results),
            'failed': len(results) - len(successful_results),
            'top_candidates': [
                {
                    'candidate_id': r['candidate_id'],
                    'match_score': r['screening_result']['match_score'],
                    'recommendation': r['screening_result']['recommendation']
                }
                for r in successful_results[:5]
            ],
            'message': f"✅ Screened {len(results)} candidates. Top match: {successful_results[0]['screening_result']['match_score']}%"
        }
    
    def rank_candidates(self, job_id: str) -> List[Dict[str, Any]]:
        """Rank all candidates for a job"""
        
        candidates = db_service.list_candidates(job_id=job_id)
        
        # Sort by match score
        ranked = sorted(
            candidates,
            key=lambda c: c.get('match_score', 0),
            reverse=True
        )
        
        return [
            {
                'rank': idx + 1,
                'candidate_id': c['id'],
                'name': c['name'],
                'email': c['email'],
                'match_score': c.get('match_score', 0),
                'status': c['status']
            }
            for idx, c in enumerate(ranked)
        ]
    
    def filter_candidates(
        self,
        job_id: str,
        min_score: float = 70.0,
        required_skills: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Filter candidates by criteria"""
        
        candidates = db_service.list_candidates(job_id=job_id)
        
        filtered = []
        
        for candidate in candidates:
            # Check score
            if candidate.get('match_score', 0) < min_score:
                continue
            
            # Check skills if specified
            if required_skills:
                parsed_data = candidate.get('parsed_data', {})
                candidate_skills = [
                    s.lower() for s in parsed_data.get('skills', [])
                ]
                
                has_required = all(
                    skill.lower() in candidate_skills 
                    for skill in required_skills
                )
                
                if not has_required:
                    continue
            
            filtered.append(candidate)
        
        return filtered
    
    def generate_shortlist(
        self,
        job_id: str,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """Generate shortlist of top candidates"""
        
        ranked = self.rank_candidates(job_id)
        shortlist = ranked[:top_n]
        
        return {
            'success': True,
            'job_id': job_id,
            'shortlist': shortlist,
            'total_candidates': len(ranked),
            'shortlisted': len(shortlist),
            'message': f"✅ Generated shortlist of {len(shortlist)} candidates"
        }
    
    def _determine_status(self, match_score: float) -> str:
        """Determine candidate status based on score"""
        
        if match_score >= 80:
            return CandidateStatus.INTERVIEW.value
        elif match_score >= 60:
            return CandidateStatus.SCREENING.value
        else:
            return CandidateStatus.NEW.value
    
    def _get_next_actions(
        self, 
        screening_result: Dict[str, Any]
    ) -> List[str]:
        """Suggest next actions based on screening"""
        
        recommendation = screening_result.get('recommendation', '')
        
        if recommendation == 'strong_match':
            return [
                'Schedule interview immediately',
                'Send interview invitation email',
                'Prepare interview questions'
            ]
        elif recommendation == 'good_match':
            return [
                'Review resume in detail',
                'Consider for phone screening',
                'Compare with other candidates'
            ]
        elif recommendation == 'potential_match':
            return [
                'Keep in pipeline',
                'Request additional information',
                'Consider for future positions'
            ]
        else:
            return [
                'Send rejection email',
                'Archive application',
                'Provide feedback if requested'
            ]


# Global screening agent instance
screening_agent = ScreeningAgent()