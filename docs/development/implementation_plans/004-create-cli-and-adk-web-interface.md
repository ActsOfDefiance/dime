# Implementation Plan: Issue #4 - Create Basic CLI Interface and ADK Web Interface

**Issue**: [FEATURE] Create basic CLI interface and ADK web interface
**Priority**: P1 - High
**Labels**: ✨ feature, 🌐 web, 📝 content, 🤖 agent
**Milestone**: Phase 0: Foundation Fix

## Overview

Implement basic CLI interface for content creation workflows and ensure ADK web interface is functional. This provides user-facing access to the agent system and validates the foundation for Phase 1 web interface enhancements.

## Key Insights from ADK Documentation Research

**Critical Discovery**: Google ADK provides `get_fast_api_app()` utility that handles most FastAPI integration automatically, including:
- Agent discovery and lifecycle management
- ADK web interface serving (at root `/`)
- Developer UI at `/dev-ui/`
- Health endpoints and session management
- CORS configuration and middleware setup

**Current Blocking Issues**:
1. Configuration parsing error for `allowed_origins` field
2. Missing application entry points (`dime/app.py`, `dime/__main__.py`)
3. No ADK agent implementation in expected structure
4. Broken agent references in `publisher/agent.py`

## Implementation Plan

### Phase 1: Fix Configuration System (Day 1, ~2 hours)
**Problem**: Config validation failing on `allowed_origins` JSON parsing
**Solution**:
1. **Debug and fix `parse_allowed_origins()` method** in `dime/config/settings.py`
   - Issue: Pydantic trying to parse comma-separated string as JSON
   - Fix: Ensure proper string-to-list conversion for CSV format
2. **Test configuration loading** without errors
3. **Validate all environment variables** from `.envrc`

### Phase 2: Create ADK-Compliant Application Structure (Day 1, ~4 hours)
**Following ADK official patterns from documentation:**

1. **Create `dime/app.py`** - Main FastAPI application using ADK utilities:
```python
import os
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from dime.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()

    # Use ADK's official FastAPI factory
    app: FastAPI = get_fast_api_app(
        agents_dir=os.path.join(os.path.dirname(__file__), "agents"),
        session_service_uri=str(settings.database.url),
        allow_origins=settings.app.allowed_origins,
        web=True,  # Enable ADK web interface
        trace_to_cloud=settings.is_production
    )

    app.title = settings.app.name
    app.description = "Dime Content Creation Agent System"

    return app
```

2. **Create `dime/__main__.py`** - CLI entry point:
```python
import argparse
import uvicorn
from dime.app import create_app
from dime.config import get_settings

def main():
    parser = argparse.ArgumentParser(description="Dime Content Creation System")
    parser.add_argument("--host", default=None, help="Host to bind to")
    parser.add_argument("--port", type=int, default=None, help="Port to bind to")
    parser.add_argument("command", nargs="?", default="start", choices=["start", "health"])

    args = parser.parse_args()
    settings = get_settings()

    if args.command == "health":
        # Simple health check
        print("✅ Configuration loaded successfully")
        return

    # Start FastAPI server
    app = create_app()
    uvicorn.run(
        app,
        host=args.host or settings.app.host,
        port=args.port or settings.app.port
    )

if __name__ == "__main__":
    main()
```

### Phase 3: Create Proper ADK Agent Structure (Day 2, ~4 hours)
**Following ADK agent discovery patterns:**

1. **Create `agents/dime_agent/` directory structure**:
   - `agents/dime_agent/__init__.py`
   - `agents/dime_agent/agent.py` - Main agent using ADK patterns

2. **Implement `agents/dime_agent/agent.py`** following ADK best practices:
```python
from google.adk.agents import Agent, SequentialAgent, LlmAgent
from google.adk.tools.function_tool import FunctionTool
from google.adk.models.lite_llm import LiteLlm

def research_topic(topic: str) -> dict:
    """Research a topic for content creation."""
    return {"status": "success", "research": f"Research data for {topic}"}

def write_content(research_data: dict) -> dict:
    """Write content based on research."""
    return {"status": "success", "content": f"Article based on {research_data}"}

# Create individual agents
researcher_agent = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Research topics related to liberation movements and political history.",
    tools=[FunctionTool(research_topic)]
)

writer_agent = LlmAgent(
    name="writer",
    model="gemini-2.5-flash",
    instruction="Write engaging articles for a general audience based on research.",
    tools=[FunctionTool(write_content)]
)

# Main agent - this will be discovered by ADK
root_agent = SequentialAgent(
    name="dime_agent",
    description="Content creation system for political liberation movement articles",
    instruction="Coordinate research and writing for high-quality political content.",
    sub_agents=[researcher_agent, writer_agent]
)
```

### Phase 4: Fix Existing Publisher Agent (Day 2, ~2 hours)
**Fix syntax errors in `publisher/agent.py`:**
1. Fix line 10: `name="r`esearcher"` → `name="researcher"`
2. Add missing comma after model parameter on line 9
3. Define missing `researcher` and `writer` agents referenced on line 30
4. Import required dependencies

### Phase 5: Integration and Testing (Day 3, ~4 hours)

1. **End-to-end validation**:
   - `uv run python -m dime.app` starts successfully
   - ADK web interface accessible at `http://localhost:8000/`
   - Developer UI accessible at `http://localhost:8000/dev-ui/`
   - Agent discovery working (agents appear in dropdown)
   - Basic conversation functionality works

2. **CLI interface testing**:
   - `uv run python -m dime.app health` - configuration check
   - `uv run python -m dime.app start` - start web server
   - Custom port/host arguments work

3. **Health endpoint validation**:
   - System health endpoints return proper status
   - Agent health monitoring functional
   - Session management working with database

## Key Architectural Decisions

1. **Use ADK's `get_fast_api_app()`** instead of manual FastAPI setup
   - Provides automatic agent discovery
   - Includes built-in ADK web interface
   - Handles session management and health endpoints
   - Manages CORS and middleware automatically

2. **Follow ADK agent directory conventions**:
   - `agents/[agent_name]/agent.py` with `root_agent` variable
   - ADK automatically discovers and exposes agents
   - Proper agent hierarchy with SequentialAgent orchestration

3. **Leverage existing Pydantic Settings system**:
   - Integrate with ADK's session service URI pattern
   - Use existing environment variable structure
   - Maintain configuration validation and error handling

## Success Criteria
- ✅ `uv run python -m dime.app` executes without errors (<15 seconds startup)
- ✅ ADK web interface accessible at http://localhost:8000/ with functional UI
- ✅ Agent appears in dropdown and basic conversations work
- ✅ Developer UI accessible at http://localhost:8000/dev-ui/
- ✅ Configuration loads without validation errors
- ✅ Health endpoints return proper JSON status
- ✅ All code passes `ruff check` and `ruff format` validation

## Files to Create/Modify:
- **Fix**: `dime/config/settings.py` (allowed_origins parsing)
- **Create**: `dime/app.py` (FastAPI with ADK integration)
- **Create**: `dime/__main__.py` (CLI entry point)
- **Create**: `agents/dime_agent/__init__.py`
- **Create**: `agents/dime_agent/agent.py` (main ADK agent)
- **Fix**: `publisher/agent.py` (syntax errors and missing agents)

## Technical Requirements

**CLI Implementation (per CLAUDE.md):**
```bash
# Main application entry point
uv run python -m dime.app

# CLI commands structure
dime health            # System health check
dime start             # Start web interface
```

**ADK Web Interface Implementation:**
```python
# FastAPI application with ADK integration
app = get_fast_api_app(...)

# ADK endpoints (served at root)
GET /                  # ADK agent web interface
GET /dev-ui/          # Developer tools and debugging
POST /run_sse         # Server-Sent Events for conversations
GET /list-apps        # List available ADK agents

# API endpoints (under /api)
GET /api/health       # System health check
GET /api/agent/health # Agent-specific health
```

## Definition of Done

### Interface Implementation
- [ ] **CLI Entry Point**: `uv run python -m dime.app` starts successfully in <15 seconds
- [ ] **Web Interface**: ADK web interface accessible at http://localhost:8000/ with functional UI
- [ ] **Developer UI**: ADK developer interface at http://localhost:8000/dev-ui/ working
- [ ] **Command Structure**: All CLI commands implemented with proper help system
- [ ] **Agent Integration**: Both interfaces can interact with agent system

### Code Quality Standards
- [ ] **Linting**: Zero errors from `ruff check .`
- [ ] **Formatting**: Zero formatting issues from `ruff format --check .`
- [ ] **Type Hints**: All interface functions properly typed with pyright validation
- [ ] **Code Complexity**: Functions maintain cyclomatic complexity <10
- [ ] **PEP 8 Compliance**: All code follows Python style guidelines enforced by ruff

### Testing Requirements
- [ ] **Test Coverage**: ≥90% line coverage for interface modules
- [ ] **Unit Tests**: Individual command and endpoint testing
- [ ] **Integration Tests**: End-to-end workflow testing for both interfaces
- [ ] **API Tests**: FastAPI endpoint testing with real HTTP requests
- [ ] **CLI Tests**: Command-line interface testing with argument parsing

### Performance Requirements
- [ ] **Application Startup**: System starts in <15 seconds from cold boot
- [ ] **Web Interface Response**: Page loads in <3 seconds
- [ ] **CLI Response**: Command execution completes in <5 seconds
- [ ] **Agent Interaction**: Basic agent responses in <10 seconds
- [ ] **Memory Usage**: Application uses <500MB RAM during normal operation

### ADK Integration Standards
- [ ] **Agent Discovery**: Proper ADK agent registration and discovery
- [ ] **Session Management**: Database-backed sessions with proper cleanup
- [ ] **Tool Integration**: Agent tools accessible through both interfaces
- [ ] **Lifecycle Management**: Proper startup/shutdown for ADK components
- [ ] **Configuration Validation**: ADK environment variables validated on startup

**Estimated Time**: 3 days (14 hours total)
**Risk Level**: Low-Medium (leveraging official ADK utilities reduces complexity)

---

**Document Status**: Implementation Plan v1.0
**Created**: 2025-01-14
**Last Updated**: 2025-01-14
**Author**: Claude Code Assistant