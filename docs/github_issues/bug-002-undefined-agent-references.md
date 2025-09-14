# [BUG] Fix undefined agent references in publisher/agent.py

## Bug Description
The current agent implementation in `publisher/agent.py` contains undefined variable references that cause runtime errors. The code references `researcher` and `writer` agents in the SequentialAgent configuration, but these variables are never defined, causing a NameError when the module is imported or executed.

## Steps to Reproduce
1. Navigate to project root: `cd /home/vance/projects/ActsOfDefiance/dime`
2. Try to import the agent module: `uv run python -c "from publisher.agent import root_agent"`
3. Observe NameError for undefined `researcher` and `writer` variables

## Expected Behavior
- Agent module should import without errors
- SequentialAgent should be properly configured with valid sub-agents
- Agent system should initialize and be ready for content creation workflows

## Actual Behavior
- Python raises NameError: name 'researcher' is not defined
- Python raises NameError: name 'writer' is not defined
- Agent system cannot start, blocking all functionality
- Application startup fails completely

## Environment
- OS: Linux
- Python version: 3.13
- Dime version: v0.1.0
- Google ADK version: >=1.9.0
- Package manager: uv

## Code Analysis
Current problematic code in `publisher/agent.py` lines 32-33:
```python
sub_agents=[researcher, writer],  # These variables are undefined
```

Defined agents in the same file:
```python
author = LlmAgent(  # This is defined but not used
    model="gemini-2.5-pro-preview-03-25",
    name="researcher",  # Name mismatch: defined as 'author' but named 'researcher'
    # ...
)
```

## Root Cause Analysis
1. **Variable naming inconsistency**: Agent is defined as `author` but named as `researcher`
2. **Missing agent definitions**: `writer` agent is referenced but never defined
3. **Configuration mismatch**: SequentialAgent references agents that don't exist in scope
4. **Incomplete multi-agent setup**: Only one agent is partially implemented

## Proposed Solution
1. **Fix immediate naming issues**:
   - Rename `author` variable to `researcher` to match its internal name
   - Create missing `writer` agent definition

2. **Implement proper multi-agent architecture**:
   - Define distinct `researcher` agent for content research
   - Define distinct `writer` agent for content creation
   - Configure SequentialAgent with proper agent references

3. **Add error handling and validation**:
   - Validate agent initialization
   - Add proper error handling for agent startup failures
   - Include agent health checks

## Acceptance Criteria
- [ ] Agent module imports without errors
- [ ] All referenced agents (`researcher`, `writer`) are properly defined
- [ ] SequentialAgent initializes successfully with sub-agents
- [ ] Agent names and variable names are consistent
- [ ] Basic agent functionality can be tested: `uv run python -c "from publisher.agent import root_agent; print(root_agent.name)"`
- [ ] No runtime errors when starting agent system
- [ ] Proper error handling for agent initialization failures

## Technical Implementation Requirements
- **Agent Architecture**: Follow Google ADK patterns for multi-agent systems
- **Error Handling**: Graceful failure with descriptive error messages
- **Configuration**: Use environment variables for model selection and agent settings
- **Testing**: Unit tests to verify agent initialization and configuration
- **Documentation**: Update agent configuration documentation

## Testing Requirements
- Unit tests for agent initialization
- Integration tests for multi-agent communication
- Error scenario testing (invalid configurations, missing models)
- Agent health check functionality

## Definition of Done
- [ ] Code changes implemented and tested
- [ ] All unit tests pass
- [ ] Agent system starts without errors
- [ ] Integration tests confirm multi-agent functionality
- [ ] Code reviewed and approved
- [ ] Documentation updated with correct agent configuration
- [ ] Changes merged to main branch

## Priority Assessment
**🔴 P0 - Critical**: This bug completely blocks system functionality and prevents any development or testing progress.

## Time Estimate
- **Investigation**: 2 hours (completed during ticket creation)
- **Implementation**: 4-6 hours for proper multi-agent setup
- **Testing**: 2-3 hours for comprehensive test coverage
- **Documentation**: 1 hour for updates
- **Total**: 1-2 days for complete resolution

## Dependencies
- Google ADK library documentation for proper agent patterns
- Environment configuration for agent model selection
- Testing framework setup (related to #003)

## Labels
- 🐛 bug
- 🤖 agent
- 🔴 P0 - Critical

## Milestone
Phase 0: Foundation Fix

## Parent Epic
#001 - [EPIC] Fix current implementation and establish working baseline

## Additional Context
This issue was discovered during initial codebase analysis and prevents any meaningful development or testing. The fix should follow established ADK patterns and prepare the agent system for the full multi-agent content pipeline described in the project documentation.