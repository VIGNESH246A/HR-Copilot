"""
Job Description Generator Agent
"""
from typing import Dict, Any, Optional, List
from services.llm_service import llm_service
from services.database_service import db_service
from tools.document_generator import document_generator
from models.schemas import JobDescription, JobStatus
from datetime import datetime
import uuid


class JDGeneratorAgent:
    """Agent for generating job descriptions"""
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute JD generation task"""
        
        user_request = task_data.get('user_request', '')
        
        # Extract requirements from natural language
        requirements = llm_service.extract_job_requirements(user_request)
        
        # Generate complete JD
        jd_content = document_generator.generate_job_description(requirements)
        
        # Create structured JD object
        job_id = str(uuid.uuid4())
        
        job_description = JobDescription(
            id=job_id,
            title=jd_content['title'],
            company_name=requirements.get('company_name', 'Your Company'),
            department=requirements.get('department'),
            location=requirements.get('location', 'Remote/Hybrid'),
            employment_type=requirements.get('employment_type', 'Full-time'),
            description=jd_content['role_summary'],
            responsibilities=jd_content['responsibilities'],
            requirements=jd_content['required_qualifications'],
            preferred_qualifications=jd_content.get('preferred_qualifications', []),
            benefits=jd_content.get('benefits', []),
            salary_range=self._format_salary_range(requirements.get('salary_range')),
            status=JobStatus.DRAFT
        )
        
        # Save to database
        db_service.create_job({
            'id': job_id,
            'title': job_description.title,
            'company_name': job_description.company_name,
            'department': job_description.department,
            'location': job_description.location,
            'employment_type': job_description.employment_type,
            'description': jd_content['full_text'],
            'requirements': jd_content['required_qualifications'],
            'status': 'draft'
        })
        
        return {
            'success': True,
            'job_id': job_id,
            'job_description': job_description.dict(),
            'formatted_text': jd_content['full_text'],
            'message': f"✅ Job description created for {job_description.title}",
            'next_actions': [
                'Review and edit the job description',
                'Post to job boards',
                'Start screening candidates'
            ]
        }
    
    def update_jd(
        self, 
        job_id: str, 
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing job description"""
        
        # Get existing job
        job = db_service.get_job(job_id)
        if not job:
            return {
                'success': False,
                'error': f'Job {job_id} not found'
            }
        
        # Update fields
        db_service.update_job(job_id, updates)
        
        return {
            'success': True,
            'job_id': job_id,
            'message': '✅ Job description updated',
            'updated_fields': list(updates.keys())
        }
    
    def generate_multiple_versions(
        self, 
        requirements: Dict[str, Any],
        num_versions: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate multiple JD versions"""
        
        versions = []
        
        for i in range(num_versions):
            # Vary tone and style
            tone = ['professional', 'casual', 'innovative'][i % 3]
            
            requirements_copy = requirements.copy()
            requirements_copy['tone'] = tone
            
            jd_content = document_generator.generate_job_description(
                requirements_copy
            )
            
            versions.append({
                'version': i + 1,
                'tone': tone,
                'content': jd_content
            })
        
        return versions
    
    def optimize_for_seo(self, job_description: str) -> Dict[str, Any]:
        """Optimize JD for search engines"""
        
        prompt = f"""
Analyze this job description and provide SEO optimization suggestions:

{job_description}

Provide:
1. Recommended keywords to add
2. Title optimization suggestions
3. Meta description (150-160 characters)
4. Suggested tags
5. Improvements for better searchability
"""
        
        schema = {
            "keywords": ["string"],
            "optimized_title": "string",
            "meta_description": "string",
            "tags": ["string"],
            "improvements": ["string"]
        }
        
        return llm_service.generate_structured_output(
            prompt=prompt,
            output_schema=schema
        )
    
    def _format_salary_range(
        self, 
        salary_data: Optional[Dict[str, float]]
    ) -> Optional[str]:
        """Format salary range for display"""
        
        if not salary_data:
            return None
        
        min_sal = salary_data.get('min')
        max_sal = salary_data.get('max')
        
        if min_sal and max_sal:
            return f"${min_sal:,} - ${max_sal:,}"
        elif min_sal:
            return f"From ${min_sal:,}"
        elif max_sal:
            return f"Up to ${max_sal:,}"
        
        return None


# Global JD generator instance
jd_generator_agent = JDGeneratorAgent()