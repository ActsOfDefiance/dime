# Dime Content Creation Agent - System Architecture

## Overview
The Dime Content Creation Agent is an AI-powered system with Google ADK integration that provides content creation and editing capabilities through both interactive agent conversations and REST API access. The system features a unified single-process architecture combining ADK web interface with FastAPI backend services.

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Single Process Application                    │
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐ │
│  │  ADK Web UI     │    │   FastAPI APIs   │    │ ADK Agent   │ │
│  │                 │    │                 │    │             │ │
│  │ • Agent Chat    │───▶│ • Health Checks │───▶│ • Tools     │ │
│  │ • Developer UI  │    │ • Job Management│    │ • Sessions  │ │
│  │ • Sessions      │    │ • Agent Control │    │ • Logging   │ │
│  └─────────────────┘    └──────────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │                         │
                                ▼                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      Redis       │    │  Google AI      │
│                 │    │                  │    │                 │
│ • Agent Sessions│    │ • Jobs & Cache   │    │ • Gemini 2.0    │
│ • Job Metadata  │    │ • Task Queue     │    │ • AI Studio     │
│ • Analysis Data │    │ • Performance    │    │ • ADK Platform  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Services

1. **ADK Agent Service**
   - Interactive content creation conversations with persistent sessions
   - Real-time tool call tracking and performance metrics

2. **FastAPI Backend Services**
   - REST API for programmatic access
   - Background task processing with job management
   - Comprehensive health monitoring and system metrics
   - Agent lifecycle management (start/stop/restart)
   - Request correlation and structured logging

3. **Database Services**
   - PostgreSQL for persistent data storage
   - Agent session management
   - Job metadata and processing status
   - Content creation results and project metadata
   - Alembic for database migrations

4. **Caching & Task Management**
   - Redis for performance caching
   - Background task coordination
   - Real-time job status tracking
   - System performance metrics

5. **Health Monitoring System**
   - Multi-service health checks (database, redis, storage, agent)
   - System resource monitoring (CPU, memory, disk)
   - Application performance monitoring (APM)
   - Request timing and error tracking

## Data Flow


## Technology Stack

### Core Framework
- **Google ADK**: Agent orchestration and tool management
- **Python 3.13+**: Primary development language
- **uv**: Package management and virtual environments

### Development & Tooling
- **GitHub**: Version control, issue tracking, and project management
- **gcloud**: Google Cloud infrastructure management and deployment
- **direnv**: Environment variable management and .envrc configuration

### Infrastructure
- **PostgreSQL**: Relational database for metadata and results
- **Redis**: In-memory data store for job queues and caching
- **Google Cloud Storage**: Object storage for audio files and transcripts
- **Vertex AI**: Model hosting and auto-scaling platform

### Database & ORM
- **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapping (ORM)
- **Alembic**: Database migration tool for SQLAlchemy

### AI/ML Services
- **Gemini Models**: Content creation and natural language generation
- **SuperClaude**: Enhanced Claude integration for complex analysis

### Web Stack
- **FastAPI**: High-performance web framework for APIs
- **React/Vue**: Frontend dashboard (TBD)
- **uvicorn**: ASGI server for production deployment

## Database Schema

### Core Tables

- **Projects**: Content creation projects and metadata
- **Content**: Generated content pieces and revisions
- **Templates**: Reusable content templates and formats

### Authentication & Authorization
- JWT-based authentication for API access
- Role-based access control (RBAC) for different user types
- API key management for external service integrations

### Data Protection
- Encryption at rest for sensitive data
- TLS/HTTPS for all network communications
- Audit logging for all analysis requests

### Content Safety
- Content filtering for inappropriate material
- Privacy compliance for generated content
- Rate limiting to prevent abuse

## Scalability & Performance

### Horizontal Scaling
- Containerized deployment Cloud Run
- Auto-scaling based on job queue depth
- Load balancing across multiple instances

### Performance Optimization
- Redis caching for frequently accessed data
- Async processing for long-running tasks
- Batch processing for transcription jobs
- CDN for static assets and reports

### Monitoring
- Application performance monitoring (APM)
- Job queue monitoring and alerting
- Cost tracking for AI/ML service usage
- Error tracking and notification system

## Deployment Architecture

### Production Environment (Vertex AI)
```
Internet ──▶ Load Balancer ──▶ Vertex AI Endpoints
                    │
                    ▼
            ┌──────────────────┐
            │   Application    │
            │    Instances     │
            │                  │
            │ ┌──────────────┐ │
            │ │ ADK Agent    │ │
            │ │ FastAPI      │ │
            │ │ Workers      │ │
            │ └──────────────┘ │
            └──────────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │    Google Cloud         │
        │                         │
        │ ┌─────────┐ ┌─────────┐ │
        │ │PostgreSQL│ │  Redis  │ │
        │ │ (Cloud   │ │(Memstore)│ │
        │ │  SQL)    │ │         │ │
        │ └─────────┘ └─────────┘ │
        │                         │
        │ ┌─────────────────────┐ │
        │ │   Cloud Storage     │ │
        │ │ (Audio & Transcripts)│ │
        │ └─────────────────────┘ │
        └─────────────────────────┘
```

### Development Environment
- Local PostgreSQL and Redis instances
- Google Cloud Storage emulator for testing
- Docker Compose for local development stack
- Environment-specific configuration management

## Cost Optimization

### AI/ML Service Usage
- Batch processing to reduce API calls
- Caching of common analysis results
- Model selection based on accuracy vs. cost trade-offs
- Usage monitoring and budget alerts

### Infrastructure Costs
- Auto-scaling to match actual demand
- Reserved instances for predictable workloads
- Storage lifecycle policies for old audio files
- Regional deployment optimization

## Maintenance & Operations

### Backup Strategy
- Daily automated backups of PostgreSQL
- Point-in-time recovery capabilities
- Cross-region backup replication
- Disaster recovery procedures

### Monitoring & Alerting
- Health checks for all services
- Performance metrics and thresholds
- Error rate monitoring and alerting
- Cost anomaly detection

### Updates & Deployments
- Blue-green deployment strategy
- Automated testing pipeline
- Rollback procedures
- Database migration management
