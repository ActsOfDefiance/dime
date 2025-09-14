# Dime Content Creation Agent - API Reference

## Overview
This document provides comprehensive API documentation for the Dime Content Creation Agent with Google ADK integration. The system provides both interactive agent conversations through the ADK web interface and REST API access for programmatic integration.

## Base URLs
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Architecture Overview
The application runs as a single process combining:
- **ADK Agent Web UI** at the root (`/`)
- **REST API endpoints** under `/api`
- **Health monitoring** under `/api/health`
- **Agent management** under `/api/agent`

## Web Interfaces

### ADK Agent Web UI
- **URL**: `http://localhost:8000/`
- **Description**: Interactive agent conversations with persistent sessions
- **Features**: Agent chat, session management, tool execution

### Developer Tools
- **URL**: `http://localhost:8000/dev-ui/`
- **Description**: Agent development and debugging interface
- **Features**: Agent introspection, tool testing, session debugging

### API Documentation
- **URL**: `http://localhost:8000/docs`
- **Description**: Interactive OpenAPI documentation (Swagger UI)
- **Features**: API exploration, request testing, schema validation

## Authentication
Currently the system operates without authentication for development. Production deployment should implement:
- JWT-based authentication for API access
- Session-based authentication for web interfaces
- API key management for programmatic access

## WebSocket/SSE Support
The ADK integration provides real-time communication:
- **Server-Sent Events** for agent conversations
- **Session persistence** across connections
- **Real-time tool execution** feedback

## Example Usage

### Starting a Conversation
```bash
# Start agent conversation
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a blog post about technology trends"}''
```

### Checking System Health
```bash
# System health check
curl http://localhost:8000/api/health

# Agent-specific health
curl http://localhost:8000/api/agent/health
```

### Job Management
```bash
# Start content creation job
curl -X POST http://localhost:8000/api/jobs/create \
  -H "Content-Type: application/json" \
  -d '{"content_type": "blog_post", "topic": "technology trends"}'

# Check job status
curl http://localhost:8000/api/jobs/{job_id}/status
```

## Development
- **Interactive API Docs**: Visit `/docs` for OpenAPI documentation
- **Agent Testing**: Use `/dev-ui/` for agent development tools
- **Health Monitoring**: Monitor system status via `/api/health`

## Production Considerations
- Enable authentication and authorization
- Configure rate limiting and request validation
- Set up monitoring and alerting for health endpoints
- Implement proper error tracking and logging
- Configure CORS settings for production domains
