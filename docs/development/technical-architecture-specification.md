# Dime Technical Architecture Specification

## Executive Summary

This document defines the technical architecture for the Dime content creation agent, providing a phased approach from the current minimal implementation to a full-featured content creation platform.

## Architecture Evolution Strategy

### Current State (v0.1)
- Minimal Python project with basic Google ADK agents
- Single file implementation in `publisher/agent.py`
- No persistence, web interface, or API

### Target State (v1.0+)
- Production-ready content creation platform
- Web interface with API access
- Database persistence and caching
- Background job processing
- Comprehensive monitoring and deployment

### Migration Path
**Phase 1**: Fix current issues and establish foundation  
**Phase 2**: Add core features (database, web UI)  
**Phase 3**: Advanced features (API, background jobs, monitoring)  
**Phase 4**: Production deployment and scaling

## Architecture Options Analysis

### Option 1: Simple Agent System (Recommended for MVP)

**Architecture:**
```
User → CLI/Simple Web UI → Google ADK Agent → Content Files
```

**Components:**
- Single-process application with Google ADK
- File-based content storage
- Simple web interface or CLI
- Direct integration with Google AI models

**Pros:**
- Fast development (2-4 weeks)
- Low complexity and maintenance
- Matches current implementation
- Minimal infrastructure requirements

**Cons:**
- Limited scalability
- No collaboration features
- Basic content management
- Manual backup/recovery

**Use Case:** MVP, proof of concept, small team usage

### Option 2: Web Application (Recommended for v1.0)

**Architecture:**
```
User → Web UI → FastAPI Backend → Google ADK Agent → Database
                     ↓
              Background Jobs ← Redis Queue
```

**Components:**
- FastAPI web application with React/Vue frontend
- PostgreSQL for content and session storage
- Redis for caching and job queues
- Google ADK for agent orchestration
- Background processing for long-running tasks

**Pros:**
- User-friendly web interface
- Scalable to medium usage
- Content management features
- Background processing capabilities

**Cons:**
- Higher development complexity (2-3 months)
- More infrastructure requirements
- Database management overhead

**Use Case:** Production deployment, team collaboration, content management

### Option 3: API-First Platform (Future v2.0+)

**Architecture:**
```
Multiple Clients → API Gateway → Microservices → Message Queue → Workers
                                      ↓
                                 Database Cluster
```

**Components:**
- Microservices architecture with API gateway
- Multiple databases (PostgreSQL, Vector DB for embeddings)
- Container orchestration (Docker/Kubernetes)
- Advanced monitoring and observability
- Multi-tenant support

**Pros:**
- High scalability and performance
- Multiple client support
- Advanced features (ML/AI integration)
- Enterprise-grade reliability

**Cons:**
- High development complexity (6+ months)
- Significant infrastructure costs
- Complex deployment and maintenance

**Use Case:** Large-scale deployment, multiple organizations, enterprise features

## Recommended Architecture (Hybrid Approach)

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Fix current implementation and establish working system

**Architecture:**
```
CLI Interface → Fixed ADK Agents → File Storage
```

**Implementation:**
```python
# Fixed agent structure
research_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="researcher",
    instruction="Liberation movement research specialist..."
)

publisher_agent = SequentialAgent(
    name="publisher", 
    model="gemini-2.0-flash-thinking-exp",
    sub_agents=[research_agent],
    instruction="Editorial oversight and quality control..."
)
```

**Components:**
- **Fixed Agent System**: Resolve undefined agent references
- **CLI Interface**: Command-line tool for content creation
- **File Storage**: Markdown files with metadata headers
- **Basic Testing**: pytest framework with core tests

**Deliverables:**
- Working agent system without errors
- CLI for content creation workflows
- Test coverage >50% for core functionality
- Updated documentation matching implementation

### Phase 2: Web Interface (Weeks 3-6)
**Goal**: Add user-friendly interface and basic persistence

**Architecture:**
```
Web UI → FastAPI → ADK Agents → SQLite Database
```

**Components:**
- **FastAPI Backend**: REST API for content operations
- **Web Frontend**: Simple HTML/CSS/JS interface
- **SQLite Database**: Local database for development
- **Content Management**: CRUD operations for articles

**Key Features:**
- Article creation and editing interface
- Research workflow management
- Basic user authentication
- Content preview and publishing

### Phase 3: Production Features (Weeks 7-12)
**Goal**: Production-ready deployment with advanced features

**Architecture:**
```
Web UI → FastAPI → ADK Agents → PostgreSQL
               ↓
      Background Jobs ← Redis
```

**Components:**
- **PostgreSQL**: Production database with proper schema
- **Redis**: Caching and background job processing
- **Enhanced Web UI**: Rich text editor, content management
- **Background Processing**: Long-running research tasks
- **Monitoring**: Health checks and basic metrics

**Key Features:**
- Async content generation
- Content collaboration tools
- Publication scheduling
- Basic analytics and reporting

## Technical Stack Specification

### Core Technologies

#### Backend Framework
**FastAPI** (chosen for Phase 2+)
- High performance with async support
- Automatic API documentation (OpenAPI/Swagger)
- Type hints and validation with Pydantic
- Easy integration with Google ADK

#### Database Strategy
**Phase 1**: File system (JSON/Markdown)
**Phase 2**: SQLite for development
**Phase 3**: PostgreSQL for production

#### Agent Framework
**Google ADK** (current choice)
- Direct integration with Google AI models
- Built-in conversation management
- Tool calling and function execution
- Web UI and API endpoints

#### Frontend Options
**Phase 1**: CLI only
**Phase 2**: Simple HTML templates
**Phase 3**: React/Vue SPA or enhanced server-side rendering

### Database Schema Design

#### Core Entities
```sql
-- Content Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Content Articles
CREATE TABLE articles (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    research_notes TEXT,
    sources JSONB,
    status VARCHAR(50) DEFAULT 'draft',
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Research Sources
CREATE TABLE sources (
    id UUID PRIMARY KEY,
    article_id UUID REFERENCES articles(id),
    title VARCHAR(255),
    author VARCHAR(255),
    url TEXT,
    citation TEXT,
    credibility_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent Sessions (for ADK integration)
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY,
    article_id UUID REFERENCES articles(id),
    session_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### API Specification

#### Core Endpoints
```yaml
# Content Management
GET    /api/articles           # List articles
POST   /api/articles           # Create article
GET    /api/articles/{id}      # Get article
PUT    /api/articles/{id}      # Update article
DELETE /api/articles/{id}      # Delete article

# Research Operations
POST   /api/research/start     # Start research process
GET    /api/research/{job_id}  # Get research status
POST   /api/research/sources   # Add research sources

# Agent Interactions
POST   /api/agent/chat         # Chat with agent
GET    /api/agent/sessions     # List agent sessions
POST   /api/agent/generate     # Generate content

# System Operations
GET    /api/health            # Health check
GET    /api/metrics           # System metrics
```

### Security & Quality

#### Security Requirements
- **Authentication**: JWT-based for API access
- **Authorization**: Role-based access control
- **Data Protection**: Encryption at rest and in transit
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: API usage protection

#### Quality Assurance
- **Testing Strategy**: Unit (80%), Integration (15%), E2E (5%)
- **Code Quality**: Black formatting, flake8 linting, mypy type checking
- **Documentation**: API docs, deployment guides, user documentation
- **Monitoring**: Health checks, performance metrics, error tracking

## Deployment Architecture

### Phase 1: Development
```
Local Machine → Python/uv → File System
```

### Phase 2: Single Server
```
Single VM → Docker Compose → PostgreSQL + Redis + FastAPI
```

### Phase 3: Scalable Cloud
```
Load Balancer → App Servers → Database Cluster
                    ↓
              Background Workers
```

### Infrastructure Components

#### Development Environment
- **Local Development**: uv for Python environment management
- **Database**: PostgreSQL with Docker for consistency
- **Testing**: pytest with coverage reporting
- **Code Quality**: pre-commit hooks with formatting and linting

#### Production Environment
- **Container Platform**: Docker with multi-stage builds
- **Orchestration**: Docker Compose (Phase 2) → Kubernetes (Phase 3)
- **Database**: Managed PostgreSQL (Google Cloud SQL, AWS RDS)
- **Caching**: Managed Redis (Google Memorystore, AWS ElastiCache)
- **Monitoring**: Health checks, logging, performance metrics

## Performance & Scaling

### Performance Requirements
- **Response Time**: <2 seconds for UI interactions
- **Content Generation**: <60 seconds for article creation
- **Research Processing**: <5 minutes for comprehensive research
- **Concurrent Users**: 10-50 (Phase 2), 100+ (Phase 3)

### Scaling Strategy
- **Horizontal Scaling**: Multiple application instances behind load balancer
- **Database Scaling**: Read replicas, connection pooling
- **Background Processing**: Worker queues for long-running tasks
- **Caching**: Multi-layer caching (Redis, CDN, application level)

### Resource Planning
```
Phase 1: Local development - minimal resources
Phase 2: Single server - 4 CPU, 8GB RAM, 100GB storage
Phase 3: Multi-server - Load balancer + 2-4 app servers + managed services
```

## Risk Assessment & Mitigation

### Technical Risks
1. **Google ADK Dependency**: Single point of failure
   - *Mitigation*: Agent abstraction layer, fallback models
2. **Database Performance**: Content and research data growth
   - *Mitigation*: Query optimization, proper indexing, archival strategy
3. **Content Quality**: AI-generated content accuracy
   - *Mitigation*: Editorial review process, human oversight, fact-checking tools

### Operational Risks
1. **Deployment Complexity**: Multi-component system
   - *Mitigation*: Infrastructure as code, automated deployment, comprehensive documentation
2. **Data Loss**: Content and research data protection
   - *Mitigation*: Regular backups, database replication, disaster recovery procedures
3. **Security Vulnerabilities**: Web application security
   - *Mitigation*: Security testing, regular updates, penetration testing

## Success Metrics

### Technical Metrics
- **System Availability**: >99% uptime
- **Response Time**: <2 seconds for 95% of requests
- **Code Quality**: >90% test coverage, zero critical vulnerabilities
- **Deployment Success**: <5 minute deployment time, zero failed deployments

### Business Metrics
- **Content Quality**: >95% accuracy rate, editorial approval
- **User Satisfaction**: User feedback scores, task completion rates
- **System Usage**: Daily active users, content creation volume
- **Development Velocity**: Features delivered per sprint, bug resolution time

---

**Document Status**: v1.0  
**Last Updated**: 2025-01-30  
**Next Review**: After Phase 1 completion