# Dime Project Structure & Development Guide

**Version**: 1.0  
**Date**: 2025-01-30  
**Status**: Development Ready  

## Project Directory Structure

```
dime/
├── README.md                      # Project overview and quick start
├── CLAUDE.md                      # Claude Code development guidelines
├── pyproject.toml                 # Python project configuration
├── uv.lock                        # Dependency lock file
├── .env.example                   # Environment variables template
├── .envrc                         # direnv configuration
├── docker-compose.yml             # Local development environment
├── docker-compose.prod.yml        # Production deployment (future)
│
├── src/                           # Source code
│   └── dime/                      # Main application package
│       ├── __init__.py
│       ├── main.py                # FastAPI application entry point
│       ├── config/                # Configuration management
│       │   ├── __init__.py
│       │   ├── settings.py        # Application settings
│       │   ├── database.py        # Database configuration
│       │   └── agents.py          # Agent configuration
│       ├── agents/                # AI Agent implementations
│       │   ├── __init__.py
│       │   ├── base.py            # Base agent class
│       │   ├── fact_checker.py    # Fact checking agent
│       │   ├── writer.py          # Content writing agent
│       │   ├── editor.py          # Content editing agent
│       │   ├── graphics.py        # Graphics generation agent
│       │   └── assembly.py        # Document assembly agent
│       ├── api/                   # FastAPI routes and endpoints
│       │   ├── __init__.py
│       │   ├── articles.py        # Article management endpoints
│       │   ├── research.py        # Research document endpoints
│       │   ├── agents.py          # Agent processing endpoints
│       │   ├── approvals.py       # Human approval endpoints
│       │   ├── graphics.py        # Graphics management endpoints
│       │   ├── auth.py            # Authentication endpoints
│       │   └── admin.py           # Admin and monitoring endpoints
│       ├── models/                # Database models
│       │   ├── __init__.py
│       │   ├── base.py            # Base model class
│       │   ├── article.py         # Article and workflow models
│       │   ├── agent.py           # Agent processing models
│       │   ├── user.py            # User and authentication models
│       │   └── content.py         # Content and media models
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

### Core Dependencies (pyproject.toml)
```toml
[project]
name = "dime"
version = "0.1.0"
description = "AI-powered content creation system for Acts of Defiance"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
    "psycopg2-binary>=2.9.7",
    "redis>=5.0.0",
    "google-adk>=1.9.0",
    "authlib>=1.2.0",
    "python-multipart>=0.0.6",
    "jinja2>=3.1.0",
    "pydantic>=2.5.0",
    "logfire[fastapi,sqlalchemy]>=0.20.0",
    "python-dotenv>=1.0.0",
    "click>=8.1.0",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "pyright>=1.1.0",
    "pre-commit>=3.4.0",
    "playwright>=1.39.0",
]

[project.scripts]
dime = "dime.cli.main:cli"
```

## Configuration Management

### Environment Variables (.env)
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

### Agent Configuration Files

#### agents/fact_checker.yml
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

### Local Development Setup
```bash
# 1. Clone repository
git clone https://github.com/ActsOfDefiance/dime.git
cd dime

# 2. Set up Python environment
uv sync --dev

# 3. Copy environment configuration
cp .env.example .env
# Edit .env with your configuration

# 4. Start development services
docker-compose up -d postgres redis

# 5. Initialize database
uv run alembic upgrade head

# 6. Run application
uv run uvicorn dime.main:app --reload --host 0.0.0.0 --port 8000
```

### Development Commands
```bash
# Application management
uv run python -m dime.main                    # Start FastAPI server
uv run python -m dime.cli --help             # CLI help

# Database operations
uv run alembic revision --autogenerate -m "description"  # Create migration
uv run alembic upgrade head                   # Apply migrations
uv run alembic downgrade -1                   # Rollback last migration

# Testing
uv run pytest                                 # Run all tests
uv run pytest tests/unit/                     # Run unit tests only
uv run pytest --cov=dime                      # Run with coverage
uv run playwright install                     # Install E2E test browsers

# Code quality
uv run ruff format .                          # Format code
uv run ruff check .                           # Lint code
uv run pyright                                # Type checking
uv run pre-commit run --all-files            # Run all quality checks
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

## Architecture Patterns

### Agent Pattern
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

### Test Categories
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

## Deployment Configuration

### Docker Compose (Local Development)
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