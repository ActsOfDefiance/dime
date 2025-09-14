# GitHub Issue #002

**Title:** [BUG] Fix undefined agent references in publisher/agent.py

**Type:** Bug
**Priority:** 🔴 P0 - Critical
**Labels:** 🐛 bug, 🤖 agent, 🔴 P0 - Critical
**Milestone:** Phase 0: Foundation Fix
**Parent Epic:** #001
**Estimated Effort:** 3-5 days

## Bug Description

The current agent implementation in `publisher/agent.py` references undefined `researcher` and `writer` agents on line 32, causing runtime errors that block all system functionality.

## Steps to Reproduce

1. Run `uv run python -m dime.app`
2. Attempt to use any agent functionality
3. See NameError: name 'researcher' is not defined

## Expected Behavior

- Agent system should start without errors
- ADK agents should be properly defined and instantiated
- Basic agent conversation should be functional

## Actual Behavior

- Runtime NameError exceptions prevent system startup
- No agent functionality is accessible
- System completely non-functional

## Root Cause Analysis

**Technical Issues:**
- Variables `researcher` and `writer` referenced but never defined
- Missing agent class implementations
- No proper ADK agent registration patterns
- Incomplete migration from planning documents to working code

**Architecture Gap:**
- Documentation describes 7-stage multi-agent pipeline
- Implementation only has placeholder references
- Missing ADK integration patterns

## Acceptance Criteria

- [ ] System starts without NameError exceptions
- [ ] At least one working ADK agent is implemented (researcher OR writer)
- [ ] Basic agent conversation works through ADK web interface
- [ ] Agent health checks return positive status
- [ ] All imports resolve correctly

## Technical Requirements

**Minimum Viable Implementation:**
```python
# Create working agent definitions
class ResearcherAgent(Agent):
    def __init__(self):
        # Minimal ADK agent implementation
        pass

class WriterAgent(Agent):
    def __init__(self):
        # Minimal ADK agent implementation
        pass
```

**ADK Integration Requirements:**
- Proper agent discovery patterns
- Tool implementations for basic functionality
- Session management integration
- Health monitoring endpoints

**Implementation Approach:**
1. **Phase 1:** Create minimal working agents that resolve references
2. **Phase 2:** Implement basic ADK patterns and tools
3. **Phase 3:** Test agent instantiation and basic functionality

## Environment

- OS: Linux (development environment)
- Python version: 3.13+
- Dime version: Development (Phase 0)
- Dependencies: google-adk >=1.9.0

## Additional Context

**Backend Engineer Assessment:**
- This is the critical path blocker for all development
- Must be fixed before any other Phase 0 work can proceed
- Represents gap between planning documents and implementation reality

**Implementation Priority:**
- Highest priority in Phase 0
- All other tasks depend on this fix
- Required for ADK web interface functionality in Phase 1

## Definition of Done

### Bug Resolution Criteria
- [ ] **Runtime Error Fixed**: Zero NameError exceptions on system startup
- [ ] **System Startup**: `uv run python -m dime.app` completes without errors in <10 seconds
- [ ] **Agent References**: All agent variables (`researcher`, `writer`) properly defined and instantiated
- [ ] **Import Resolution**: All imports resolve correctly with no ModuleNotFoundError
- [ ] **ADK Integration**: Basic ADK agent functionality works end-to-end

### Code Quality Standards
- [ ] **Linting**: Zero errors from `ruff check .`
- [ ] **Formatting**: Zero formatting issues from `ruff format --check .`
- [ ] **Type Hints**: All new/modified functions have proper type annotations
- [ ] **Code Complexity**: Functions maintain cyclomatic complexity <8
- [ ] **PEP 8 Compliance**: All code follows Python style guidelines enforced by ruff
- [ ] **Import Organization**: Proper import grouping and ordering enforced by ruff

### Testing Requirements
- [ ] **Unit Tests**: Tests for agent instantiation and basic functionality
- [ ] **Integration Tests**: ADK agent workflow tests with proper mocking
- [ ] **Test Coverage**: ≥90% coverage for modified/new code
- [ ] **Test Execution**: All tests pass with 100% success rate
- [ ] **Performance**: Agent instantiation tests complete in <2 seconds each
- [ ] **Error Scenarios**: Tests for edge cases and error conditions

### Documentation Requirements
- [ ] **Class Docstrings**: All agent classes have comprehensive docstrings (Google style)
- [ ] **Method Documentation**: All public methods documented with parameters and return types
- [ ] **Code Comments**: Complex agent logic explained with inline comments
- [ ] **Architecture Notes**: Agent relationships and dependencies documented
- [ ] **Usage Examples**: Clear examples of agent instantiation and usage

### Functional Validation
- [ ] **ADK Web Interface**: Accessible at http://localhost:8000/ with agent selection
- [ ] **Agent Interaction**: Can send message and receive response through web interface
- [ ] **Session Management**: Agent conversations persist across requests
- [ ] **Health Endpoints**: `/api/health` and `/api/agent/health` return 200 status
- [ ] **Error Handling**: Graceful error messages for invalid inputs or failures

### Security & Performance
- [ ] **Input Validation**: Agent inputs properly validated and sanitized
- [ ] **Error Messages**: No sensitive information exposed in error responses
- [ ] **Resource Management**: Proper cleanup of agent resources and connections
- [ ] **Memory Usage**: Agent instantiation doesn't cause memory leaks
- [ ] **Response Time**: Basic agent responses in <3 seconds

### ADK Integration Standards
- [ ] **Agent Discovery**: Agents properly registered with ADK discovery system
- [ ] **Tool Integration**: Basic tools implemented with error handling and logging
- [ ] **Session Persistence**: Database-backed session management working
- [ ] **Configuration**: Environment-driven agent configuration with validation
- [ ] **Lifecycle Management**: Proper agent startup and shutdown procedures

### Production Readiness
- [ ] **Error Recovery**: System recovers gracefully from agent failures
- [ ] **Logging**: Structured logging for agent operations with appropriate levels
- [ ] **Monitoring**: Agent health metrics collected and reported
- [ ] **Configuration Validation**: Invalid configuration caught early with clear errors
- [ ] **Dependency Management**: All ADK dependencies properly declared and versioned