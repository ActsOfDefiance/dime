# Dime - AI-Powered Content Creation Agent

**AI-powered content creation system for Acts of Defiance**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Google ADK](https://img.shields.io/badge/Google_ADK-1.0+-orange.svg)](https://ai.google.dev/adk)

Dime is a sophisticated multi-agent content creation system designed for Acts of Defiance, specializing in generating high-quality articles about political liberation movements and historical analysis.

## ✨ Features

### 🤖 Multi-Agent Pipeline
- **7-stage content processing**: Topic → Research → Fact Check → Writer → Editor → Graphics → Assembly
- **Human approval workflow**: Quality gates at each stage with accept/reject/edit options
- **Intelligent fact-checking**: 3-dimensional scoring for credibility, bias, and verification
- **Automated graphics generation**: AI-generated images with human selection and refinement

### 🎯 Content Focus
- **Political liberation movements**: Historical and contemporary analysis
- **Target audience**: Educated 25-40 year olds interested in social justice topics  
- **Quality standards**: Academic-level research with accessible writing style
- **Source verification**: Rigorous fact-checking with comprehensive citation tracking

### 🛠️ Technical Architecture
- **Local-first development**: Run entirely on your machine initially
- **Google ADK integration**: Leverages Google's Agent Development Kit
- **Web dashboard**: Real-time monitoring and approval interface
- **Cost-optimized**: Designed for $50/month budget (primarily AI API costs)

## 🚀 Quick Start

### Prerequisites
- Python 3.13 or higher
- Docker Desktop
- Google Cloud account with ADK access
- 8GB+ RAM recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/ActsOfDefiance/dime.git
cd dime

# Set up Python environment
uv sync --dev

# Copy environment configuration
cp .env.example .env
# Edit .env with your configuration

# Start development services
docker-compose up -d postgres redis

# Initialize database
uv run alembic upgrade head

# Run the application
uv run uvicorn dime.main:app --reload --host 0.0.0.0 --port 8000
```

### First Article

```bash
# Create a new article
uv run dime create-article \"Civil Rights Movement Impact\"

# Import research (markdown with footnotes)
uv run dime import-research --file research.md --article-id <uuid>

# Process through agents
uv run dime process --agent fact-checker --article-id <uuid>
uv run dime process --agent writer --article-id <uuid>
uv run dime process --agent editor --article-id <uuid>

# Check status
uv run dime status --article-id <uuid>
```

Access the web dashboard at http://localhost:8000 for the full approval workflow interface.

## 📋 Content Workflow

### 1. Topic Selection (Human)
Manual curation of topics based on historical events, current relevance, and Acts of Defiance mission.

### 2. Research (Human → Future AI)
- **Current**: Human-created markdown with footnote citations
- **Future**: Google Gemini Deep Research API integration
- **Input methods**: Direct paste, Google Docs import, file system pickup

### 3. Fact Checker Agent
- **Credibility scoring**: Source reliability assessment (1-10 scale)
- **Bias analysis**: Political lean and objectivity evaluation  
- **Claim verification**: Cross-reference with authoritative sources
- **Quality gate**: Articles scoring <5 average flagged for human review

### 4. Writer Agent
- **Style**: Casual, hip, intelligent tone
- **Length**: 5-10 paragraphs per article
- **Source prioritization**: Emphasizes high-credibility sources
- **Citations**: References back to research footnotes

### 5. Editor Agent  
- **Style consistency**: Maintains voice and tone standards
- **Fact validation**: Double-checks citations and claims
- **Readability**: Optimizes for target audience (high school to college level)
- **Citation formatting**: Standardizes reference style

### 6. Graphics Agent
- **Image generation**: Creates header images and thumbnails
- **Human interaction**: Presents multiple options for selection
- **Style consistency**: Maintains visual identity across content
- **Accessibility**: Generates alt text for all images

### 7. Assembly Agent
- **Document compilation**: Creates final markdown with frontmatter
- **Git integration**: Automated commits to repository
- **Template-based**: Consistent structure across all articles
- **Metadata inclusion**: Research, fact-check scores, and processing history

## 🛡️ Human Oversight

### Approval Workflow
- **Web dashboard**: Visual interface with progress indicators  
- **Real-time updates**: WebSocket and Server-Sent Events
- **Approval actions**: Accept, reject, edit prompts, provide feedback
- **Quality tracking**: Performance metrics and success rates

### Review Information
- **Complete history**: All agent outputs and previous processing steps
- **Confidence scores**: Detailed metrics for each validation dimension  
- **Processing metrics**: Time spent, retry counts, performance data
- **Audit trail**: Who approved what, when, and why

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

### Technology Stack
- **Backend**: FastAPI with Python 3.13+
- **AI Framework**: Google ADK (Agent Development Kit)
- **Database**: PostgreSQL for persistence, Redis for caching
- **Frontend**: Web dashboard with HTML/CSS/JavaScript
- **Authentication**: OAuth 2.0 with Google login
- **Package Management**: uv for Python dependencies

### Development Approach
- **Local-first**: Full development environment on local machine
- **Cloud-ready**: Prepared for future Google Cloud deployment  
- **Modular design**: Clear separation between agents, services, and API layers
- **Quality gates**: Comprehensive testing and validation at each stage

## 📚 Documentation

### For Developers
- **[Technical Requirements](docs/development/technical-requirements.md)**: Complete system specifications
- **[Implementation Plan](docs/development/implementation-plan.md)**: 16-week development timeline
- **[Project Structure](docs/development/project-structure.md)**: Codebase organization guide
- **[Agent Prompts](docs/technical/agent-prompts.md)**: AI agent instruction specifications

### For Product Teams
- **[Product Discovery](docs/development/product-discovery-session.md)**: Complete discovery session results  
- **[Content Capabilities](docs/development/content-capabilities-specification.md)**: Content creation workflow specification
- **[Requirements Analysis](docs/development/requirements-analysis.md)**: Stakeholder needs and system requirements

### For Project Management
- **[GitHub Setup](docs/development/github-project-setup.md)**: Issue tracking and project board configuration
- **[Current State Analysis](docs/development/current-state-analysis.md)**: Gap analysis and recommendations

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'feat: add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Quality Standards
- **Formatting**: Black code formatter
- **Linting**: flake8 with strict rules  
- **Type checking**: mypy with comprehensive coverage
- **Testing**: 90%+ test coverage required
- **Documentation**: Comprehensive docstrings and API docs

### Getting Started with Development
```bash
# Set up development environment
uv sync --dev

# Install pre-commit hooks  
uv run pre-commit install

# Run quality checks
uv run black .
uv run flake8
uv run mypy dime/

# Run tests
uv run pytest --cov=dime
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Comprehensive guides in the `docs/` directory
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join conversations in GitHub Discussions

### Development Support
- **Local Setup**: See [Local Development Guide](docs/setup/local-development.md)
- **Architecture Questions**: Review [Technical Requirements](docs/development/technical-requirements.md)
- **API Integration**: Check [API Reference](docs/technical/api-reference.md)

## 🎯 Mission

Dime empowers Acts of Defiance to create high-quality, well-researched content about political liberation movements and social justice topics. By combining AI automation with human oversight, we maintain academic rigor while making complex historical topics accessible to a broader audience.

**Focus areas:**
- Historical liberation movements and their contemporary relevance
- Political analysis from a progressive perspective  
- Educational content that bridges academic research and public understanding
- Source-verified information with transparent fact-checking

---

**Built with ❤️ for social justice and historical education**