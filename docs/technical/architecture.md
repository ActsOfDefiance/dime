# Dime Content Creation Agent - System Architecture

**Version**: Phase 0 (Foundation)
**Last Updated**: 2025-01-30
**Status**: Basic ADK Integration Complete

## Overview

The Dime Content Creation Agent is an AI-powered content creation system built with Google ADK. The Phase 0 implementation provides a minimal viable foundation with basic agent orchestration and web interface.

## Phase 0: Current Architecture

### High-Level System Design

```
┌────────────────────────────────────────────┐
│      Single Process Application            │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │    Google ADK FastAPI Integration    │ │
│  │                                      │ │
│  │  • ADK Web UI (/)                   │ │
│  │  • Developer UI (/dev-ui/)          │ │
│  │  • Agent Discovery                   │ │
│  │  • Session Management                │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │         Agent Orchestration          │ │
│  │                                      │ │
│  │  • dime_agent (root)                │ │
│  │  • researcher (sub-agent)            │ │
│  │  • writer (sub-agent)                │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │      Configuration Management        │ │
│  │                                      │ │
│  │  • Pydantic Settings                 │ │
│  │  • Environment Variables (.envrc)    │ │
│  │  • Validation & Error Handling       │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Google Gemini  │
         │   AI Models     │
         │  (via ADK API)  │
         └────────────────┘
```

### Core Components

#### 1. Application Entry Points

**CLI Interface** (`dime/__main__.py`):
- `health`: Configuration validation and system status
- `start`: Launches ADK web server with agent discovery

**FastAPI Application** (`dime/app.py`):
- Uses ADK's `get_fast_api_app()` utility
- Automatic agent discovery from `agents/` directory
- Built-in web interface and developer tools

#### 2. Agent System

**Root Agent** (`agents/dime_agent/agent.py`):
- Name: `dime_agent`
- Type: SequentialAgent
- Purpose: Coordinates research and writing workflows
- Sub-agents: researcher, writer

**Research Agent**:
- Name: `researcher`
- Model: `gemini-2.5-flash`
- Tools: `research_topic` function
- Purpose: Content research and source gathering

**Writer Agent**:
- Name: `writer`
- Model: `gemini-2.5-flash`
- Tools: `write_content` function
- Purpose: Article creation from research

#### 3. Configuration System

**Implementation**: Simplified Pydantic Settings (`dime/config/settings.py`)
- Single `DimeSettings` class with all configuration
- Case-sensitive field names mapping directly to environment variables
- Automatic environment loading via direnv (`.envrc`)
- Built-in validation with descriptive error messages

**Required Configuration**:
- `DATABASE_URL`: PostgreSQL connection (placeholder OK for Phase 0)
- `GOOGLE_ADK_PROJECT_ID`: Google Cloud project ID
- `GOOGLE_ADK_API_KEY`: Google AI API key
- `AUTH_*`: Authentication settings (placeholders OK for Phase 0)

#### 4. Testing Infrastructure

**Framework**: pytest with pytest-cov
- 20 tests covering core functionality
- 93% code coverage for Phase 0 features
- Test locations: `tests/` directory
- Fixtures: `conftest.py` for shared test setup

**Test Coverage**:
- Configuration validation (`test_config.py`)
- CLI commands (`test_cli.py`)
- FastAPI application (`test_app.py`)
- Agent functionality (`test_agents.py`)

### Technology Stack

**Core Framework**:
- **Python 3.13+**: Primary development language
- **Google ADK 1.0+**: Agent orchestration and tool management
- **FastAPI**: Web framework (via ADK integration)
- **uvicorn**: ASGI server
- **Pydantic**: Configuration and data validation
- **uv**: Package management

**Development Tools**:
- **pytest 8.0+**: Testing framework
- **pytest-cov**: Code coverage reporting
- **ruff 0.8+**: Linting and formatting
- **httpx**: HTTP client for testing
- **direnv**: Environment variable management

**Version Control & Process**:
- **Git**: Version control
- **Gitflow**: Branch management methodology
- **GitHub**: Repository hosting and PR workflow

### Development Workflow

**Local Setup**:
1. Clone repository
2. Install dependencies with `uv sync`
3. Configure environment variables in `.envrc`
4. Run health check: `uv run python -m dime health`
5. Start server: `uv run python -m dime start`

**Development Commands**:
```bash
# Application
uv run python -m dime health
uv run python -m dime start

# Testing
uv run pytest
uv run pytest --cov

# Code Quality
uv run ruff format .
uv run ruff check .
```

### Current Limitations

**Phase 0 Constraints**:
- No database persistence (placeholder configuration only)
- No Redis caching
- No background job processing
- No authentication/authorization
- No custom REST API endpoints (using ADK's built-in)
- No production deployment infrastructure
- No monitoring or observability
- Limited CLI functionality (health check and start only)

---

## Planned Architecture (Phase 1+)

**Note**: The following architecture is planned for future phases and not currently implemented.

### Enhanced System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│                                                             │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  ADK Web UI      │    │  Custom REST API │              │
│  │                  │    │                  │              │
│  │  • Chat UI       │───▶│  • Health /api/  │              │
│  │  • Dev Tools     │    │  • Jobs /api/    │              │
│  └──────────────────┘    └──────────────────┘              │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Article    │  │    Agent     │  │   Approval   │     │
│  │   Service    │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Redis     │  │    Storage   │     │
│  │  (Sessions,  │  │  (Cache,     │  │  (Files,     │     │
│  │  Articles)   │  │  Jobs)       │  │  Graphics)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  External Services                           │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Google AI   │  │  Vertex AI   │  │  Cloud       │     │
│  │  (Gemini)    │  │  (Hosting)   │  │  Storage     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Planned Components

#### Enhanced Agent System (Phase 1)
- **Fact Checker Agent**: Source validation and credibility scoring
- **Editor Agent**: Style consistency and quality refinement
- **Graphics Agent**: AI-generated images with human approval
- **Assembly Agent**: Final document compilation and Git publishing

#### Database Layer (Phase 1)
- **PostgreSQL**: Session persistence, article storage, user data
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration management

#### Caching Layer (Phase 1)
- **Redis**: Performance caching, job queue, session storage
- **Cache Strategies**: TTL-based, pattern matching, invalidation

#### Custom REST API (Phase 1)
- **Health Endpoints**: `/api/health`, `/api/agent/health`
- **Job Management**: `/api/jobs/create`, `/api/jobs/{id}/status`
- **Content Operations**: `/api/content/articles/*`
- **Agent Management**: `/api/agents/*`

#### Authentication System (Phase 1)
- **OAuth 2.0**: Google authentication
- **JWT Tokens**: API access tokens
- **Role-Based Access**: Admin, Editor, Reviewer roles
- **Session Management**: Redis-backed sessions

#### Web Dashboard (Phase 1)
- **Approval Workflow**: Visual interface for human review
- **Progress Tracking**: Real-time status updates
- **Quality Metrics**: Performance and success rate tracking
- **Content Management**: Article browsing and editing

### Planned Technology Additions

**Backend Services**:
- **SQLAlchemy 2.0+**: Database ORM
- **Alembic 1.12+**: Database migrations
- **Redis 5.0+**: Caching and job queue
- **Celery**: Background task processing

**Security & Auth**:
- **authlib 1.2+**: OAuth implementation
- **python-jose**: JWT token handling
- **passlib**: Password hashing

**Monitoring & Observability**:
- **Logfire**: Application monitoring and logging
- **Sentry**: Error tracking and alerting
- **Prometheus**: Metrics collection

**Deployment**:
- **Docker**: Containerization
- **Cloud Run**: Serverless deployment
- **Cloud SQL**: Managed PostgreSQL
- **Memorystore**: Managed Redis

### Scalability Considerations

**Horizontal Scaling** (Phase 2+):
- Containerized deployment on Cloud Run
- Auto-scaling based on request volume
- Load balancing across multiple instances

**Performance Optimization** (Phase 2+):
- Redis caching for frequent queries
- Async processing for long-running tasks
- Database connection pooling
- CDN for static assets

**Monitoring** (Phase 2+):
- Application performance monitoring
- Cost tracking for AI API usage
- Error rate monitoring and alerting
- Resource utilization tracking

### Security Architecture

**Current (Phase 0)**:
- Environment-based secrets management
- No authentication (development only)
- Input validation via Pydantic

**Planned (Phase 1+)**:
- JWT-based authentication
- Role-based access control
- Database connection encryption
- API rate limiting
- Input sanitization
- CORS configuration
- Security headers
- Regular dependency updates

### Deployment Architecture

**Current (Phase 0)**:
- Local development only
- No production deployment

**Planned (Phase 1+)**:
```
Internet ──▶ Load Balancer ──▶ Cloud Run Instances
                    │
                    ▼
        ┌─────────────────────────┐
        │    Google Cloud         │
        │                         │
        │ ┌─────────┐ ┌─────────┐│
        │ │Cloud SQL│ │Memstore ││
        │ │(Postgres)│ │(Redis) ││
        │ └─────────┘ └─────────┘│
        │                         │
        │ ┌─────────────────────┐│
        │ │   Cloud Storage     ││
        │ │  (Files & Graphics) ││
        │ └─────────────────────┘│
        └─────────────────────────┘
```

## Migration Path

### Phase 0 → Phase 1
1. **Database Integration**: Add PostgreSQL with SQLAlchemy
2. **Caching Layer**: Integrate Redis for performance
3. **Custom API**: Implement REST endpoints under `/api/*`
4. **Authentication**: Add OAuth and JWT support
5. **Enhanced Agents**: Implement fact-checker, editor, graphics agents

### Phase 1 → Phase 2
1. **Deployment Infrastructure**: Docker + Cloud Run
2. **Monitoring**: Logfire, Sentry integration
3. **Performance Optimization**: Caching strategies, async processing
4. **Security Hardening**: Full production security measures
5. **Web Dashboard**: Human approval workflow interface

## Additional Resources

- **[API Reference](./api-reference.md)**: API endpoint documentation
- **[Agent Prompts](./agent-prompts.md)**: Agent configurations
- **[Local Development Guide](../setup/local-development.md)**: Setup instructions
- **[Project Structure](../development/project-structure.md)**: Code organization
- **[Google ADK Documentation](https://ai.google.dev/adk)**: Official ADK docs

---

**Document Status**: Aligned with Phase 0 implementation
**Next Review**: After Phase 1 implementation
**Owner**: Development Team
