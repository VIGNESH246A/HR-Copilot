"""
HR Copilot - Main Application Entry Point
"""
import os
import sys
import subprocess
from config import settings, validate_settings, create_directories


def setup_environment():
    """Setup application environment"""
    print("🚀 Starting HR Copilot...")
    print(f"Version: {settings.APP_VERSION}")
    print("-" * 50)
    
    # Create necessary directories
    create_directories()
    print("✓ Directories created")
    
    # Validate settings
    try:
        validate_settings()
        print("✓ Configuration validated")
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        print("\nPlease create a .env file with:")
        print("ANTHROPIC_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Initialize database
    from services.database_service import db_service
    print("✓ Database initialized")
    
    print("-" * 50)
    print("✅ HR Copilot is ready!\n")


def run_streamlit():
    """Run Streamlit UI"""
    setup_environment()
    
    print("🌐 Starting web interface...")
    print("📱 Open your browser at: http://localhost:8501")
    print("\nPress Ctrl+C to stop\n")
    
    # Set PYTHONPATH to include current directory
    import subprocess
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "ui/app.py"], env=env)


def run_cli():
    """Run CLI interface"""
    setup_environment()
    
    from agents.orchestrator import orchestrator
    from models.conversation import conversation_manager
    
    session_id = conversation_manager.create_session()
    
    print("💬 HR Copilot CLI")
    print("Type 'exit' to quit, 'help' for examples\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                show_help()
                continue
            
            # Process request
            response = orchestrator.process_request(user_input, session_id)
            
            print(f"\n🤖 Assistant: {response.message}\n")
            
            if response.suggestions:
                print("💡 Suggestions:")
                for suggestion in response.suggestions:
                    print(f"  - {suggestion}")
                print()
            
            if response.next_actions:
                print("✓ Next Actions:")
                for action in response.next_actions:
                    print(f"  - {action}")
                print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


def show_help():
    """Show CLI help"""
    print("""
📚 HR Copilot Examples:

JOB DESCRIPTIONS:
  - "Create a job description for a Senior Python Developer"
  - "I need to hire a Marketing Manager with 5+ years experience"

RESUME SCREENING:
  - "Screen this resume: /path/to/resume.pdf for job_id: job_123"
  - "Rank all candidates for job_id: job_123"

INTERVIEWS:
  - "Schedule an interview with candidate_id: cand_123 for next Monday"
  - "Show me upcoming interviews"
  - "Generate interview questions for Senior Developer position"

ANALYTICS:
  - "Show me hiring metrics"
  - "What's the average candidate match score?"

GENERAL:
  - Type 'exit' to quit
  - Type 'help' to see this message again
""")


def run_tests():
    """Run basic tests"""
    print("🧪 Running tests...\n")
    
    # Test configuration
    try:
        validate_settings()
        print("✓ Configuration test passed")
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False
    
    # Test LLM service
    try:
        from services.llm_service import llm_service
        response = llm_service.generate_response("Hello")
        print("✓ LLM service test passed")
    except Exception as e:
        print(f"❌ LLM service test failed: {str(e)}")
        return False
    
    # Test database
    try:
        from services.database_service import db_service
        analytics = db_service.get_analytics()
        print("✓ Database test passed")
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False
    
    print("\n✅ All tests passed!")
    return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HR Copilot - AI-powered hiring assistant')
    parser.add_argument(
        'mode',
        choices=['ui', 'cli', 'test'],
        default='ui',
        nargs='?',
        help='Run mode: ui (Streamlit), cli (Command Line), or test'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'ui':
        run_streamlit()
    elif args.mode == 'cli':
        run_cli()
    elif args.mode == 'test':
        run_tests()


if __name__ == "__main__":
    main()