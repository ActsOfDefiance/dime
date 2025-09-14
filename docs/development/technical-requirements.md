# Dime Content Creation Agent - Technical Requirements

**Version**: 1.0  
**Date**: 2025-01-30  
**Status**: Final  
**Derived from**: Product Discovery Session

## Executive Summary

Dime is a multi-agent content creation system for Acts of Defiance, focused on generating high-quality articles about political liberation movements and historical analysis. The system processes content through a 7-stage pipeline with human approval gates, delivering final articles via Git-based publishing.

## System Architecture

### Overview
- **Deployment**: Local development with future cloud migration
- **Budget**: $50/month primarily for AI API calls
- **Processing Volume**: 1-10 articles per day
- **Processing Time**: 1 hour per article maximum
- **Error Strategy**: Fail-fast with human intervention

### Technology Stack
- **Language**: Python 3.13+
- **Package Management**: uv
- **AI Framework**: Google ADK (Agent Development Kit)
- **Web Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **File Storage**: Local filesystem + Git
- **Frontend**: Web dashboard (HTML/CSS/JS initially)
- **Authentication**: OAuth Google Login via social-auth library

## Content Processing Workflow

### 7-Stage Agent Pipeline

#### 1. Topic Selection (Human)
- **Input**: Human-driven topic selection
- **Process**: Manual curation based on historical events, current relevance
- **Output**: Topic definition with scope and context

#### 2. Research (Human → Future AI)
- **Current**: Human-created markdown with footnote citations
- **Future**: Google Gemini Deep Research API integration
- **Input Methods**: 
  - Direct paste into conversation
  - Google Docs import
  - File system pickup
- **Format**: Markdown with footnotes `[^1]: Source information`
- **Output**: Research document with comprehensive source citations

#### 3. Fact Checker Agent
- **Input**: Research markdown document
- **Process**: Three-dimensional validation with 1-10 scoring:
  - Source credibility verification
  - Bias assessment
  - Claim verification against sources
- **Quality Gate**: Average score <5 triggers human review
- **Output**: Separate markdown report with detailed analysis
- **Retry Logic**: Auto-retry 2 times, then human intervention

#### 4. Writer Agent
- **Input**: Research document + fact-checking report
- **Content Specifications**:
  - Length: 5-10 paragraphs
  - Style: Casual, hip, intelligent
  - Audience: 25-40 years old, educated, topic-interested (not politics experts)
- **Strategy**: Prioritize high-credibility sources, downplay low-scoring ones
- **Citations**: Reference back to research document footnotes
- **Output**: Article draft in markdown format

#### 5. Editor Agent
- **Input**: Article draft + fact-checking report + research
- **Functions**:
  - Style consistency enforcement
  - Fact-checking validation
  - Readability optimization for target audience
  - Citation formatting standardization
- **Output**: Polished article ready for graphics

#### 6. Graphics Agent
- **Input**: Final article content
- **Process**: AI generation with human interaction/approval
- **Outputs**:
  - Large header/feature image
  - Thumbnail version of header image
- **Workflow**: Agent generates options → Human selects/refines
- **Output**: Image files with references for final document

#### 7. Document Assembly Agent
- **Input**: All previous outputs
- **Process**: Template-based document compilation
- **Output**: Single markdown document containing:
  - YAML frontmatter metadata
  - Original research document
  - Final article content
  - Image references
  - Fact-checking summary and scores
- **Destination**: Git repository for consumption by external application

## Human Approval System

### Approval Workflow
- **Trigger**: Each agent completion
- **Interface**: Web dashboard with progress indicators
- **Chat Integration**: Conversation interface with agent team
- **Notifications**: Browser alerts + optional Slack integration

### Approval Actions
- **Accept**: Proceed to next agent
- **Reject**: Store rejection with feedback, retry with human guidance
- **Edit Prompt**: Modify agent instructions for current task
- **Provide Feedback**: Structured feedback for reprocessing

### Review Information
- **Current Agent Output**: Latest generated content
- **Previous Agent Outputs**: Full pipeline history
- **Metadata**: Processing time, confidence scores, agent performance

### Tracking & Audit
- **Approval Log**: Who approved what and when
- **Rejection Tracking**: Reasons and feedback stored in database
- **Performance Metrics**: Agent success rates, processing times
- **Version History**: All iterations and modifications

## Data Architecture

### Database Schema (PostgreSQL)

#### Core Tables
```sql
-- Articles and Workflow
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'topic_selected',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP NULL,
    metadata JSONB DEFAULT '{}'
);

-- Agent Processing Steps
CREATE TABLE processing_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id),
    agent_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    confidence_scores JSONB,
    processing_time INTERVAL,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP NULL
);

-- Human Approvals
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    step_id UUID REFERENCES processing_steps(id),
    reviewer_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL, -- 'approve', 'reject', 'edit'
    feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Research Documents
CREATE TABLE research_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id),
    content TEXT NOT NULL,
    source_count INTEGER,
    import_method VARCHAR(50), -- 'paste', 'google_docs', 'file_system'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Fact Check Reports
CREATE TABLE fact_check_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id),
    credibility_score INTEGER CHECK (credibility_score BETWEEN 1 AND 10),
    bias_score INTEGER CHECK (bias_score BETWEEN 1 AND 10),
    verification_score INTEGER CHECK (verification_score BETWEEN 1 AND 10),
    average_score DECIMAL(3,2),
    detailed_analysis TEXT,
    flagged_for_review BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Generated Content
CREATE TABLE generated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id),
    content_type VARCHAR(50), -- 'draft', 'edited', 'final'
    content TEXT NOT NULL,
    word_count INTEGER,
    agent_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Graphics and Assets
CREATE TABLE graphics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id),
    image_type VARCHAR(50), -- 'header', 'thumbnail'
    file_path VARCHAR(500),
    alt_text TEXT,
    generation_prompt TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    google_id VARCHAR(100) UNIQUE,
    role VARCHAR(50) DEFAULT 'editor',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

### Caching Strategy (Redis)
- **Agent State**: Temporary processing state between stages
- **Session Data**: User sessions and authentication tokens
- **Performance Metrics**: Real-time processing statistics
- **Queue Management**: Background job queues for async processing

## API Specification

### Agent Management Endpoints
```yaml
# Article Workflow
POST   /api/articles                 # Create new article
GET    /api/articles                 # List articles with status
GET    /api/articles/{id}            # Get article details
PUT    /api/articles/{id}/status     # Update article status
DELETE /api/articles/{id}            # Delete article

# Research Management
POST   /api/articles/{id}/research   # Submit research document
GET    /api/articles/{id}/research   # Get research document
PUT    /api/articles/{id}/research   # Update research document

# Agent Processing
POST   /api/agents/{agent_name}/process  # Trigger agent processing
GET    /api/agents/{agent_name}/status   # Get agent status
POST   /api/agents/{agent_name}/retry    # Retry failed processing

# Human Approvals
GET    /api/approvals/pending        # Get pending approvals
POST   /api/approvals/{step_id}      # Submit approval decision
GET    /api/approvals/{step_id}      # Get approval details

# Content Generation
GET    /api/articles/{id}/content/{type}  # Get generated content
POST   /api/articles/{id}/feedback        # Submit feedback for revision

# Graphics Management
POST   /api/articles/{id}/graphics        # Generate graphics options
GET    /api/articles/{id}/graphics        # Get graphics options
POST   /api/articles/{id}/graphics/select # Select and refine graphics

# System Management
GET    /api/health                   # System health check
GET    /api/metrics                  # Performance metrics
GET    /api/users/profile            # User profile
```

## Agent Specifications

### Research Agent (Future Implementation)
- **Model**: Gemini 2.0 Flash
- **Capabilities**: Web scraping, document analysis, source verification
- **Output Format**: Markdown with structured footnotes
- **Performance Target**: <15 minutes per research task

### Fact Checker Agent
- **Model**: Gemini 2.5 Pro (for accuracy)
- **Scoring Dimensions**:
  - Source credibility (1-10): Publication reputation, author credentials
  - Bias assessment (1-10): Political lean, objectivity measures
  - Claim verification (1-10): Cross-referencing with authoritative sources
- **Output**: Structured JSON with detailed explanations
- **Performance Target**: <10 minutes per fact-check

### Writer Agent
- **Model**: Gemini 2.5 Pro
- **Style Configuration**:
  - Tone: Conversational but authoritative
  - Complexity: Accessible to college-educated general audience
  - Political Perspective: Progressive/leftist viewpoint
- **Citation Integration**: Seamless footnote references
- **Performance Target**: <20 minutes per article

### Editor Agent
- **Model**: Gemini 2.0 Flash (sufficient for editing tasks)
- **Editing Dimensions**:
  - Grammar and syntax correction
  - Style consistency enforcement
  - Fact-checking cross-reference
  - Readability optimization
- **Quality Metrics**: Flesch-Kincaid reading level 8-12
- **Performance Target**: <10 minutes per edit

### Graphics Agent
- **Model**: Gemini Pro + DALL-E 3 or Midjourney API
- **Image Types**:
  - Header image: 1200x630px for social media
  - Thumbnail: 300x200px for previews
- **Style Guide**: Consistent visual identity, historical aesthetic
- **Human Interaction**: Present 3-5 options for selection/refinement
- **Performance Target**: <15 minutes per graphics set

### Assembly Agent
- **Model**: Gemini 2.0 Flash (template processing)
- **Template Engine**: Jinja2 for markdown generation
- **Output Validation**: YAML frontmatter compliance, link verification
- **Git Integration**: Automated commit with structured commit messages
- **Performance Target**: <5 minutes per assembly

## Security & Authentication

### OAuth Integration
- **Provider**: Google OAuth 2.0
- **Library**: Python social-auth-app-django or authlib
- **Scope**: email, profile, openid
- **Token Management**: JWT with Redis storage

### Authorization Levels
- **Admin**: Full system access, user management
- **Editor**: Content creation and approval workflow
- **Reviewer**: Approval and feedback only
- **Viewer**: Read-only access to content and metrics

### Data Protection
- **Encryption**: All sensitive data encrypted at rest
- **API Security**: Rate limiting, input validation, CORS configuration
- **Audit Logging**: All user actions logged with timestamps
- **Backup Strategy**: Daily PostgreSQL dumps, Git repository backups

## Performance & Monitoring

### Performance Targets
- **End-to-end Processing**: <60 minutes per article
- **Web Interface Response**: <2 seconds for all operations
- **Agent Processing**: <20 minutes per agent (varies by complexity)
- **System Availability**: >99% uptime for local development

### Monitoring & Metrics
- **Agent Performance**: Success rates, processing times, retry counts
- **User Activity**: Approval rates, feedback frequency, session duration
- **System Health**: CPU/memory usage, database performance, cache hit rates
- **Cost Tracking**: AI API usage, token consumption, daily/monthly totals

### Error Handling
- **Failure Detection**: Automated health checks every 5 minutes
- **Retry Logic**: Exponential backoff with maximum 2 retries
- **Human Escalation**: Automatic notification after failure threshold
- **Graceful Degradation**: Continue pipeline with manual intervention options

## Deployment Architecture

### Local Development Environment
```
Docker Compose Stack:
├── app/                 # FastAPI application
├── postgres/           # PostgreSQL database
├── redis/             # Redis cache
├── nginx/             # Reverse proxy (optional)
└── monitoring/        # Prometheus + Grafana (optional)
```

### Configuration Management
- **Environment Variables**: .env files with validation
- **Agent Configuration**: JSON/YAML files for prompts and parameters
- **Database Migrations**: Alembic for schema versioning
- **Secrets Management**: Local environment variables, future cloud secrets

### Future Cloud Migration Path
- **Container Registry**: Google Container Registry
- **Compute**: Cloud Run for auto-scaling
- **Database**: Cloud SQL PostgreSQL
- **Cache**: Memorystore Redis
- **Storage**: Cloud Storage for assets
- **Monitoring**: Cloud Monitoring and Logging

## Quality Assurance

### Testing Strategy
- **Unit Tests**: 80%+ coverage for agent logic and business rules
- **Integration Tests**: API endpoints and database interactions
- **End-to-End Tests**: Complete workflow validation
- **Performance Tests**: Load testing for concurrent processing

### Code Quality
- **Formatting**: Black code formatter
- **Linting**: flake8 with strict rules
- **Type Checking**: mypy with strict configuration
- **Security**: bandit for security vulnerabilities

### Documentation Standards
- **Code Documentation**: Comprehensive docstrings
- **API Documentation**: OpenAPI/Swagger auto-generation
- **User Documentation**: Markdown guides in docs/
- **Architecture Documentation**: System design diagrams

## Development Workflow

### Git Strategy
- **Main Branch**: Stable, production-ready code
- **Feature Branches**: Individual feature development
- **Development Branch**: Integration testing
- **Release Tags**: Semantic versioning (v1.0.0)

### Development Phases
- **Phase 1**: Core agent pipeline with basic approval workflow
- **Phase 2**: Web dashboard with real-time progress tracking  
- **Phase 3**: Advanced features (graphics, analytics, optimization)
- **Phase 4**: Cloud deployment and scaling preparation

### Continuous Integration
- **Pre-commit Hooks**: Formatting, linting, type checking
- **Automated Testing**: Run full test suite on pull requests
- **Code Review**: Required approval for all changes
- **Deployment**: Automated deployment to development environment

---

**Document Owner**: Product Team  
**Review Schedule**: Monthly during active development  
**Next Review**: 2025-02-28