"""
Document generation tool for JDs, offer letters, etc.
"""
from typing import Dict, Any, List
from datetime import datetime
from services.llm_service import llm_service
import json


class DocumentGenerator:
    """Generate HR documents"""
    
    def generate_job_description(
        self,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate complete job description"""
        
        prompt = f"""
Create a comprehensive job description based on these requirements:

{json.dumps(requirements, indent=2)}

Generate a professional job description including:
1. Compelling job title
2. Company overview (if company name provided)
3. Role summary
4. Key responsibilities (5-7 bullet points)
5. Required qualifications
6. Preferred qualifications
7. Benefits and perks
8. Equal opportunity statement
"""
        
        schema = {
            "title": "string",
            "company_overview": "string",
            "role_summary": "string",
            "responsibilities": ["string"],
            "required_qualifications": ["string"],
            "preferred_qualifications": ["string"],
            "benefits": ["string"],
            "equal_opportunity_statement": "string"
        }
        
        result = llm_service.generate_structured_output(
            prompt=prompt,
            output_schema=schema,
            system_prompt="You are an expert HR professional creating engaging job descriptions."
        )
        
        # Format as complete document
        jd_text = self._format_job_description(result)
        result['full_text'] = jd_text
        
        return result
    
    def _format_job_description(self, jd_data: Dict[str, Any]) -> str:
        """Format JD as readable text"""
        
        sections = []
        
        sections.append(f"# {jd_data['title']}\n")
        
        if jd_data.get('company_overview'):
            sections.append(f"## About Us\n{jd_data['company_overview']}\n")
        
        sections.append(f"## Role Overview\n{jd_data['role_summary']}\n")
        
        sections.append("## Key Responsibilities")
        for resp in jd_data['responsibilities']:
            sections.append(f"• {resp}")
        sections.append("")
        
        sections.append("## Required Qualifications")
        for qual in jd_data['required_qualifications']:
            sections.append(f"• {qual}")
        sections.append("")
        
        if jd_data.get('preferred_qualifications'):
            sections.append("## Preferred Qualifications")
            for qual in jd_data['preferred_qualifications']:
                sections.append(f"• {qual}")
            sections.append("")
        
        if jd_data.get('benefits'):
            sections.append("## Benefits")
            for benefit in jd_data['benefits']:
                sections.append(f"• {benefit}")
            sections.append("")
        
        if jd_data.get('equal_opportunity_statement'):
            sections.append(f"## Equal Opportunity\n{jd_data['equal_opportunity_statement']}")
        
        return "\n".join(sections)
    
    def generate_offer_letter(
        self,
        candidate_name: str,
        position: str,
        company_name: str,
        start_date: str,
        salary: str,
        benefits: List[str],
        reporting_to: str = None
    ) -> str:
        """Generate offer letter"""
        
        prompt = f"""
Create a professional job offer letter with these details:

Candidate: {candidate_name}
Position: {position}
Company: {company_name}
Start Date: {start_date}
Salary: {salary}
Benefits: {', '.join(benefits)}
Reports To: {reporting_to or 'To be determined'}

Include:
1. Formal greeting
2. Expression of enthusiasm
3. Position details
4. Compensation and benefits
5. Start date
6. Reporting structure
7. Next steps
8. Professional closing
"""
        
        return llm_service.generate_response(
            prompt=prompt,
            system_prompt="You are an HR professional creating formal offer letters."
        )
    
    def generate_interview_questions(
        self,
        position: str,
        required_skills: List[str],
        interview_type: str = "technical"
    ) -> List[Dict[str, str]]:
        """Generate interview questions"""
        
        schema = {
            "questions": [
                {
                    "question": "string",
                    "type": "string (technical|behavioral|situational)",
                    "focus_area": "string",
                    "sample_answer": "string"
                }
            ]
        }
        
        prompt = f"""
Generate {interview_type} interview questions for:

Position: {position}
Key Skills: {', '.join(required_skills)}

Create 8-10 questions covering:
- Technical competency
- Problem-solving
- Communication
- Cultural fit
- Specific skills assessment

For each question, provide:
- The question text
- Question type
- Focus area
- Sample good answer
"""
        
        result = llm_service.generate_structured_output(
            prompt=prompt,
            output_schema=schema,
            system_prompt="You are an expert interviewer creating assessment questions."
        )
        
        return result.get('questions', [])
    
    def generate_rejection_letter(
        self,
        candidate_name: str,
        position: str,
        company_name: str,
        reason: str = "general"
    ) -> str:
        """Generate rejection letter"""
        
        prompt = f"""
Create a professional, empathetic rejection letter:

Candidate: {candidate_name}
Position: {position}
Company: {company_name}
Reason: {reason}

The letter should:
1. Thank the candidate
2. Deliver the decision respectfully
3. Provide brief, constructive feedback if appropriate
4. Encourage future applications
5. Maintain positive brand image
"""
        
        return llm_service.generate_response(
            prompt=prompt,
            system_prompt="You are an HR professional creating respectful rejection letters."
        )
    
    def generate_screening_report(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        screening_results: Dict[str, Any]
    ) -> str:
        """Generate candidate screening report"""
        
        report_parts = []
        
        report_parts.append("# CANDIDATE SCREENING REPORT\n")
        report_parts.append(f"**Candidate:** {candidate_data.get('name', 'Unknown')}")
        report_parts.append(f"**Position:** {job_requirements.get('position', 'Unknown')}")
        report_parts.append(f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}\n")
        
        report_parts.append(f"## Match Score: {screening_results.get('match_score', 0)}%\n")
        
        report_parts.append("## Matching Skills")
        for skill in screening_results.get('matching_skills', []):
            report_parts.append(f"✓ {skill}")
        report_parts.append("")
        
        if screening_results.get('missing_skills'):
            report_parts.append("## Missing Skills")
            for skill in screening_results['missing_skills']:
                report_parts.append(f"✗ {skill}")
            report_parts.append("")
        
        report_parts.append("## Strengths")
        for strength in screening_results.get('strengths', []):
            report_parts.append(f"• {strength}")
        report_parts.append("")
        
        if screening_results.get('concerns'):
            report_parts.append("## Concerns")
            for concern in screening_results['concerns']:
                report_parts.append(f"• {concern}")
            report_parts.append("")
        
        report_parts.append(f"## Summary\n{screening_results.get('summary', '')}\n")
        report_parts.append(f"## Recommendation\n{screening_results.get('recommendation', '')}")
        
        return "\n".join(report_parts)


# Global document generator instance
document_generator = DocumentGenerator()