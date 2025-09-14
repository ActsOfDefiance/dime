# GitHub Issue #004

**Title:** [FEATURE] Create basic CLI interface and ADK web interface

**Type:** Feature
**Priority:** 🟠 P1 - High
**Labels:** ✨ feature, 📝 content, 🌐 web, 🤖 agent, 🟠 P1 - High
**Milestone:** Phase 0: Foundation Fix
**Parent Epic:** #001
**Estimated Effort:** 5-7 days
**Dependencies:** #002 (agent references), #003 (testing framework)

## Feature Description

Implement basic CLI interface for content creation workflows and ensure ADK web interface is functional. This provides user-facing access to the agent system and validates the foundation for Phase 1 web interface enhancements.

## Problem Statement

Currently there is no functional user interface:
- No CLI commands for content creation workflows
- ADK web interface not accessible or functional
- No way for users to interact with the agent system
- Cannot validate end-to-end functionality
- Missing entry points per CLAUDE.md specifications

## Proposed Solution

Implement dual interface approach:

1. **Basic CLI Interface** - Command-line access for developer workflows
2. **ADK Web Interface** - Browser-based interface using Google ADK development UI

Both interfaces should provide access to the basic content creation workflow and validate agent functionality.

## User Stories

- As a **content creator**, I want a CLI interface so that I can create content through command-line workflows
- As a **developer**, I want an ADK web interface so that I can test and debug agent conversations
- As a **user**, I want basic content creation workflow so that I can research → draft → review content
- As a **team member**, I want both interfaces working so that we can validate the system foundation

## Acceptance Criteria

**CLI Interface:**
- [ ] Entry point `uv run python -m dime.app` works without errors
- [ ] Basic CLI commands for content workflow (research, draft, review)
- [ ] Help system with command documentation
- [ ] Error handling with clear user messages
- [ ] Integration with agent system

**ADK Web Interface:**
- [ ] ADK web interface accessible at http://localhost:8000/
- [ ] Developer UI available at http://localhost:8000/dev-ui/
- [ ] Basic agent conversation functionality
- [ ] Session management working
- [ ] Health dashboard accessible

**Integration Requirements:**
- [ ] Both interfaces use same underlying agent system
- [ ] Consistent user experience between CLI and web
- [ ] Proper error handling and logging
- [ ] Health monitoring integration

## Technical Requirements

**CLI Implementation (per CLAUDE.md):**
```bash
# Main application entry point
uv run python -m dime.app

# CLI commands structure
dime create [topic]     # Start content creation workflow
dime research [topic]   # Run research phase
dime draft [topic]      # Generate draft from research
dime review [content]   # Review and edit content
dime status            # Show current workflows
dime health            # System health check
```

**ADK Web Interface Implementation:**
```python
# FastAPI application with ADK integration
app = FastAPI()

# ADK endpoints (served at root)
GET /                  # ADK agent web interface
GET /dev-ui/          # Developer tools and debugging
POST /run_sse         # Server-Sent Events for conversations
GET /list-apps        # List available ADK agents

# API endpoints (under /api)
GET /api/health       # System health check
GET /api/agent/health # Agent-specific health
```

**Architecture Requirements:**
- Single process architecture (ADK as main FastAPI app)
- Shared database connection for session persistence
- Proper logging and monitoring integration
- Environment-driven configuration

## Implementation Plan

**Phase 1: Project Structure (Days 1-2)**
1. Create proper `dime/` package structure per CLAUDE.md
2. Implement `dime/main.py` and `dime/app.py` entry points
3. Set up basic FastAPI application structure
4. Create CLI argument parsing framework

**Phase 2: ADK Integration (Days 3-4)**
1. Configure ADK agent manager and lifecycle
2. Implement basic agent conversation endpoints
3. Set up session management with database
4. Create health monitoring endpoints

**Phase 3: CLI Implementation (Days 5-6)**
1. Implement basic CLI commands
2. Create command help system
3. Add error handling and user feedback
4. Test CLI integration with agent system

**Phase 4: Integration & Testing (Day 7)**
1. End-to-end testing of both interfaces
2. Error scenario testing
3. Performance validation
4. Documentation updates

## Technical Considerations

**ADK Integration Challenges:**
- Single process architecture requires careful FastAPI integration
- Session management needs database backend
- Agent lifecycle management during development
- Proper error handling for web interface

**CLI Design Decisions:**
- Command structure should match content workflow
- Error messages must be user-friendly
- Progress indication for long-running operations
- Consistent with existing uv-based execution patterns

**Shared Architecture:**
- Both interfaces use same agent system
- Consistent logging and error handling
- Shared configuration management
- Common health monitoring

## Environment Requirements

**Required Environment Variables (per CLAUDE.md):**
```bash
# ADK Agent Configuration
AGENT_NAME="dime_agent"
AGENT_MODEL="gemini-2.5-flash"
AGENT_MAX_LLM_CALLS=500
ENABLE_AGENT_TRACING=false

# Tool Configuration
TOOL_TIMEOUT_SECONDS=60
TOOL_MAX_RETRIES=3

# Session Configuration
AGENT_SESSION_DB_URL="${DATABASE_URL}"
AGENT_SERVE_WEB=true
AGENT_ALLOWED_ORIGINS="http://localhost,http://localhost:3000,http://localhost:8000,http://localhost:8080,*"
```

## Success Criteria

**Functional Validation:**
- [ ] `uv run python -m dime.app` starts without errors
- [ ] CLI help command shows available options
- [ ] ADK web interface loads and shows agent conversation UI
- [ ] Basic agent interaction works (send message, receive response)
- [ ] Health endpoints return green status
- [ ] Both interfaces can access same agent functionality

**Quality Standards:**
- [ ] All tests pass (100% requirement)
- [ ] Code follows formatting standards
- [ ] Proper error handling throughout
- [ ] Logging integration working
- [ ] Documentation updated

## Definition of Done

### Interface Implementation
- [ ] **CLI Interface**: Complete command-line interface with all specified commands working
- [ ] **ADK Web Interface**: Functional web interface accessible at http://localhost:8000/
- [ ] **Dual Access**: Both interfaces access same underlying agent system
- [ ] **Entry Points**: `uv run python -m dime.app` starts system without errors
- [ ] **Command Structure**: All documented CLI commands implemented and functional

### Code Quality Standards
- [ ] **Linting**: Zero errors from `ruff check .`
- [ ] **Formatting**: Zero formatting issues from `ruff format --check .`
- [ ] **Type Hints**: 100% type annotation coverage for all new code
- [ ] **Code Complexity**: Functions maintain cyclomatic complexity <10
- [ ] **PEP 8 Compliance**: All code follows Python style guidelines enforced by ruff
- [ ] **Import Organization**: Proper import grouping and ordering enforced by ruff
- [ ] **Code Documentation**: All public APIs documented with Google-style docstrings

### Testing Requirements
- [ ] **Test Coverage**: ≥90% line coverage for interface modules
- [ ] **Unit Tests**: Individual command and endpoint testing
- [ ] **Integration Tests**: End-to-end workflow testing for both interfaces
- [ ] **API Tests**: FastAPI endpoint testing with real HTTP requests
- [ ] **CLI Tests**: Command-line interface testing with argument parsing
- [ ] **Error Scenario Tests**: Invalid inputs and failure conditions tested
- [ ] **Performance Tests**: Interface response times under acceptable thresholds

### CLI Interface Requirements
- [ ] **Command Parsing**: Robust argument parsing with help system
- [ ] **Error Handling**: User-friendly error messages for invalid inputs
- [ ] **Progress Indication**: Progress feedback for long-running operations
- [ ] **Output Formatting**: Consistent and readable command output
- [ ] **Help System**: Comprehensive help documentation accessible via CLI
- [ ] **Exit Codes**: Proper exit codes for success/failure scenarios

### ADK Web Interface Requirements
- [ ] **Agent Conversation**: Multi-turn conversations with session persistence
- [ ] **Developer UI**: Debug interface accessible at /dev-ui/
- [ ] **Session Management**: Database-backed session persistence working
- [ ] **Real-time Updates**: Server-Sent Events for live conversation updates
- [ ] **Error Display**: User-friendly error messages in web interface
- [ ] **Mobile Responsive**: Interface works on mobile and desktop browsers

### API Integration Standards
- [ ] **FastAPI Integration**: Proper FastAPI application structure
- [ ] **Health Endpoints**: Comprehensive health monitoring at /api/health
- [ ] **Agent Management**: Agent lifecycle management endpoints
- [ ] **Error Responses**: Consistent error response format with proper HTTP codes
- [ ] **Request Validation**: Input validation using Pydantic models
- [ ] **API Documentation**: OpenAPI/Swagger documentation automatically generated

### Performance Criteria
- [ ] **Startup Time**: Application starts in <15 seconds
- [ ] **CLI Response**: CLI commands respond in <5 seconds for basic operations
- [ ] **Web Response**: Web interface loads in <3 seconds
- [ ] **Agent Response**: Basic agent interactions complete in <10 seconds
- [ ] **Memory Usage**: Base application memory usage <300MB
- [ ] **Concurrent Users**: Support for multiple concurrent web sessions

### Security Requirements
- [ ] **Input Validation**: All user inputs validated and sanitized
- [ ] **CORS Configuration**: Proper CORS settings for web interface
- [ ] **Session Security**: Secure session management with proper cleanup
- [ ] **Error Information**: No sensitive information leaked in error responses
- [ ] **Environment Secrets**: All sensitive configuration externalized
- [ ] **XSS Protection**: Web interface protected against common attacks

### Database Integration
- [ ] **Connection Management**: Proper database connection pooling
- [ ] **Session Persistence**: ADK sessions stored and retrieved from database
- [ ] **Transaction Management**: Database transactions properly handled
- [ ] **Migration Support**: Database schema migrations working
- [ ] **Cleanup Procedures**: Proper cleanup of expired sessions
- [ ] **Error Recovery**: Database connection failure recovery

### Documentation Requirements
- [ ] **API Documentation**: Complete API reference with examples
- [ ] **CLI Documentation**: Comprehensive command reference
- [ ] **User Guide**: End-user documentation for both interfaces
- [ ] **Developer Guide**: Setup and development instructions
- [ ] **Architecture Documentation**: System design and component interaction
- [ ] **Troubleshooting Guide**: Common issues and solutions

### Environment Configuration
- [ ] **Environment Variables**: All required environment variables documented
- [ ] **Configuration Validation**: Invalid configuration detected with clear errors
- [ ] **Default Values**: Sensible defaults for optional configuration
- [ ] **Development Mode**: Development-specific configuration options
- [ ] **Production Ready**: Configuration suitable for production deployment

### Integration Testing
- [ ] **End-to-End Workflows**: Complete user workflows tested
- [ ] **Cross-Interface Testing**: Same functionality works via both interfaces
- [ ] **Session Continuity**: Sessions persist across interface switches
- [ ] **Error Recovery**: Graceful recovery from various failure scenarios
- [ ] **Load Testing**: Basic load testing for concurrent usage
- [ ] **Browser Compatibility**: Web interface tested across major browsers

### Production Readiness
- [ ] **Monitoring Integration**: Application metrics and health monitoring
- [ ] **Structured Logging**: Comprehensive logging with correlation IDs
- [ ] **Resource Management**: Proper cleanup of resources and connections
- [ ] **Graceful Shutdown**: Clean shutdown procedures for both interfaces
- [ ] **Deployment Ready**: System can be containerized and deployed

## Additional Context

**Relationship to Phase 1:**
- This establishes foundation for Phase 1 ADK web interface focus
- Phase 1 will enhance the web interface with advanced features
- CLI remains as developer/power-user tool
- ADK integration patterns established here will be extended

**Backend Engineer Assessment:**
- ADK web interface is critical path for Phase 1 work
- CLI provides fallback and developer workflow
- Both interfaces validate agent system is working correctly
- Foundation for all future user interaction development