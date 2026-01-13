"""
Gemini LLM Service Integration (Updated with Rate Limiting)
"""
import json
import time
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from config import settings


class LLMService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        # Configure Gemini with new API
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL
        self.temperature = settings.GEMINI_TEMPERATURE
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2  # Minimum 2 seconds between requests
        
        # Generation config
        self.generation_config = types.GenerateContentConfig(
            temperature=self.temperature,
            top_p=0.95,
            top_k=40,
            max_output_tokens=settings.GEMINI_MAX_TOKENS,
        )
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            print(f"⏳ Rate limiting: waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3
    ) -> str:
        """Generate response from Gemini with retry logic"""
        
        # Wait to respect rate limits
        self._wait_for_rate_limit()
        
        for attempt in range(max_retries):
            try:
                # Build complete prompt with system instructions
                full_prompt = ""
                
                if system_prompt:
                    full_prompt += f"System Instructions: {system_prompt}\n\n"
                
                # Add conversation history
                if conversation_history:
                    full_prompt += "Previous conversation:\n"
                    for msg in conversation_history[-5:]:  # Last 5 messages
                        role = msg.get('role', 'user')
                        content = msg.get('content', '')
                        full_prompt += f"{role.title()}: {content}\n"
                    full_prompt += "\n"
                
                full_prompt += f"User: {prompt}\n\nAssistant:"
                
                # Update generation config if custom values provided
                config = types.GenerateContentConfig(
                    temperature=temperature if temperature is not None else self.temperature,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=max_tokens if max_tokens is not None else settings.GEMINI_MAX_TOKENS,
                )
                
                # Generate response
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=config
                )
                
                return response.text
            
            except Exception as e:
                error_msg = str(e)
                
                # Handle rate limit errors
                if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                    # Extract retry delay if available
                    import re
                    retry_match = re.search(r'retry in (\d+\.?\d*)', error_msg)
                    if retry_match:
                        retry_seconds = float(retry_match.group(1))
                    else:
                        retry_seconds = 60  # Default to 60 seconds
                    
                    if attempt < max_retries - 1:
                        print(f"⚠️ Rate limit hit. Waiting {retry_seconds:.0f}s before retry...")
                        time.sleep(retry_seconds)
                        continue
                    else:
                        raise Exception(
                            f"Rate limit exceeded. Your Gemini API quota is exhausted. "
                            f"Please wait ~{retry_seconds:.0f}s or check your quota at: "
                            f"https://aistudio.google.com/app/apikey"
                        )
                
                # Handle other errors
                if attempt < max_retries - 1:
                    print(f"⚠️ Attempt {attempt + 1} failed. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                raise Exception(f"Error generating response: {error_msg}")
        
        raise Exception("Max retries exceeded")
    
    def generate_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON output"""
        
        schema_prompt = f"""
{prompt}

You MUST respond with ONLY valid JSON matching this exact schema:
{json.dumps(output_schema, indent=2)}

Important:
- Do not include markdown formatting or code blocks
- Do not include any explanation or text outside the JSON
- Ensure all required fields are present
- Use proper JSON syntax

Respond with JSON only:
"""
        
        response = self.generate_response(
            prompt=schema_prompt,
            system_prompt=system_prompt
        )
        
        # Clean response
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            raise Exception(f"Failed to parse JSON response: {str(e)}\nResponse: {response[:500]}")
    
    def analyze_intent(self, user_message: str) -> Dict[str, Any]:
        """Analyze user intent"""
        
        schema = {
            "intent": "string (job_description|resume_screening|interview_scheduling|email|analytics|general)",
            "confidence": "float (0-1)",
            "entities": {
                "position": "string or null",
                "candidate_name": "string or null",
                "date": "string or null"
            },
            "requires_clarification": "boolean",
            "clarification_questions": ["string"]
        }
        
        prompt = f"""
Analyze this HR-related user message and determine the intent:

Message: "{user_message}"

Available task types:
- job_description: Create or modify job descriptions
- resume_screening: Screen and evaluate candidate resumes
- interview_scheduling: Schedule and manage interviews
- email: Send emails to candidates
- analytics: Generate hiring metrics and reports
- general: General conversation or unclear intent

Identify:
1. Primary intent (choose from the types above)
2. Confidence level (0.0 to 1.0)
3. Key entities mentioned (position, candidate name, dates)
4. Whether clarification is needed
5. What questions to ask if clarification needed
"""
        
        return self.generate_structured_output(
            prompt=prompt,
            output_schema=schema,
            system_prompt="You are an intent analyzer for an HR system."
        )
    
    def extract_job_requirements(self, description: str) -> Dict[str, Any]:
        """Extract structured job requirements from text"""
        
        schema = {
            "position": "string",
            "department": "string or null",
            "experience_years": "integer or null",
            "required_skills": ["string"],
            "preferred_skills": ["string"],
            "education": "string or null",
            "location": "string or null",
            "employment_type": "string",
            "salary_range": {"min": "integer or null", "max": "integer or null"}
        }
        
        prompt = f"""
Extract structured job requirements from this description:

{description}

Identify all relevant information about the position including:
- Job title/position
- Department (if mentioned)
- Years of experience required
- Required skills (must-have)
- Preferred skills (nice-to-have)
- Education requirements
- Work location
- Employment type (full-time, part-time, contract, etc.)
- Salary range if mentioned
"""
        
        return self.generate_structured_output(
            prompt=prompt,
            output_schema=schema
        )
    
    def summarize_resume(self, resume_text: str) -> str:
        """Summarize resume content"""
        
        prompt = f"""
Provide a concise 2-3 sentence professional summary of this resume highlighting:
- Key skills and expertise
- Years of experience
- Notable achievements or strengths

Resume:
{resume_text[:3000]}
"""
        
        return self.generate_response(prompt)
    
    def compare_candidate_to_job(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare candidate against job requirements"""
        
        schema = {
            "match_score": "float (0-100)",
            "matching_skills": ["string"],
            "missing_skills": ["string"],
            "experience_match": "boolean",
            "education_match": "boolean",
            "summary": "string",
            "recommendation": "string (strong_match|good_match|potential_match|not_recommended)",
            "strengths": ["string"],
            "concerns": ["string"]
        }
        
        prompt = f"""
Evaluate this candidate against the job requirements:

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

CANDIDATE PROFILE:
{json.dumps(resume_data, indent=2)}

Provide a detailed matching analysis:
1. Calculate match score (0-100) based on skills, experience, and qualifications
2. List matching skills (skills candidate has that job requires)
3. List missing skills (required skills candidate doesn't have)
4. Evaluate experience match (does candidate have required years?)
5. Evaluate education match
6. Write a 2-3 sentence summary
7. Provide recommendation (strong_match if 80%+, good_match if 60-80%, potential_match if 40-60%, not_recommended if <40%)
8. List 3-5 key strengths
9. List 2-3 concerns or gaps
"""
        
        return self.generate_structured_output(
            prompt=prompt,
            output_schema=schema,
            system_prompt="You are an expert HR recruiter evaluating candidate-job fit."
        )


# Global LLM service instance
llm_service = LLMService()