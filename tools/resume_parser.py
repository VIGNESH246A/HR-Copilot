"""
Resume parsing tool
"""
import re
import os
from typing import Dict, Any, List, Optional
import PyPDF2
import docx
from services.llm_service import llm_service


class ResumeParser:
    """Parse and extract information from resumes"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse resume file and extract structured data"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        # Extract text based on file type
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = self._extract_from_pdf(file_path)
        elif file_ext == '.docx':
            text = self._extract_from_docx(file_path)
        elif file_ext == '.txt':
            text = self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Parse structured data using LLM
        structured_data = self._parse_with_llm(text)
        structured_data['raw_text'] = text
        
        return structured_data
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return text.strip()
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        
        return text.strip()
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
        
        return text.strip()
    
    def _parse_with_llm(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text using LLM"""
        
        schema = {
            "candidate_name": "string",
            "email": "string or null",
            "phone": "string or null",
            "location": "string or null",
            "summary": "string or null",
            "skills": ["string"],
            "experience": [
                {
                    "company": "string",
                    "position": "string",
                    "duration": "string",
                    "description": "string"
                }
            ],
            "education": [
                {
                    "institution": "string",
                    "degree": "string",
                    "field": "string or null",
                    "year": "string or null"
                }
            ],
            "certifications": ["string"],
            "languages": ["string"],
            "total_experience_years": "integer or null"
        }
        
        prompt = f"""
Parse this resume and extract structured information:

{resume_text[:4000]}

Extract:
1. Contact information
2. Professional summary
3. Skills (technical and soft skills)
4. Work experience with details
5. Education
6. Certifications
7. Languages
8. Estimated total years of experience
"""
        
        try:
            return llm_service.generate_structured_output(
                prompt=prompt,
                output_schema=schema,
                system_prompt="You are an expert resume parser. Extract accurate information from resumes."
            )
        except Exception as e:
            # Fallback to basic parsing
            return self._basic_parse(resume_text)
    
    def _basic_parse(self, text: str) -> Dict[str, Any]:
        """Basic fallback parsing without LLM"""
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Extract phone
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        
        # Extract potential skills (simple keyword matching)
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'sql',
            'aws', 'docker', 'kubernetes', 'git', 'agile', 'scrum'
        ]
        
        text_lower = text.lower()
        skills = [skill for skill in skill_keywords if skill in text_lower]
        
        return {
            "candidate_name": "Unknown",
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "location": None,
            "summary": text[:200] if len(text) > 200 else text,
            "skills": skills,
            "experience": [],
            "education": [],
            "certifications": [],
            "languages": [],
            "total_experience_years": None
        }
    
    def extract_skills(self, resume_text: str) -> List[str]:
        """Extract only skills from resume"""
        parsed_data = self._parse_with_llm(resume_text)
        return parsed_data.get('skills', [])
    
    def calculate_match_score(
        self,
        resume_data: Dict[str, Any],
        required_skills: List[str]
    ) -> float:
        """Calculate skill match score"""
        
        candidate_skills = [s.lower() for s in resume_data.get('skills', [])]
        required_skills_lower = [s.lower() for s in required_skills]
        
        if not required_skills_lower:
            return 0.0
        
        matching_skills = set(candidate_skills) & set(required_skills_lower)
        score = (len(matching_skills) / len(required_skills_lower)) * 100
        
        return round(score, 2)


# Global resume parser instance
resume_parser = ResumeParser()