# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Python package called "dime" - a multi-agent content creation system for political liberation movement analysis using Google ADK. The project uses `uv` as the package manager and requires Python 3.13+.

## Development Commands

### Package Management
- **Install dependencies**: `uv sync`
- **Add a dependency**: `uv add <package-name>`
- **Add development dependency**: `uv add --dev <package-name>`
- **Update dependencies**: `uv lock --upgrade`

### Running the Code
**Important**: Always run applications via `uv`, never call `python` directly.
- **Start the web server**: `uv run python -m dime start` (starts ADK web interface on http://localhost:8000)
- **Health check**: `uv run python -m dime health` (validates configuration and system status)
- **Run any Python file**: `uv run python <filename.py>`

## Current Project State

### ✅ Phase 0: Foundation - COMPLETED
The foundation phase has been successfully completed with all critical issues resolved:

1. **✅ Fixed Critical Bugs**: All agent reference errors in `publisher/agent.py` resolved
2. **✅ CLI Interface**: Implemented CLI with `health` and `start` commands
3. **✅ ADK Web Interface**: Functional web interface using Google ADK's `get_fast_api_app()`
4. **✅ Agent System**: Proper ADK agent structure with automatic discovery
5. **✅ Configuration System**: Simplified case-sensitive configuration with automatic field mapping

### Current Working Components
- **✅ Configuration System**: Simplified Pydantic Settings with case-sensitive environment variable mapping
- **✅ CLI Interface**: `uv run python -m dime health` and `uv run python -m dime start` commands
- **✅ ADK Web Interface**: Functional web interface at http://localhost:8000/ when server is running
- **✅ Agent Discovery**: Proper ADK agent structure in `agents/dime_agent/` directory
- **✅ Environment Management**: direnv integration with `.envrc` (contains secrets, not tracked)
- **✅ Package Management**: Modern uv-based dependency management
- **✅ Git Workflow**: Gitflow methodology with protected main/develop branches

### Next Phase Requirements
- **Testing Framework**: Set up pytest framework with ADK testing patterns
- **Enhanced Agent Tools**: Implement more sophisticated content creation tools
- **Database Integration**: Full PostgreSQL and Redis integration

## Architecture Overview

### Multi-Agent Content Pipeline (Planned)
The system is designed as a 7-stage content creation pipeline:
1. **Topic Selection**: Human-driven topic curation
2. **Research Agent**: Content research and source gathering
3. **Fact Checker Agent**: Source validation and credibility scoring
4. **Writer Agent**: Article creation from research
5. **Editor Agent**: Style and quality refinement
6. **Graphics Agent**: Image generation with human approval
7. **Assembly Agent**: Final document compilation and Git publishing

### Technology Stack
- **Core Framework**: Google ADK (Agent Development Kit) >= 1.0.0
- **Web Framework**: FastAPI (planned)
- **Database**: PostgreSQL with SQLAlchemy (planned)
- **Caching**: Redis (planned)
- **Observability**: Logfire for structured logging (configured)
- **Authentication**: Google OAuth + JWT (planned)

### Current File Structure
```
dime/
├── dime/                     # Main package (✅ implemented)
│   ├── __init__.py          # Package initialization
│   ├── app.py               # ✅ FastAPI application with ADK integration
│   ├── __main__.py          # ✅ CLI entry point (health, start commands)
│   └── config/              # ✅ Configuration system (working)
│       ├── __init__.py
│       └── settings.py      # ✅ Simplified Pydantic Settings with case-sensitive mapping
├── agents/                  # ✅ ADK agent directory
│   └── dime_agent/          # ✅ Main content creation agent
│       ├── __init__.py
│       └── agent.py         # ✅ ADK agent with research and writing tools
├── publisher/               # ✅ Legacy agent code (fixed)
│   ├── __init__.py
│   └── agent.py            # ✅ Fixed undefined variable references
├── docs/                    # Project documentation
│   └── github_issues/       # Detailed implementation requirements
├── .envrc                   # Environment variables (contains secrets, git-ignored)
├── pyproject.toml          # Project configuration
└── uv.lock                 # Dependency lock file
```

## Key Dependencies
- **google-adk** (>=1.0.0): Google's Agent Development Kit for multi-agent systems

## Coding Guidelines
- **Always follow PEP 8 styles**: Code style enforced by ruff
- **Run ruff format on every file after editing**: Auto-formatting required
- **Do not overengineer**: Simplicity is a virtue
- **Use uv python package management**: Never use pip directly
- **Never run `python` directly**: Always use `uv run`
- **Use Pydantic for typing**: Type validation and serialization
- **All Python files should end with a single newline character** (PEP 8)

## Environment Configuration
- **Environment Management**: Uses direnv with `.envrc` file
- **Environment Variables**: Comprehensive configuration via environment
- **Secrets Management**: `.envrc` contains API keys and is git-ignored
- **Configuration Classes**: Pydantic Settings with nested configuration in `dime.config.settings`

## Branch Management & Git Workflow
- **Methodology**: Gitflow workflow (user preference)
- **Protected Branches**: `main` and `develop` require pull requests with 1 required reviewer
- **Branch Structure**:
  - `main`: Production-ready code
  - `develop`: Integration branch for features
  - `feature/`: Feature development branches
  - `hotfix/`: Critical production fixes
- **No Direct Pushes**: All changes must go through PR process
- **Status Checks**: All PRs must pass CI tests before merge
- **Branch Protection**: Force pushes disabled, deletions blocked

## Quality Standards (Phase 0 Requirements)

### Code Quality
- **Linting**: Must pass `ruff check .`
- **Formatting**: Must pass `ruff format --check .`
- **Type Checking**: 100% type hint coverage required
- **Complexity**: Cyclomatic complexity <10 per function
- **Coverage**: ≥90% test coverage required

### Testing Requirements
- **Framework**: pytest (to be implemented)
- **Coverage**: pytest-cov with ≥90% line coverage
- **Test Types**: Unit tests for core logic, integration tests for ADK workflows
- **Performance**: Test suite must complete in <60 seconds
- **ADK Testing**: Special patterns needed for agent workflow testing

### Performance Criteria
- **Application Startup**: System starts in <10 seconds
- **Health Check Response**: <200ms response time
- **Memory Usage**: Base footprint <200MB
- **Agent Response**: Basic conversations <5 seconds

## Development Interfaces

### CLI Interface
- **Health Check**: `uv run python -m dime health` - validates configuration and displays system status
- **Start Server**: `uv run python -m dime start` - launches ADK web interface on http://localhost:8000
- **Custom Host/Port**: `uv run python -m dime start --host 127.0.0.1 --port 3000`

### ADK Web Interface
When running `uv run python -m dime start`, the following interfaces become available:
- **Main Interface**: http://localhost:8000/ - Interactive ADK agent conversations
- **Developer UI**: http://localhost:8000/dev-ui/ - ADK development and debugging tools
- **Agent Discovery**: Automatic discovery and loading of agents from `agents/` directory

### Configuration System
- **Environment Variables**: All configuration via uppercase environment variables in `.envrc`
- **Case Sensitivity**: Configuration uses case-sensitive field mapping (e.g., `DATABASE_URL` → `DATABASE_URL`)
- **Auto-Discovery**: Field names automatically map to environment variables without prefixes or complex field mappings
- **Validation**: Built-in validation with descriptive error messages

## Next Phase Development Priority
1. **✅ COMPLETED**: Fix Critical Bug - Resolved undefined agent references in `publisher/agent.py`
2. **✅ COMPLETED**: Create Basic Interface - Implemented CLI interface and ADK web interface
3. **✅ COMPLETED**: Update Documentation - Aligned documentation with actual implementation
4. **TODO**: Establish Testing - Set up pytest framework with ADK testing patterns

## Commit and Testing Policy
- **100% test pass before committing**: No skipping tests allowed
- **Run ruff format on every file after editing**: Auto-formatting required
- **When updating existing code, also update tests and fixtures**
- **Never disable tests instead of fixing them**
- **Never commit code that doesn't pass tests**
- **Never make assumptions - verify with existing code**
- **Always update plan documentation as you go**
- **Stop after 3 failed attempts and reassess**

## Definition of Done Requirements
Every commit must:
- Pass all existing tests (100% pass rate)
- Include tests for new functionality
- Follow project formatting/linting standards
- Have clear commit messages
- Match planned implementation
- Include proper error handling with descriptive messages
- Fail fast with descriptive error messages
- Include context for debugging
- Handle errors at appropriate level
- Never silently swallow exceptions

## Important Notes
- **Critical Path Blocker**: The undefined agent references must be fixed first
- **ADK Integration**: Requires proper agent discovery patterns and session management
- **Content Focus**: System targets political liberation movement analysis
- **Audience**: Liberal audience, 20-40 years old, college-educated or lay interest in political history
- **Quality Standards**: Emphasis on source citation and accuracy for historical content
- Never use inline imports. Imports always go in the header in accordance with PEP8
- always start with the simplest approach possible