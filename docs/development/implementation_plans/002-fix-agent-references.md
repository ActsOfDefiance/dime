# Implementation Plan: Fix Undefined Agent References (Issue #002)

**Issue**: [BUG] Fix undefined agent references in publisher/agent.py
**Priority**: 🔴 P0 - Critical
**Epic**: #001 - Foundation Fix
**Estimated Effort**: 4-6 hours

## Overview
Fix the critical NameError bug in `publisher/agent.py` that prevents system startup due to undefined `researcher` and `writer` agent references on line 30.

## Problem Analysis

### Current Issues
1. **Undefined Variables**: Line 30 references `researcher` and `writer` that are never defined
2. **Syntax Errors**:
   - Line 9: Missing comma after model parameter
   - Line 10: Stray backtick in `name="r\`esearcher"`
3. **Missing Agent Classes**: No implementation for ResearcherAgent or WriterAgent
4. **No ADK Integration**: Missing proper ADK agent discovery patterns

### Root Cause
Incomplete migration from planning documents to working code - the multi-agent architecture was documented but never implemented.

## Implementation Strategy

### Phase 1: Analysis & Setup (1 hour)
- [x] Create implementation plan directory: `docs/development/implementation_plans/`
- [ ] Research ADK integration patterns using Context7
- [ ] Identify minimum viable agent structure for system startup

### Phase 2: Code Structure Setup (1 hour)
1. **Create agent module structure**:
   - `dime/agents/__init__.py` - Agent module initialization
   - `dime/agents/base.py` - Base agent classes and common functionality
   - `dime/agents/researcher.py` - Research agent implementation
   - `dime/agents/writer.py` - Writer agent implementation

2. **Fix syntax errors in publisher/agent.py**:
   - Line 9: Add missing comma after model parameter
   - Line 10: Remove stray backtick from agent name

### Phase 3: Minimal Agent Implementation (2-3 hours)
1. **Create ResearcherAgent class**:
   - Inherit from ADK LlmAgent
   - Research-focused instruction prompt
   - Basic tool set for content research

2. **Create WriterAgent class**:
   - Inherit from ADK LlmAgent
   - Article writing instruction prompt
   - Content formatting capabilities

3. **Update publisher/agent.py**:
   - Import the new agent classes
   - Replace undefined variables with proper instantiation
   - Maintain existing root_agent configuration

### Phase 4: Integration & Testing (1 hour)
1. **Create application entry point**: `dime/app.py` or `dime/main.py`
2. **Test system startup**: Verify `uv run python -m dime.app` works
3. **Validate ADK web interface**: Ensure http://localhost:8000 is accessible
4. **Test agent functionality**: Basic conversation through web interface

### Phase 5: Documentation & Validation (1 hour)
1. **Update CLAUDE.md**: Document new agent structure
2. **Create basic unit tests**: Agent instantiation and basic functionality
3. **Validate acceptance criteria**: All items from issue #002
4. **Run quality checks**: ruff linting, formatting, and type checking
5. **Commit changes**: Following project standards

## Technical Implementation Details

### Agent Architecture
```python
# Base agent structure
from google.adk.agents import LlmAgent

class ResearcherAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="researcher",
            model="gemini-2.5-flash",
            instruction="Research specialist for political liberation movements..."
        )

class WriterAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="writer",
            model="gemini-2.5-flash",
            instruction="Content writer for accessible political history articles..."
        )
```

### File Structure Changes
```
dime/
├── agents/                   # NEW: Agent implementations
│   ├── __init__.py          # Agent module exports
│   ├── base.py              # Common agent functionality
│   ├── researcher.py        # Research agent
│   └── writer.py            # Writer agent
├── app.py                   # NEW: Application entry point
└── main.py                  # NEW: Alternative entry point
```

### Updated publisher/agent.py
```python
from google.adk.agents import SequentialAgent, LlmAgent
from dime.agents import ResearcherAgent, WriterAgent

# Fix syntax errors and add proper agent instantiation
researcher = ResearcherAgent()
writer = WriterAgent()

# Keep existing root_agent logic with fixed references
root_agent = SequentialAgent(
    # ... existing configuration ...
    sub_agents=[researcher, writer],  # Now properly defined
)
```

## Success Criteria

### Acceptance Criteria (from Issue #002)
- [ ] System starts without NameError exceptions
- [ ] At least one working ADK agent is implemented
- [ ] Basic agent conversation works through ADK web interface
- [ ] Agent health checks return positive status
- [ ] All imports resolve correctly

### Quality Standards
- [ ] Code passes `ruff check .` with zero errors
- [ ] Code passes `ruff format --check .` with zero issues
- [ ] Type hints added for all new functions/classes
- [ ] Unit tests created for agent instantiation
- [ ] Documentation updated to reflect changes

### Functional Validation
- [ ] `uv run python -m dime.app` executes without errors
- [ ] ADK web interface accessible at http://localhost:8000
- [ ] Can send message and receive response through web interface
- [ ] Agent health endpoints return 200 status
- [ ] No runtime exceptions in agent instantiation

## Risk Mitigation

### Technical Risks
- **ADK Integration Complexity**: Start with minimal viable agents, expand incrementally
- **Import Resolution**: Test imports at each step before proceeding
- **Agent Configuration**: Keep existing publisher logic intact where possible

### Quality Risks
- **Testing Gaps**: Create unit tests alongside implementation
- **Documentation Drift**: Update docs immediately after code changes
- **Regression Issues**: Test system startup after each major change

### Timeline Risks
- **ADK Learning Curve**: Allocate extra time for ADK pattern research
- **Debugging Time**: Plan for troubleshooting import and instantiation issues

## Dependencies

### External Dependencies
- google-adk library (already configured)
- Python 3.13+ environment (already setup)
- uv package manager (already installed)

### Internal Dependencies
- Pydantic Settings system (already implemented)
- Environment configuration (already working)
- Project structure (partially complete)

## Validation Plan

### Testing Strategy
1. **Unit Tests**: Agent instantiation and basic functionality
2. **Integration Tests**: ADK web interface and agent communication
3. **System Tests**: Full application startup and health checks
4. **Manual Tests**: Interactive agent conversations

### Quality Checks
1. **Code Quality**: Run ruff linting and formatting
2. **Type Safety**: Add type hints and run type checking
3. **Import Resolution**: Verify all imports work correctly
4. **Performance**: Ensure startup time <10 seconds

## Post-Implementation Tasks

### Immediate Follow-up
- Monitor system stability after deployment
- Gather feedback on agent conversation quality
- Document any additional ADK patterns discovered

### Future Enhancements
- Implement remaining 5 agents from 7-stage pipeline
- Add agent-specific tools and capabilities
- Enhance error handling and logging
- Add agent performance metrics

## Notes

### Implementation Decisions
- **Minimal Viable Product**: Focus on resolving NameError first
- **Incremental Approach**: Build complexity gradually
- **Existing Logic Preservation**: Keep publisher/agent.py structure intact
- **Standard Compliance**: Follow all project coding guidelines

### Lessons Learned
- Document lessons learned during implementation
- Note any ADK patterns that work particularly well
- Identify areas for improvement in future agent development

---

**Implementation Date**: 2024-09-13
**Assignee**: Claude Code
**Reviewer**: N/A (Individual development)
**Status**: In Progress