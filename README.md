# Dime - AI-Powered Content Creation Agent

**AI-powered content creation system for Acts of Defiance**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Google ADK](https://img.shields.io/badge/Google_ADK-1.0+-orange.svg)](https://ai.google.dev/adk)

Dime is a sophisticated multi-agent content creation system designed for Acts of Defiance, specializing in generating high-quality articles about political liberation movements and historical analysis.

## 📋 Current Status

**✅ Phase 0: Foundation Complete (Issues #1-4)**
- ✅ **CLI Interface**: Working `health` and `start` commands
- ✅ **ADK Web Interface**: Functional web interface at http://localhost:8000
- ✅ **Agent System**: Basic content creation agents with research and writing tools
- ✅ **Configuration**: Simplified case-sensitive environment variable management
- ✅ **Testing Framework**: pytest with 93% code coverage (20 tests passing)
- ✅ **Code Quality**: PEP 8 compliant, ruff linting and formatting

**📋 Phase 1: Planned (Not Yet Implemented)**
- Enhanced agent tools and sophisticated workflows
- Database (PostgreSQL) and Redis integration
- Full approval workflow interface
- Production monitoring and observability

## ✨ Features

### 🤖 Multi-Agent System (Phase 0: Basic Implementation)
**Currently Implemented:**
- **Research Agent**: Content research and source gathering
- **Writer Agent**: Article creation from research
- **Root Agent**: Coordinates research and writing workflows
- **Interactive ADK Web Interface**: Agent conversations and debugging tools

**Planned for Phase 1:**
- 7-stage content processing pipeline
- Human approval workflow with quality gates
- Intelligent fact-checking with 3-dimensional scoring
- Automated graphics generation with human selection

### 🎯 Content Focus
- **Political liberation movements**: Historical and contemporary analysis
- **Target audience**: Educated 25-40 year olds interested in social justice topics  
- **Quality standards**: Academic-level research with accessible writing style
- **Source verification**: Rigorous fact-checking with comprehensive citation tracking

### 🛠️ Technical Architecture
**Phase 0 Implementation:**
- **Local-first development**: Runs entirely on your machine
- **Google ADK integration**: Uses ADK's `get_fast_api_app()` for agent orchestration
- **FastAPI backend**: Lightweight web framework with ADK integration
- **Configuration management**: Pydantic Settings with environment variables

**Planned Enhancements:**
- Web dashboard for monitoring and approval workflow
- Database (PostgreSQL) for persistence
- Redis for caching and task queues
- Cost-optimized design (targeting $50/month budget)

## 🚀 Quick Start

### Prerequisites
- Python 3.13 or higher
- Google ADK API key (get from [Google AI Studio](https://aistudio.google.com/))
- 2GB+ RAM recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/ActsOfDefiance/dime.git
cd dime

# Set up Python environment
uv sync

# Configure environment variables
# Create a .envrc file with required variables:
# - DATABASE_URL (PostgreSQL connection string)
# - GOOGLE_ADK_PROJECT_ID (your Google Cloud project ID)
# - GOOGLE_ADK_API_KEY (your API key)
# - AUTH_* variables (for production only)

# For development, you can use a minimal .envrc:
cat > .envrc << 'EOF'
export DATABASE_URL="postgresql://user:pass@localhost/dime"
export GOOGLE_ADK_PROJECT_ID="your-project-id"
export GOOGLE_ADK_API_KEY="your-api-key"
export AUTH_GOOGLE_OAUTH_CLIENT_ID="placeholder"
export AUTH_GOOGLE_OAUTH_CLIENT_SECRET="placeholder"
export AUTH_JWT_SECRET_KEY="dev-secret-key-change-in-production"
EOF

# Load environment (if using direnv, or source manually)
direnv allow  # or: source .envrc

# Health check - verify configuration
uv run python -m dime health

# Start the ADK web interface
uv run python -m dime start
```

### First Interaction

```bash
# Check system status
uv run python -m dime health

# Start the web interface (runs on http://localhost:8000)
uv run python -m dime start

# Custom host/port
uv run python -m dime start --host 127.0.0.1 --port 3000
```

**Available Interfaces:**
- **Main ADK Web UI**: http://localhost:8000/ - Interactive agent conversations
- **Developer Tools**: http://localhost:8000/dev-ui/ - ADK debugging interface

**What You Can Do:**
- Start conversations with the dime_agent
- Test research and writing workflows
- Inspect agent behavior and tool execution
- Debug agent configurations

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_config.py
```

## 📋 Content Workflow

### Phase 0: Current Implementation
**Basic Agent Interactions:**
- Interactive conversations with research and writer agents
- Manual topic input through ADK web interface
- Basic research and writing workflow coordination
- Agent debugging and tool inspection

### Planned 7-Stage Pipeline (Phase 1+)

**Stage 1: Topic Selection (Human)**
- Manual curation of topics based on historical events and mission alignment

**Stage 2: Research Agent**
- Automated research using Google Gemini models
- Source gathering and preliminary analysis
- Citation collection and organization

**Stage 3: Fact Checker Agent (Planned)**
- Credibility scoring (1-10 scale) for source reliability
- Bias analysis for political lean and objectivity
- Claim verification against authoritative sources
- Quality gate for articles scoring <5 average

**Stage 4: Writer Agent (Enhanced)**
- Casual, hip, intelligent tone
- 5-10 paragraphs per article
- High-credibility source prioritization
- Citations referencing research footnotes

**Stage 5: Editor Agent (Planned)**
- Style consistency and voice maintenance
- Fact validation and citation double-checking
- Readability optimization for target audience
- Citation formatting standardization

**Stage 6: Graphics Agent (Planned)**
- AI-generated header images and thumbnails
- Multiple option presentation for human selection
- Visual identity consistency
- Accessibility with alt text generation

**Stage 7: Assembly Agent (Planned)**
- Final markdown document compilation
- Automated Git repository commits
- Template-based structure
- Metadata inclusion (scores, processing history)

## 🛡️ Human Oversight (Planned for Phase 1)

**Approval Workflow:**
- Web dashboard with progress indicators
- Real-time updates via WebSocket/SSE
- Approval actions: Accept, reject, edit, feedback
- Quality tracking and performance metrics

**Review Information:**
- Complete processing history
- Confidence scores and validation metrics
- Processing time and retry counts
- Audit trail for all approvals

## 💰 Cost Optimization

### Budget-Conscious Design
- **$50/month target**: Primarily for Google ADK/Gemini API calls
- **Local development**: No cloud infrastructure costs initially
- **Aggressive caching**: Reduces redundant API calls
- **Model optimization**: Right-sized models for each task

### Volume Expectations
- **Processing capacity**: 1-10 articles per day
- **Processing time**: <1 hour per article end-to-end
- **Fail-fast approach**: Quick error detection and human escalation

## 📊 Performance Metrics

### Quality Indicators
- **Fact-check scores**: Average credibility, bias, and verification ratings
- **Approval rates**: Human acceptance rate by agent and overall
- **Processing efficiency**: Time per stage and total article completion
- **Error rates**: Failed processing attempts and recovery success

### System Health  
- **Agent performance**: Success rates, processing times, retry frequency
- **Cost tracking**: Daily/monthly API usage and spend analysis
- **User engagement**: Approval workflow usage and feedback quality

## 🏗️ Architecture

### Current Technology Stack (Phase 0)
- **Backend**: FastAPI 0.104+ with Python 3.13+
- **AI Framework**: Google ADK 1.0+ (Agent Development Kit)
- **Configuration**: Pydantic Settings with environment variables
- **Testing**: pytest 8.0+ with pytest-cov for coverage
- **Code Quality**: ruff 0.8+ for linting and formatting
- **Package Management**: uv for Python dependencies
- **Web Server**: uvicorn ASGI server

### Planned Infrastructure (Phase 1+)
- **Database**: PostgreSQL for persistence
- **Caching**: Redis for performance and task queues
- **Frontend**: Web dashboard for approval workflows
- **Authentication**: OAuth 2.0 with Google login
- **Monitoring**: Logfire for observability

### Development Approach
- **Local-first**: Full development environment on local machine
- **Cloud-ready**: Architecture prepared for Google Cloud deployment
- **Test-driven**: 90%+ test coverage requirement
- **Quality-focused**: PEP 8 compliance and comprehensive testing

## 📚 Documentation

### For Developers
- **[CLAUDE.md](CLAUDE.md)**: AI-assisted development guide for Claude Code
- **[Project Structure](docs/development/project-structure.md)**: Current codebase organization
- **[Implementation Plans](docs/development/implementation_plans/)**: Detailed plans for Issues #2 and #4
- **[Technical Requirements](docs/development/technical-requirements.md)**: Complete system specifications
- **[Agent Prompts](docs/technical/agent-prompts.md)**: Current agent instruction specifications

### Planning Documentation
- **[Product Discovery](docs/development/product-discovery-session.md)**: Discovery session results
- **[Implementation Plan](docs/development/implementation-plan.md)**: 16-week development timeline
- **[Roadmap](docs/development/roadmap.md)**: Development phases and milestones
- **[Requirements Analysis](docs/development/requirements-analysis.md)**: Stakeholder needs

### Technical Documentation
- **[API Reference](docs/technical/api-reference.md)**: ADK API and endpoint documentation
- **[Architecture](docs/technical/architecture.md)**: System architecture overview
- **[Settings Usage](docs/technical/settings-usage-examples.md)**: Configuration examples

### GitHub Issues
- **[GitHub Issues Directory](docs/github_issues/)**: Detailed issue specifications for all project issues

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'feat: add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Quality Standards
- **Formatting**: `ruff format` for PEP 8 compliance
- **Linting**: `ruff check` with automatic fixes
- **Testing**: 90%+ test coverage required (currently 93%)
- **Documentation**: Comprehensive docstrings and API docs
- **Commit Policy**: 100% test pass rate before committing

### Getting Started with Development
```bash
# Set up development environment
uv sync

# Run quality checks
uv run ruff format .     # Auto-format code
uv run ruff check .      # Lint code
uv run ruff check --fix .  # Auto-fix linting issues

# Run tests
uv run pytest            # Run all tests
uv run pytest --cov      # Run with coverage
uv run pytest -v         # Verbose output
```

### Development Commands
```bash
# Application commands
uv run python -m dime health         # Check configuration
uv run python -m dime start          # Start web server
uv run python -m dime start --port 3000  # Custom port

# Testing commands
uv run pytest                        # Run all tests
uv run pytest tests/test_config.py   # Run specific test
uv run pytest --cov --cov-report=html  # Coverage report

# Code quality
uv run ruff format .                 # Format all code
uv run ruff check .                  # Check for issues
uv run ruff check --fix .           # Auto-fix issues
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Comprehensive guides in the `docs/` directory
- **Issues**: Report bugs and request features via GitHub Issues
- **CLAUDE.md**: Development guide for AI-assisted development

### Development Support
- **Setup Guide**: See Quick Start section above for installation
- **Architecture Questions**: Review [Technical Requirements](docs/development/technical-requirements.md)
- **API Integration**: Check [API Reference](docs/technical/api-reference.md)
- **Configuration**: See [Settings Usage Examples](docs/technical/settings-usage-examples.md)

## 🎯 Mission

Dime empowers Acts of Defiance to create high-quality, well-researched content about political liberation movements and social justice topics. By combining AI automation with human oversight, we maintain academic rigor while making complex historical topics accessible to a broader audience.

**Focus areas:**
- Historical liberation movements and their contemporary relevance
- Political analysis from a progressive perspective  
- Educational content that bridges academic research and public understanding
- Source-verified information with transparent fact-checking

---

**Built with ❤️ for social justice and historical education**