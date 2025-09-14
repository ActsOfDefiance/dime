# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Python package called "dime" that uses `uv` as the package manager. The project requires Python 3.13+ and has a core dependency on `google-adk`.

## Development Commands

### Package Management
- **Install dependencies**: `uv sync`
- **Add a dependency**: `uv add <package-name>`
- **Add a dev dependency**: `uv add --dev <package-name>`
- **Update dependencies**: `uv lock --upgrade`

### Running the Code
**Important**: Always run applications via `uv`, never call `python` directly.
- **Run the integrated application**: `uv run python -m dime.app`
- **Run any Python file**: `uv run python <filename.py>`

## Project Structure
```
dime/
├── agents/
│   └── dime_agent/          # ADK agent implementation
│       ├── __init__.py
│       └── agent.py           # Main agent class
├── dime/                   # Main package
│   ├── __init__.py
│   ├── main.py               # Application entry point
│   ├── app.py                # FastAPI application
│   ├── api/                  # API endpoints
│   │   ├── __init__.py
│   │   ├── agent.py          # ADK agent management endpoints  
│   │   ├── dependencies.py   # Dependency injection
│   │   ├── health.py         # Health check endpoints with monitoring
│   │   └── jobs.py           # Job management endpoints
│   ├── background/           # Background task processing
│   │   ├── __init__.py
│   │   ├── manager.py        # Task manager implementation
│   │   └── tasks.py          # Task definitions
│   ├── cache/                # Redis caching layer
│   │   ├── __init__.py
│   │   ├── redis_client.py   # Redis connection
│   │   ├── strategies.py     # Caching strategies
│   │   └── utils.py          # Cache utilities
│   ├── config/               # Configuration modules
│   │   ├── __init__.py
│   │   ├── agent.py          # ADK agent configuration
│   │   ├── agent_manager.py  # ADK agent lifecycle management
│   │   └── logging.py        # Logging configuration
│   ├── database/             # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py     # Database connection
│   │   ├── session.py        # Session management
│   │   └── models/           # SQLAlchemy models
│   │       ├── __init__.py
│   │       ├── analysis.py   # Analysis results
│   │       ├── episode.py    # Episode data
│   │       ├── job.py        # Background jobs
│   │       └── dime.py    # Dime metadata
│   ├── logging/              # Logging infrastructure
│   │   ├── __init__.py
│   │   ├── context.py        # Log context management
│   │   └── middleware.py     # Request logging middleware
│   ├── monitoring/           # Performance monitoring
│   │   ├── __init__.py
│   │   ├── decorators.py     # Performance tracking decorators
│   │   └── metrics.py        # APM metrics collection
│   └── services/             # Business logic
│       ├── __init__.py
│       └── workflow.py       # Workflow orchestration
├── tests/                    # Test suite
├── docs/                     # Documentation
├── alembic/                  # Database migrations
├── pyproject.toml           # Project configuration
└── uv.lock                  # Dependency lock file
```

## Key Dependencies
- **google-adk** (>=1.9.0): Google's ADK library

## API and SDK Guidelines
- When working with SDK's and API's use context7
- Use `gcloud` for managing Google infrastructure

## Project Documentation

### Discovery & Planning
- **Product Discovery**: See `docs/development/product-discovery-session.md` for complete discovery session results
- **Requirements Analysis**: See `docs/development/requirements-analysis.md` for stakeholder analysis and requirements
- **Current State Analysis**: See `docs/development/current-state-analysis.md` for gap analysis between current and target state
- **Content Capabilities**: See `docs/development/content-capabilities-specification.md` for content creation workflow and capabilities

### Technical Documentation  
- **Technical Requirements**: See `docs/development/technical-requirements.md` for complete system specifications
- **Technical Architecture**: See `docs/development/technical-architecture-specification.md` for system design decisions
- **Implementation Plan**: See `docs/development/implementation-plan.md` for development phases and timeline
- **Project Structure**: See `docs/development/project-structure.md` for codebase organization and development workflow
- **GitHub Setup**: See `docs/development/github-project-setup.md` for project management configuration
- **Agent Prompts**: See `docs/technical/agent-prompts.md` for agent instruction specifications

### Legacy Documentation (Imported)
- **API Reference**: See `docs/technical/api-reference.md` for API specifications and endpoint documentation
- **Architecture**: See `docs/technical/architecture.md` for system design and component structure  
- **Database Examples**: See `docs/technical/database-examples.md` for database usage patterns

## Environment Management & Configuration

### Pydantic Settings System
The project uses Pydantic Settings for comprehensive configuration management with direnv integration:

- **Settings Module**: `dime.config.settings` - Centralized configuration with validation
- **Environment Variables**: Managed via direnv and `.envrc` file
- **Configuration Sections**: Nested settings for app, database, cache, agent, logging, auth, and storage
- **Validation**: Automatic environment validation with helpful error messages
- **Secrets**: Secure handling of API keys and tokens using Pydantic SecretStr

### Environment Setup
1. **Copy template**: `cp .envrc.example .envrc`
2. **Configure values**: Edit `.envrc` with your settings
3. **Reload environment**: `direnv reload` or restart shell
4. **Verify config**: Application validates on startup

### Settings Usage in Code
```python
from dime.config import get_settings, get_app_settings, get_logfire_settings

# Get complete settings
settings = get_settings()
database_url = settings.database.url
logfire_token = settings.get_logfire_token()

# Get specific sections
app_config = get_app_settings()
debug_mode = app_config.debug

# Environment checks
if settings.is_development:
    # Development-specific code
    pass
```

### Configuration Sections
- **Application**: Core app settings (name, version, debug mode)
- **Database**: PostgreSQL connection and pool configuration
- **Redis**: Cache settings and connection parameters
- **Google ADK**: Project ID, location, API keys for agent functionality
- **Agent**: ADK agent behavior and limits configuration
- **Logfire**: Logging and observability settings with token management
- **Authentication**: JWT secrets and OAuth configuration
- **Storage**: File storage paths and size limits

### Environment Variables
Required environment variables managed in `.envrc`:
- `DATABASE_URL`: PostgreSQL connection string
- `GOOGLE_ADK_PROJECT_ID`, `GOOGLE_ADK_API_KEY`: Google ADK configuration
- `LOGFIRE_TOKEN`: Pydantic Logfire API token (optional for development)
- `AUTH_JWT_SECRET_KEY`: JWT signing secret
- See `.envrc.example` for complete list with documentation

## ADK Agent Integration

### Architecture Overview
The project integrates Google ADK (Agent Development Kit) for a multi-agent content creation system focused on political liberation movements and historical analysis. The system processes articles through a 7-stage pipeline with human approval gates.

### Agent Configuration
- **Configuration class**: `dime.config.agent.AgentConfig` - Environment-driven configuration management
- **Manager class**: `dime.config.agent_manager.DimeAgentManager` - Production lifecycle management
- **Environment variables**: Comprehensive agent, tool, and session configuration via `.envrc`
- **Validation**: Built-in configuration validation with detailed error reporting

### Development Commands
- **Run integrated application**: `uv run python -m dime.app` (ADK web UI at root, APIs under `/api`)
- **Agent health check**: `curl http://localhost:8000/api/health/agent`
- **Restart agent**: `curl -X POST http://localhost:8000/api/agent/restart`
- **Access web interfaces**:
  - ADK Agent Web UI: http://localhost:8000/
  - Developer UI: http://localhost:8000/dev-ui/
  - API Documentation: http://localhost:8000/docs
  - Health Dashboard: http://localhost:8000/api/health

### Agent Structure
- **Agent location**: `agents/dime_agent/agent.py`
- **Agent pattern**: Uses direct `Agent` class with proper ADK discovery patterns
- **Tools integration**: Enhanced tools with error handling, validation, and structured logging
- **Health monitoring**: Built-in health tracking with metrics and status reporting
- **Session management**: Database-backed sessions with PostgreSQL integration

### API Endpoints

#### ADK Web Interface (at root)
- **GET /**: ADK agent web interface for interactive conversations
- **GET /dev-ui/**: Developer tools and agent debugging interface
- **POST /run_sse**: Server-Sent Events endpoint for agent conversations
- **GET /list-apps**: List available ADK agents

#### Management Endpoints (under `/api/agent`)
- **GET /api/agent/health**: Comprehensive agent health check
- **GET /api/agent/status**: Basic agent status information
- **POST /api/agent/restart**: Restart agent manager
- **GET /api/agent/config**: Get agent configuration (sanitized)

#### Health Integration
- **GET /api/health**: System health check (includes agent health)
- **GET /api/health/agent**: Dedicated agent health check

### Environment Configuration
Required environment variables in `.envrc`:

```bash
# ADK Agent Configuration
export AGENT_NAME="dime_agent"
export AGENT_MODEL="gemini-2.5-flash"
export AGENT_MAX_LLM_CALLS=500
export ENABLE_AGENT_TRACING=false

# Tool Configuration
export TOOL_TIMEOUT_SECONDS=60
export TOOL_MAX_RETRIES=3

# Session Configuration
export AGENT_SESSION_DB_URL="${DATABASE_URL}"
export AGENT_SERVE_WEB=true
export AGENT_ALLOWED_ORIGINS="http://localhost,http://localhost:3000,http://localhost:8000,http://localhost:8080,*"
```

### Multi-Agent Content Pipeline
The dime system uses a 7-stage multi-agent pipeline for content creation:

1. **Topic Selection**: Human-driven topic curation
2. **Research Agent**: Content research and source gathering
3. **Fact Checker Agent**: Source validation and credibility scoring
4. **Writer Agent**: Article creation from research
5. **Editor Agent**: Style and quality refinement
6. **Graphics Agent**: Image generation with human approval
7. **Assembly Agent**: Final document compilation and Git publishing

### Production Features
- **Lifecycle management**: Automatic startup/shutdown with FastAPI application lifecycle
- **Error handling**: Comprehensive error recovery and graceful degradation
- **Health monitoring**: Real-time health checks and performance metrics
- **Structured logging**: Integration with existing logging infrastructure
- **Configuration validation**: Environment variable validation with helpful error messages
- **Session persistence**: Database-backed session management for conversation continuity

### Development Workflow
1. **Environment setup**: Configure environment variables in `.envrc` 
2. **Start application**: `uv run python -m dime.app` (unified single-process application)
3. **Verify health**: Check `/api/health` to ensure agent is running
4. **Test interaction**: Use `/` (root) for interactive ADK agent conversations
5. **Monitor metrics**: Use `/api/agent/health` for detailed status information

### Integration Points
- **Single Process Architecture**: ADK serves as main FastAPI application with custom routes for API endpoints
- **Health system**: Agent health integrated into comprehensive system health checks
- **Logging**: Structured logging with monitoring events and correlation IDs
- **Configuration**: Environment-driven configuration with validation and error reporting
- **Database**: Shared database connection for session persistence
- **Background tasks**: Compatible with existing background task infrastructure

## Code Quality

- **Every commit must**:
  - Pass all existing tests
  - Include tests for new functionality
  - Follow project formatting/linting

- **Before committing**:
  - Run formatters/linters
  - Self-review changes


## Definition of Done

- [ ] Tests written and passing
- [ ] Code follows project conventions
- [ ] No linter/formatter warnings
- [ ] Commit messages are clear
- [ ] Implementation matches plan
- [ ] No TODOs without issue numbers

## Error Handling

- Fail fast with descriptive messages
- Include context for debugging
- Handle errors at appropriate level
- Never silently swallow exceptions


## Testing Strategy
Based on Issue #2 implementation experience, comprehensive testing requires both unit and end-to-end approaches:

### Unit Testing (pytest)
- Test individual functions and components in isolation
- Mock external dependencies (API calls, databases)
- Fast execution and good for development workflow
- **Limitation**: Cannot validate complete user workflows

### End-to-End Testing (Playwright recommended)
- **Critical requirement**: Test complete user workflows from user perspective
- **Chat validation**: Test entire conversations with real agent responses
- **Agent integration**: Validate multi-agent pipeline processes articles end-to-end
- **Human approval workflow**: Test approval gates between each agent stage
- **Content quality**: Validate fact-checking, writing, and editing agent outputs
- **API integration**: Test real HTTP requests to ADK web server endpoints
- **Session management**: Verify session creation, persistence, and state management
- **Error scenarios**: Test invalid inputs, API failures, timeout handling
- **Cross-browser**: Validate ADK web UI works across different browsers

### Testing Insights
- Unit tests alone are insufficient for ADK agent validation
- ADK agents require real API integration testing to verify functionality
- Tool execution must be validated in context of complete conversations
- Session state and persistence are critical for multi-turn conversations
- HTTP endpoint testing needs real server responses, not just mocks

## Coding Guidelines
- **Type System**: Use Pydantic for data validation and serialization
- **Type Checking**: Use pyright for static type analysis
- **Linting & Formatting**: Use ruff for both linting and code formatting
- **Logging**: Use Pydantic Logfire for structured logging and observability
- **Code Style**: Follow PEP 8, enforced by ruff
- **File Endings**: All Python files should end with a single newline character

## Development Tools
- **Linting**: `uv run ruff check .`
- **Formatting**: `uv run ruff format .`
- **Type Checking**: `uv run pyright`
- **Testing**: `uv run pytest`
- **Logging**: Structured logging with Logfire instrumentation

## Logging Standards
- **Use Logfire**: Import and configure `logfire` for all logging needs
- **Structured Logging**: Use structured data with Pydantic models where applicable
- **Instrumentation**: Instrument FastAPI, SQLAlchemy, and ADK agent operations
- **Log Levels**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Context**: Include relevant context (user_id, request_id, agent_name, etc.)
- **Performance**: Log performance metrics for agent operations and API calls
- **Security**: Never log sensitive data (passwords, API keys, personal information)

## Commit and Testing Policy
- We require 100% test pass before committing. No skipping tests allowed
- Run `uv run ruff format .` on every file after editing
- Ensure `uv run ruff check .` passes with zero errors
- Ensure `uv run pyright` passes with zero errors



## Important Reminders

**NEVER**:
- Disable tests instead of fixing them
- Commit code that doesn't pass tests
- Make assumptions - verify with existing code

**ALWAYS**:
- Update plan documentation as you go
- Learn from existing implementations
- Stop after 3 failed attempts and reassess

- Always run tests and require 100% test passage before committing
- When updating existing code, also update tests and fixtures
- Always run ruff formatting and linting before committing
- Ensure pyright type checking passes before committing
- Use Pydantic models for all data validation and API schemas
- Include structured logging with Logfire for all new functionality
- Ensure logging follows security guidelines (no sensitive data)
- This is github project we are using for this project https://github.com/ActsOfDefiance/dime