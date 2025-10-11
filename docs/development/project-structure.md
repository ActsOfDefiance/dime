# Dime Project Structure & Development Guide

**Version**: 2.0
**Date**: 2025-01-14
**Status**: Phase 0 Complete - Foundation Implemented

## Current Project Directory Structure

```
dime/
├── README.md                      # ✅ Project overview with current status
├── CLAUDE.md                      # ✅ Claude Code development guidelines
├── pyproject.toml                 # ✅ Python project configuration
├── uv.lock                        # ✅ Dependency lock file
├── .envrc                         # ✅ direnv configuration (contains secrets)
│
├── dime/                          # ✅ Main application package
│   ├── __init__.py                # ✅ Package initialization
│   ├── app.py                     # ✅ FastAPI application with ADK integration
│   ├── __main__.py                # ✅ CLI entry point (health, start commands)
│   └── config/                    # ✅ Configuration management
│       ├── __init__.py            # ✅ Configuration exports
│       └── settings.py            # ✅ Simplified case-sensitive Pydantic settings
│
├── agents/                        # ✅ ADK agent directory
│   └── dime_agent/                # ✅ Main content creation agent
│       ├── __init__.py            # ✅ Agent package
│       └── agent.py               # ✅ Research and writing agent implementation
│
├── publisher/                     # ✅ Legacy agent code (fixed)
│   ├── __init__.py                # ✅ Package init
│   └── agent.py                   # ✅ Fixed undefined references
│
├── docs/                          # ✅ Project documentation
│   ├── development/               # ✅ Development guides
│   │   ├── implementation_plans/  # ✅ Issue implementation plans
│   │   ├── project-structure.md   # ✅ This document
│   │   └── roadmap.md            # Development roadmap
│   └── github_issues/             # GitHub issue documentation
```

## ✅ Phase 0 Implementation Status

### Completed Components
- **CLI Interface**: Working `health` and `start` commands via `dime/__main__.py`
- **ADK Integration**: FastAPI application using `get_fast_api_app()` utility
- **Agent System**: Functional research and writing agents with ADK discovery
- **Configuration**: Simplified case-sensitive environment variable mapping
- **Code Quality**: All syntax errors fixed, proper ADK patterns implemented

### Key Architecture Decisions
1. **Simplified Configuration**: Single `DimeSettings` class with uppercase field names matching environment variables exactly
2. **ADK-First Approach**: Using Google ADK's `get_fast_api_app()` for automatic agent discovery and web interface
3. **Minimal CLI**: Simple health check and server start commands following the "start with simplest approach" principle
4. **Standard Project Layout**: Main package at root level, agents in dedicated directory for ADK discovery

### Development Commands

#### Running the Application
```bash
# Check system health
uv run python -m dime health

# Start ADK web interface
uv run python -m dime start

# Custom host/port
uv run python -m dime start --host 127.0.0.1 --port 3000
```

#### Available Interfaces
- **ADK Web UI**: http://localhost:8000/ (interactive agent conversations)
- **Developer Tools**: http://localhost:8000/dev-ui/ (ADK debugging interface)
- **Agent Discovery**: Automatic loading from `agents/` directory

### Configuration System
- **Environment Variables**: All settings via `.envrc` file with direnv
- **Case Sensitivity**: `case_sensitive=True` with exact field-to-env-var mapping
- **Auto-Discovery**: No complex prefixes or Field() mappings - simple and direct
- **Validation**: Built-in validation with descriptive error messages

### Next Phase Priorities
1. **Enhanced Agents**: More sophisticated research and writing tools
2. **Database Integration**: Full PostgreSQL and Redis integration
3. **Web Dashboard**: Human approval workflow interface
4. **Production Readiness**: Monitoring, observability, deployment

---

## 📋 Future Planned Structure (Phase 1+)

**Note**: The following directory structure represents the planned architecture for future phases. None of these components are currently implemented. This serves as a design reference for future development.

### Planned Application Structure
```
dime/
├── dime/                          # Main package expansion (planned)
│   ├── models/                    # Database models (planned)
│   │   ├── __init__.py
│   │   ├── article.py             # Article and content models
│   │   ├── user.py                # User and authentication models
│   │   └── content.py         # Content and media models
│       ├── services/              # Business logic services
│       │   ├── __init__.py
│       │   ├── article_service.py # Article workflow orchestration
│       │   ├── agent_service.py   # Agent processing coordination
│       │   ├── approval_service.py# Human approval workflow
│       │   ├── auth_service.py    # Authentication and authorization
│       │   └── notification_service.py # Notifications and alerts
│       ├── db/                    # Database utilities
│       │   ├── __init__.py
│       │   ├── connection.py      # Database connection management
│       │   ├── session.py         # Session management
│       │   └── migrations/        # Database migrations (Alembic)
│       ├── cache/                 # Redis caching utilities
│       │   ├── __init__.py
│       │   ├── client.py          # Redis client setup
│       │   └── strategies.py      # Caching strategies
│       ├── web/                   # Web interface
│       │   ├── static/            # Static files (CSS, JS, images)
│       │   │   ├── css/
│       │   │   ├── js/
│       │   │   └── images/
│       │   └── templates/         # HTML templates
│       │       ├── base.html
│       │       ├── dashboard.html
│       │       ├── article_detail.html
│       │       ├── approval_queue.html
│       │       └── login.html
│       └── cli/                   # Command-line interface
│           ├── __init__.py
│           ├── main.py            # CLI entry point
│           ├── articles.py        # Article management commands
│           ├── agents.py          # Agent processing commands
│           └── admin.py           # Administrative commands
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration and fixtures
│   ├── unit/                      # Unit tests
│   │   ├── test_agents.py         # Agent functionality tests
│   │   ├── test_services.py       # Service layer tests
│   │   ├── test_models.py         # Database model tests
│   │   └── test_api.py            # API endpoint tests
│   ├── integration/               # Integration tests
│   │   ├── test_workflow.py       # End-to-end workflow tests
│   │   ├── test_database.py       # Database integration tests
│   │   └── test_auth.py           # Authentication integration tests
│   └── e2e/                       # End-to-end tests (Playwright)
│       ├── test_dashboard.py      # Web interface tests
│       └── test_approval_flow.py  # Human approval workflow tests
│
├── docs/                          # Documentation
│   ├── README.md                  # Documentation index
│   ├── development/               # Development documentation
│   │   ├── product-discovery-session.md
│   │   ├── current-state-analysis.md
│   │   ├── requirements-analysis.md
│   │   ├── content-capabilities-specification.md
│   │   ├── technical-architecture-specification.md
│   │   ├── technical-requirements.md
│   │   ├── implementation-plan.md
│   │   ├── project-structure.md
│   │   └── github-project-setup.md
│   ├── technical/                 # Technical documentation
│   │   ├── README.md
│   │   ├── agent-prompts.md
│   │   ├── architecture.md
│   │   ├── api-reference.md
│   │   └── database-examples.md
│   ├── setup/                     # Setup and deployment guides
│   │   └── local-development.md
│   └── user/                      # User documentation
│       └── dashboard-guide.md
│
├── scripts/                       # Development and deployment scripts
│   ├── setup_dev.sh               # Development environment setup
│   ├── run_tests.sh              # Test execution script
│   ├── deploy.sh                 # Deployment script
│   └── backup_db.sh              # Database backup script
│
├── config/                        # Configuration files
│   ├── agents/                    # Agent configuration
│   │   ├── fact_checker.yml      # Fact checker agent config
│   │   ├── writer.yml             # Writer agent config
│   │   ├── editor.yml             # Editor agent config
│   │   ├── graphics.yml           # Graphics agent config
│   │   └── assembly.yml           # Assembly agent config
│   ├── docker/                    # Docker configuration
│   │   ├── Dockerfile             # Application Dockerfile
│   │   ├── nginx.conf             # Nginx configuration
│   │   └── postgres.conf          # PostgreSQL configuration
│   └── alembic.ini               # Database migration configuration
│
├── storage/                       # Local file storage
│   ├── research/                  # Research documents
│   ├── articles/                  # Generated articles
│   ├── graphics/                  # Generated images
│   └── exports/                   # Final assembled documents
│
└── .github/                       # GitHub configuration
    ├── workflows/                 # GitHub Actions
    │   ├── test.yml               # CI testing workflow
    │   ├── lint.yml               # Code quality checks
    │   └── deploy.yml             # Deployment workflow (future)
    ├── ISSUE_TEMPLATE/            # Issue templates
    │   ├── bug_report.md
    │   ├── feature_request.md
    │   └── epic.md
    └── pull_request_template.md   # PR template
```

## Module Dependencies

### Phase 0: Actual Dependencies (pyproject.toml)
```toml
[project]
name = "dime"
version = "0.1.0"
description = "AI-powered multi-agent content creation system for political liberation movement analysis"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "google-adk>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "ruff>=0.8.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=dime --cov=agents --cov-report=term-missing --cov-report=html"
```

### Planned Dependencies (Phase 1+)
The following dependencies will be added in future phases:
- **Database**: `sqlalchemy>=2.0.0`, `alembic>=1.12.0`, `psycopg2-binary>=2.9.7`
- **Caching**: `redis>=5.0.0`
- **Web Framework**: `fastapi>=0.104.0`, `uvicorn>=0.24.0` (currently using ADK's built-in FastAPI)
- **Authentication**: `authlib>=1.2.0`, `python-multipart>=0.0.6`
- **Monitoring**: `logfire[fastapi,sqlalchemy]>=0.20.0`
- **CLI**: `click>=8.1.0` (currently using argparse)
- **Testing**: `playwright>=1.39.0` (E2E tests), `pyright>=1.1.0` (type checking)

## Configuration Management

### Phase 0: Current Configuration
**Implementation**: Simplified Pydantic Settings with case-sensitive environment variable mapping
- All fields in `DimeSettings` map directly to uppercase environment variables
- Example: `DATABASE_URL` field → `DATABASE_URL` environment variable
- No complex prefixes, no Field() mappings for most fields
- Validation with descriptive error messages

**Configuration File**: `dime/config/settings.py`
- Single `DimeSettings` class with all configuration
- Case-sensitive field names matching environment variables exactly
- Automatic environment variable discovery via direnv (`.envrc`)

### Planned Environment Variables (Phase 1+)
```bash
# Database Configuration
DATABASE_URL=postgresql://dime:password@localhost:5432/dime_dev
DATABASE_POOL_SIZE=10
DATABASE_POOL_TIMEOUT=30

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# Google ADK Configuration
GOOGLE_ADK_PROJECT_ID=your-project-id
GOOGLE_ADK_LOCATION=us-central1
GOOGLE_API_KEY=your-api-key

# Authentication
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
JWT_SECRET_KEY=your-jwt-secret
SESSION_TIMEOUT=86400

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000

# Logfire Configuration
LOGFIRE_TOKEN=your-logfire-token
LOGFIRE_PROJECT_NAME=dime-development
LOGFIRE_ENVIRONMENT=development
LOGFIRE_SERVICE_NAME=dime-app

# Agent Configuration
AGENT_TIMEOUT_SECONDS=1800
AGENT_MAX_RETRIES=2
AGENT_DEFAULT_MODEL=gemini-2.5-flash

# File Storage
STORAGE_PATH=./storage
GRAPHICS_PATH=./storage/graphics
RESEARCH_PATH=./storage/research
```

### Planned Agent Configuration Files (Phase 1+)

**Note**: These configuration files do not currently exist. Agent configuration is currently embedded in Python code.

#### agents/fact_checker.yml (Planned)
```yaml
name: "fact_checker"
model: "gemini-2.5-pro"
temperature: 0.1
max_tokens: 4000
timeout_seconds: 600

instruction: |
  You are a rigorous fact-checker specializing in political and historical content 
  about liberation movements. Your job is to verify claims, assess source credibility, 
  and identify potential bias.

  For each claim in the content, provide:
  1. Credibility score (1-10): Assess the reliability of sources
  2. Bias score (1-10): Evaluate political bias and objectivity  
  3. Verification score (1-10): Cross-check claims against authoritative sources
  
  Provide detailed explanations for scores below 7.

scoring_weights:
  credibility: 0.4
  bias: 0.3
  verification: 0.3

quality_threshold: 5.0
```

## Development Workflow

### Phase 0: Current Development Setup
```bash
# 1. Clone repository
git clone https://github.com/ActsOfDefiance/dime.git
cd dime

# 2. Set up Python environment
uv sync

# 3. Configure environment variables
# Create .envrc with required variables (see Configuration Management section)
# Load environment
direnv allow  # or: source .envrc

# 4. Health check
uv run python -m dime health

# 5. Start ADK web interface
uv run python -m dime start
```

### Phase 0: Current Commands
```bash
# Application commands
uv run python -m dime health                 # System health check
uv run python -m dime start                  # Start web server (default host/port)
uv run python -m dime start --host 127.0.0.1 --port 3000  # Custom host/port

# Testing commands
uv run pytest                                # Run all tests
uv run pytest -v                            # Verbose output
uv run pytest --cov                         # With coverage
uv run pytest tests/test_config.py          # Specific test file
uv run pytest --cov --cov-report=html       # HTML coverage report

# Code quality
uv run ruff format .                         # Format code
uv run ruff check .                          # Lint code
uv run ruff check --fix .                   # Auto-fix linting issues
```

### Planned Commands (Phase 1+)
The following commands will be added in future phases:
```bash
# Database operations (planned)
uv run alembic revision --autogenerate -m "description"  # Create migration
uv run alembic upgrade head                   # Apply migrations
uv run alembic downgrade -1                   # Rollback migration

# Advanced testing (planned)
uv run pytest tests/unit/                    # Unit tests only
uv run pytest tests/integration/             # Integration tests
uv run playwright install                    # E2E test browsers
uv run pyright                               # Type checking

# Enhanced CLI (planned)
uv run python -m dime articles create        # Article management
uv run python -m dime agents list            # Agent management
```

### Git Workflow
```bash
# Feature development
git checkout -b feature/agent-improvements
git add .
git commit -m "feat: improve fact-checking accuracy"
git push origin feature/agent-improvements

# Pull request process
# 1. Create PR on GitHub
# 2. Automated testing runs
# 3. Code review required
# 4. Merge to main after approval
```

## Planned Architecture Patterns (Phase 1+)

**Note**: These design patterns are planned for future implementation. Current implementation uses simpler direct agent instantiation.

### Planned Agent Pattern
```python
# Base agent interface
class BaseAgent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.adk_agent = LlmAgent(
            model=config.model,
            name=config.name,
            instruction=config.instruction
        )
    
    @abstractmethod
    async def process(self, input_data: dict) -> AgentResult:
        pass
    
    async def _retry_with_backoff(self, operation, max_retries=2):
        # Standardized retry logic
        pass
```

### Service Pattern  
```python
# Business logic services
class ArticleService:
    def __init__(self, db: DatabaseService, cache: CacheService):
        self.db = db
        self.cache = cache
    
    async def create_article(self, topic: str) -> Article:
        # Business logic for article creation
        pass
    
    async def process_with_agent(self, article_id: str, agent_name: str) -> ProcessingResult:
        # Agent processing coordination
        pass
```

### Repository Pattern
```python
# Data access layer
class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, article: Article) -> Article:
        self.session.add(article)
        await self.session.commit()
        return article
    
    async def get_by_id(self, article_id: str) -> Optional[Article]:
        return await self.session.get(Article, article_id)
```

## Testing Strategy

### Phase 0: Current Testing
- **Unit Tests**: 20 tests covering configuration, CLI, app, and agents
- **Test Coverage**: 93% for Phase 0 features
- **Framework**: pytest with pytest-cov
- **Test Locations**: `tests/` directory with conftest.py for fixtures
- **Performance**: Test suite completes in ~2.3 seconds

### Planned Test Expansion (Phase 1+)

**Test Categories**
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing  
- **E2E Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing

### Test Structure
```python
# Unit test example
@pytest.mark.asyncio
async def test_fact_checker_agent():
    agent = FactCheckerAgent(test_config)
    result = await agent.process(sample_research_data)
    
    assert result.credibility_score >= 1
    assert result.credibility_score <= 10
    assert len(result.detailed_analysis) > 0

# Integration test example  
@pytest.mark.asyncio
async def test_article_workflow():
    # Test complete article processing pipeline
    article = await article_service.create_article("Test Topic")
    result = await workflow_service.process_article(article.id)
    
    assert result.status == "completed"
    assert result.final_content is not None
```

## Planned Deployment Configuration (Phase 1+)

**Note**: Deployment infrastructure is not currently implemented. The application runs locally using `uv run python -m dime start`.

### Docker Compose (Planned)
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://dime:password@postgres:5432/dime_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./storage:/app/storage

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: dime
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dime_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Security Considerations

### Authentication & Authorization
- OAuth 2.0 with Google for user authentication
- JWT tokens for API access
- Role-based access control (Admin, Editor, Reviewer)
- Session management with Redis

### Data Protection
- Environment variable management for secrets
- Database connection encryption
- Input validation and sanitization
- Rate limiting on API endpoints

### Development Security
- Pre-commit hooks for security scanning
- Dependency vulnerability scanning
- Code quality checks (bandit security linter)
- Regular security updates

---

**Document Owner**: Development Team  
**Last Updated**: 2025-01-30  
**Next Review**: After Phase 1 implementation