# Dime Content Creation Agent - API Reference

**Version**: Phase 0 (Foundation)
**Last Updated**: 2025-01-30
**Status**: Basic ADK Integration Complete

## Overview
This document provides API documentation for the Dime Content Creation Agent. The Phase 0 implementation uses Google ADK's `get_fast_api_app()` utility which provides automatic agent discovery and web interface integration.

## Base URLs
- **Development**: `http://localhost:8000`
- **Production**: Not yet deployed

## Phase 0: Current Implementation

### Architecture Overview
The application runs as a single process using Google ADK's FastAPI integration:
- **ADK Agent Web UI** at the root (`/`)
- **Developer Tools** at `/dev-ui/`
- **Built-in ADK endpoints** for agent interactions
- **No custom REST API endpoints** (using ADK's default behavior)

### Available Interfaces

#### ADK Agent Web UI
- **URL**: `http://localhost:8000/`
- **Description**: Interactive agent conversations provided by Google ADK
- **Features**:
  - Agent chat interface
  - Session management
  - Tool execution visibility
  - Conversation history
- **Status**: ✅ Implemented and working

#### Developer Tools
- **URL**: `http://localhost:8000/dev-ui/`
- **Description**: Agent development and debugging interface provided by Google ADK
- **Features**:
  - Agent introspection
  - Tool inspection
  - Session debugging
  - Configuration viewing
- **Status**: ✅ Implemented and working

### CLI Interface

The application provides a simple CLI for local development:

#### Health Check
```bash
uv run python -m dime health
```

**Output Example**:
```
✅ Configuration loaded successfully
📁 Database: postgresql://user:***@localhost:5432/dime_dev
🤖 Agent: dime_agent
🌍 Environment: development
```

#### Start Server
```bash
# Default (localhost:8000)
uv run python -m dime start

# Custom host/port
uv run python -m dime start --host 127.0.0.1 --port 3000
```

### Agent Interactions

#### Available Agents
- **dime_agent** (root agent): Coordinates research and writing workflows
- **researcher**: Research agent for content research
- **writer**: Writing agent for article creation

#### Using the Web Interface
1. Navigate to http://localhost:8000/
2. Start a conversation with the agent
3. Ask for research or content creation
4. View real-time tool execution
5. Review agent responses

### Authentication
**Phase 0**: No authentication implemented
- All endpoints are open for local development
- No API keys required for ADK web interface
- Configuration validation only

### Configuration Management
**Environment Variables**: All configuration via `.envrc` file
```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost/dime
GOOGLE_ADK_PROJECT_ID=your-project-id
GOOGLE_ADK_API_KEY=your-api-key

# Required (placeholders OK for Phase 0)
AUTH_GOOGLE_OAUTH_CLIENT_ID=placeholder
AUTH_GOOGLE_OAUTH_CLIENT_SECRET=placeholder
AUTH_JWT_SECRET_KEY=dev-secret-key
```

## Planned API Endpoints (Phase 1+)

**Note**: The following endpoints are planned for future implementation. They do not currently exist.

### Health Monitoring (Planned)
```bash
# System health check (planned)
GET /api/health

# Agent-specific health (planned)
GET /api/agent/health
```

### Job Management (Planned)
```bash
# Create content job (planned)
POST /api/jobs/create
{
  "content_type": "blog_post",
  "topic": "technology trends"
}

# Check job status (planned)
GET /api/jobs/{job_id}/status
```

### Agent Management (Planned)
```bash
# List available agents (planned)
GET /api/agents

# Get agent details (planned)
GET /api/agents/{agent_id}

# Execute agent task (planned)
POST /api/agents/{agent_id}/execute
```

### Content Operations (Planned)
```bash
# Create article (planned)
POST /api/content/articles

# Get article (planned)
GET /api/content/articles/{article_id}

# Update article (planned)
PUT /api/content/articles/{article_id}
```

## Development

### Testing the Application
```bash
# Run health check
uv run python -m dime health

# Start server
uv run python -m dime start

# Access web interface
# Open http://localhost:8000 in browser
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test
uv run pytest tests/test_app.py -v
```

## Production Considerations (Phase 1+)

**Planned for future phases**:
- JWT-based authentication for API access
- Session-based authentication for web interfaces
- API key management for programmatic access
- Rate limiting and request validation
- Monitoring and alerting for health endpoints
- Error tracking and logging infrastructure
- CORS configuration for production domains
- Input validation and sanitization
- Response caching and optimization

## Migration Notes

**From Phase 0 to Phase 1**:
- Custom REST API endpoints will be added under `/api/*`
- Authentication system will be implemented
- Database persistence will be added
- Job queue and background processing will be implemented
- Health monitoring endpoints will be created
- The ADK web interface will remain available alongside custom APIs

## Additional Resources

- **[Local Development Guide](../setup/local-development.md)**: Setup instructions
- **[Architecture Documentation](./architecture.md)**: System design
- **[Agent Prompts](./agent-prompts.md)**: Agent configurations
- **[Google ADK Documentation](https://ai.google.dev/adk)**: Official ADK docs

---

**Document Status**: Aligned with Phase 0 implementation
**Next Review**: After Phase 1 API implementation
