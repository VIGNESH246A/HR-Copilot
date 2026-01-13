# 👔 HR Copilot - AI-Powered Hiring Assistant

An intelligent HR assistant powered by Google Gemini AI that automates and streamlines your entire hiring workflow.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hr-copilot-2egdggstbugtejcanhzcnu.streamlit.app/)

## 🌟 Features

### Core Capabilities
- **🤖 Natural Language Interface**: Chat with the AI to manage all hiring tasks
- **📝 Job Description Generation**: Create professional JDs from simple requirements
- **📄 Resume Screening**: Automatically parse and rank candidates
- **📅 Interview Scheduling**: Schedule and manage interviews with automated emails
- **📊 Analytics Dashboard**: Track hiring metrics and pipeline health
- **✉️ Email Automation**: Send templated emails to candidates
- **💡 Smart Recommendations**: Get AI-powered hiring suggestions

### Agentic Workflows
- **Task Decomposition**: Breaks complex requests into actionable steps
- **Multi-Agent Orchestration**: Routes tasks to specialized agents
- **Context Awareness**: Maintains conversation memory across sessions
- **Intelligent Routing**: Automatically determines the best agent for each task

## 🏗️ Architecture

```
User Request → Orchestrator → Task Decomposer → Specialized Agents → Tools → Response
                    ↓
              Memory Service (Context Management)
                    ↓
              Database (Persistent Storage)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/hr-copilot.git
cd hr-copilot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Option A: Using .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Option B: Using Streamlit secrets (recommended for deployment)
# Create .streamlit/secrets.toml and add your GEMINI_API_KEY
```

4. **Run the application**

**Option A: Web Interface (Recommended)**
```bash
python main.py ui
```
Then open http://localhost:8501 in your browser

**Option B: Command Line Interface**
```bash
python main.py cli
```

**Option C: Run tests**
```bash
python main.py test
```

## 📖 Usage Examples

### Creating Job Descriptions
```
User: "I need to hire a Senior Python Developer with 5+ years experience in Django and FastAPI"

HR Copilot: ✅ Job description created for Senior Python Developer

Next Actions:
- Review and edit the job description
- Post to job boards
- Start screening candidates
```

### Screening Resumes
```
User: "Screen resume at ./resumes/john_doe.pdf for job_id: job_123"

HR Copilot: ✅ Screened candidate: John Doe (Match: 85%)

Strengths:
- 7 years Python experience
- Strong Django and FastAPI background
- Excellent problem-solving skills

Next Actions:
- Schedule interview immediately
- Send interview invitation email
```

### Scheduling Interviews
```
User: "Schedule interview with candidate cand_456 for next Monday at 2 PM"

HR Copilot: ✅ Interview scheduled with Jane Smith on 2026-01-20 at 14:00

Next Actions:
- Send interview invitation email
- Prepare interview questions
- Share candidate profile with interviewer
```

## 📁 Project Structure

```
hr-copilot/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
│
├── models/
│   ├── schemas.py        # Data models
│   └── conversation.py   # Conversation management
│
├── agents/
│   ├── orchestrator.py           # Main orchestrator
│   ├── task_decomposer.py        # Task decomposition
│   ├── jd_generator_agent.py     # Job description agent
│   ├── screening_agent.py        # Resume screening agent
│   └── interview_agent.py        # Interview management agent
│
├── tools/
│   ├── resume_parser.py          # Resume parsing
│   ├── email_sender.py           # Email automation
│   ├── calendar_manager.py       # Calendar integration
│   └── document_generator.py     # Document generation
│
├── services/
│   ├── llm_service.py            # Gemini API integration
│   ├── memory_service.py         # Memory management
│   ├── database_service.py       # Database operations
│   └── vector_store.py           # Semantic search
│
├── ui/
│   └── app.py                    # Streamlit interface
│
└── data/
    ├── hr_copilot.db             # SQLite database
    ├── resumes/                  # Uploaded resumes
    └── templates/                # Document templates
```

## 🔧 Configuration

### Required Settings
```env
GEMINI_API_KEY=your_api_key_here
```

### Optional Settings
```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_password
FROM_EMAIL=hr@yourcompany.com

# Database (default is SQLite)
DATABASE_URL=sqlite:///./data/hr_copilot.db

# Gemini Model (optional)
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_MAX_TOKENS=8000
GEMINI_TEMPERATURE=0.7

# ATS Integration
ATS_API_KEY=your_ats_api_key
ATS_API_URL=https://api.ats-provider.com
```

## 🤖 Agents

### 1. Orchestrator Agent
- Routes requests to appropriate agents
- Manages conversation context
- Coordinates multi-step workflows

### 2. Task Decomposer Agent
- Analyzes complex requests
- Breaks down into actionable tasks
- Identifies dependencies

### 3. Job Description Generator Agent
- Creates professional job descriptions
- Extracts requirements from natural language
- Optimizes for SEO

### 4. Screening Agent
- Parses resumes (PDF, DOCX)
- Matches candidates to job requirements
- Generates screening reports
- Ranks candidates

### 5. Interview Agent
- Schedules interviews
- Sends invitation emails
- Generates interview questions
- Manages interview calendar

### 6. Analytics Agent
- Generates hiring metrics
- Tracks pipeline performance
- Provides insights and recommendations

## 🛠️ Tools

### Resume Parser
- Supports PDF, DOCX, TXT formats
- Extracts structured information
- Uses Gemini for intelligent parsing

### Email Sender
- Automated email templates
- Customizable messages
- SMTP integration

### Document Generator
- Job descriptions
- Offer letters
- Interview questions
- Screening reports

### Calendar Manager
- Interview scheduling
- Availability tracking
- Meeting link generation

## 📊 Database Schema

### Jobs Table
- Job postings and descriptions
- Requirements and qualifications
- Status tracking

### Candidates Table
- Candidate profiles
- Resume data
- Match scores
- Application status

### Interviews Table
- Interview schedules
- Interviewer assignments
- Meeting links
- Notes and feedback

## 🔐 Security

- API keys stored in environment variables or Streamlit secrets
- No credentials in code
- SQLite database for local storage
- Optional PostgreSQL for production
- `.gitignore` configured to exclude sensitive files

## 💡 Gemini AI Features

This application leverages Google Gemini's powerful capabilities:
- **Natural Language Understanding**: Understands complex HR queries
- **Structured Output**: Generates JSON responses for data processing
- **Context Awareness**: Maintains conversation history
- **Multi-turn Conversations**: Handles follow-up questions
- **Rate Limiting**: Built-in retry logic for API quotas

### Available Models
- `gemini-2.0-flash-exp` - Latest, fastest (recommended)
- `gemini-1.5-flash` - Fast and efficient
- `gemini-1.5-pro-002` - Best quality

## 🚧 Roadmap

- [ ] Integration with job boards (LinkedIn, Indeed)
- [ ] Video interview scheduling (Zoom, Google Meet)
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Slack/Teams integration
- [ ] Calendar sync (Google Calendar, Outlook)
- [ ] Automated reference checking
- [ ] Voice interface integration
- [ ] Real-time collaboration features

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Google Gemini AI](https://ai.google.dev/)
- UI powered by [Streamlit](https://streamlit.io/)
- Resume parsing with PyPDF2 and python-docx
- Database management with SQLite/SQLAlchemy

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: vignesh246v@gmail.com
- Check [Gemini API Documentation](https://ai.google.dev/docs)

## ⚠️ Important Notes

### API Quotas
Google Gemini Free Tier limits:
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

The application includes automatic rate limiting and retry logic to handle these limits gracefully.

### Getting Started with Gemini
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file or `.streamlit/secrets.toml`
4. Start using HR Copilot!

---

**Made with ❤️ for HR professionals**

*Powered by Google Gemini AI*
