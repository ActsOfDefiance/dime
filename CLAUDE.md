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
- **Run the integrated application**: `uv run python -m dime.app`
- **Run any Python file**: `uv run python <filename.py>`

## Current Project State & Critical Issues

### Known Issues (Phase 0: Foundation Fix)
The project is currently in Phase 0 with critical runtime issues that must be resolved:

1. **Critical Bug**: `publisher/agent.py` has undefined `researcher` and `writer` variables (line 30)
   - Causes NameError on system startup
   - Blocks all functionality
   - Must be fixed before any development can proceed

2. **Missing Project Structure**: The documented `dime/` package structure doesn't exist
   - Only basic `dime/__init__.py` and `dime/config/` modules are implemented
   - Most of the planned architecture is not yet built

3. **Testing Framework**: No testing infrastructure exists
   - No `/tests` directory
   - No pytest configuration
   - Required for Phase 0 completion

### Current Working Components
- **Configuration System**: Pydantic Settings with environment validation in `dime/config/settings.py`
- **Environment Management**: direnv integration with `.envrc` (contains secrets, not tracked)
- **Package Management**: Modern uv-based dependency management
- **Git Workflow**: Gitflow methodology with protected main/develop branches

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
├── dime/                     # Main package (minimal implementation)
│   ├── __init__.py          # Package initialization
│   └── config/              # Configuration system (working)
│       ├── __init__.py
│       └── settings.py      # Pydantic Settings with environment validation
├── publisher/               # Legacy agent code (has critical bugs)
│   ├── __init__.py
│   └── agent.py            # Contains undefined variable references
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

## Phase 0 Development Priority
1. **Fix Critical Bug**: Resolve undefined agent references in `publisher/agent.py`
2. **Establish Testing**: Set up pytest framework with ADK testing patterns
3. **Create Basic Interface**: Implement CLI interface and ADK web interface
4. **Update Documentation**: Align documentation with actual implementation

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