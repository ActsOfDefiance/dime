# Technical Reference Documentation

This folder contains technical reference documentation for developers working on the Dime Content Creation Agent codebase.

## Architecture & Design

- **[Architecture Overview](architecture.md)** - System design, components, and data flow
  - Core components and their interactions
  - Database schema and relationships
  - API design patterns
  - Background task processing architecture

## Configuration & Setup

- **[Settings Usage Examples](settings-usage-examples.md)** - Pydantic Settings configuration
  - Environment variable management with direnv
  - Configuration sections and validation
  - Usage patterns and best practices
  - Testing and development workflows

- **[Logfire Configuration](logfire-configuration.md)** - Structured logging and observability
  - Logfire setup and configuration
  - Agent instrumentation patterns
  - Performance monitoring and metrics
  - Security and compliance guidelines

## Agent Development

- **[Agent Prompts](agent-prompts.md)** - ADK agent configuration and prompts
  - Agent instruction specifications
  - Tool integration patterns
  - Multi-agent workflow design

## API Documentation

- **[API Reference](api-reference.md)** - Complete API endpoint documentation
  - REST API endpoints and specifications
  - Request/response schemas
  - Authentication and error handling
  - OpenAPI/Swagger integration

## Database Reference

- **[Database Examples](database-examples.md)** - Database usage patterns and examples
  - SQLAlchemy model usage
  - Query patterns and best practices
  - Migration examples
  - Database optimization techniques

## Related Implementation

The technical documentation here corresponds to:

## For Developers

This technical reference is intended for:

- **Backend Developers** - Understanding API and database patterns
- **System Architects** - Reviewing system design decisions
- **DevOps Engineers** - Understanding deployment requirements
- **Contributors** - Learning the codebase structure

For setup and deployment information, see [docs/setup/](../setup/).
For performance optimizations, see [docs/optimizations/](../optimizations/).
