"""
Basic usage examples for HR Copilot
"""
import sys
sys.path.append('..')

from agents.orchestrator import orchestrator
from models.conversation import conversation_manager
from config import validate_settings


def example_create_job_description():
    """Example: Create a job description"""
    print("\n" + "="*50)
    print("Example 1: Creating Job Description")
    print("="*50)
    
    session_id = conversation_manager.create_session()
    
    request = """
    I need to hire a Senior Backend Engineer with:
    - 5+ years of Python experience
    - Strong knowledge of Django and FastAPI
    - Experience with PostgreSQL and Redis
    - AWS/Docker experience preferred
    - Remote position, salary range $120k-$150k
    """
    
    response = orchestrator.process_request(request, session_id)
    
    print(f"\n✅ Response: {response.message}")
    if response.data:
        print(f"\n📄 Job ID: {response.data.get('job_id')}")
    if response.next_actions:
        print("\n📌 Next Actions:")
        for action in response.next_actions:
            print(f"  - {action}")


def example_screen_resume():
    """Example: Screen a candidate's resume"""
    print("\n" + "="*50)
    print("Example 2: Screening Resume")
    print("="*50)
    
    session_id = conversation_manager.create_session()
    
    # First, we need a job
    print("\n1. Creating job first...")
    job_request = "Create a job for Senior Python Developer with 5 years experience"
    response1 = orchestrator.process_request(job_request, session_id)
    print(f"✅ {response1.message}")
    
    # Then screen resume
    print("\n2. Screening resume...")
    # Note: In real usage, you'd have an actual resume file
    screen_request = """
    Screen a candidate with these qualifications:
    - 7 years Python experience
    - Expert in Django, Flask
    - Strong PostgreSQL and MongoDB
    - AWS and Docker certified
    - Bachelor's in Computer Science
    """
    
    response2 = orchestrator.process_request(screen_request, session_id)
    print(f"\n✅ {response2.message}")


def example_schedule_interview():
    """Example: Schedule an interview"""
    print("\n" + "="*50)
    print("Example 3: Scheduling Interview")
    print("="*50)
    
    session_id = conversation_manager.create_session()
    
    request = """
    Schedule an interview:
    - Position: Senior Python Developer
    - Candidate: John Doe (john@email.com)
    - Date: Next Monday at 2 PM
    - Type: Technical Interview
    - Interviewer: Sarah Smith
    """
    
    response = orchestrator.process_request(request, session_id)
    
    print(f"\n✅ Response: {response.message}")
    if response.next_actions:
        print("\n📌 Next Actions:")
        for action in response.next_actions:
            print(f"  - {action}")


def example_conversational_flow():
    """Example: Multi-turn conversation"""
    print("\n" + "="*50)
    print("Example 4: Conversational Flow")
    print("="*50)
    
    session_id = conversation_manager.create_session()
    
    conversations = [
        "I want to hire a data scientist",
        "They should have 3+ years experience with Python and ML",
        "Also need SQL and visualization skills",
        "Create the job description"
    ]
    
    for i, message in enumerate(conversations, 1):
        print(f"\n{i}. User: {message}")
        response = orchestrator.process_request(message, session_id)
        print(f"   Assistant: {response.message[:200]}...")


def example_get_analytics():
    """Example: Get hiring analytics"""
    print("\n" + "="*50)
    print("Example 5: Hiring Analytics")
    print("="*50)
    
    from services.database_service import db_service
    
    analytics = db_service.get_analytics()
    
    print("\n📊 Current Hiring Metrics:")
    print(f"  Total Jobs: {analytics['total_jobs']}")
    print(f"  Active Jobs: {analytics['active_jobs']}")
    print(f"  Total Candidates: {analytics['total_candidates']}")
    print(f"  Average Match Score: {analytics['average_match_score']}%")
    print(f"  Interviews Scheduled: {analytics['interviews_scheduled']}")
    
    if analytics['candidates_by_status']:
        print("\n  Candidates by Status:")
        for status, count in analytics['candidates_by_status'].items():
            print(f"    - {status}: {count}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("HR COPILOT - USAGE EXAMPLES")
    print("="*60)
    
    # Validate configuration
    try:
        validate_settings()
        print("✅ Configuration validated")
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        print("\nPlease set ANTHROPIC_API_KEY in .env file")
        return
    
    # Run examples
    try:
        example_create_job_description()
        example_screen_resume()
        example_schedule_interview()
        example_conversational_flow()
        example_get_analytics()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()