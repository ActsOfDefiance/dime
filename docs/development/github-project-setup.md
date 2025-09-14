# GitHub Project Management Setup Guide

## Overview

This document provides a complete guide for setting up GitHub project management for the Dime content creation agent, including issues, milestones, project boards, and templates.

**Repository**: https://github.com/ActsOfDefiance/dime

## Project Structure Setup

### 1. GitHub Project Board Configuration

#### Main Project Board: "Dime Development"
**URL**: `https://github.com/ActsOfDefiance/dime/projects`

**Columns**:
- **📋 Backlog**: Planned issues not yet started
- **🔍 Ready**: Issues ready for development (requirements clarified)
- **🚧 In Progress**: Currently being worked on
- **👀 Review**: Completed, awaiting review/testing
- **✅ Done**: Completed and deployed

#### Board Automation:
- Issues automatically move to "In Progress" when assigned
- Pull requests move to "Review" when opened
- Issues move to "Done" when closed as completed

### 2. Milestones Setup

#### Phase 0: Foundation Fix
- **Due Date**: 2 weeks from project start
- **Description**: Fix current implementation issues and establish working baseline
- **Success Criteria**: Agent system runs without errors, basic CLI functional

#### Phase 1: MVP Agent System with ADK Web Interface
- **Due Date**: 6 weeks from project start
- **Description**: Complete content creation workflow with ADK web interface and CLI support
- **Success Criteria**: Research → Draft → Review → Publish workflow operational via ADK web UI, ADK development interface functional

#### Phase 2: Enhanced Web Application
- **Due Date**: 12 weeks from project start
- **Description**: Enhanced web application with custom UI, database persistence, and content management
- **Success Criteria**: Custom web application with content management, user authentication, advanced workflow controls

#### Phase 3: Advanced Features
- **Due Date**: 20 weeks from project start
- **Description**: Production-ready features and collaboration tools
- **Success Criteria**: Background processing, multi-user support

#### Phase 4: Production Deployment
- **Due Date**: 24 weeks from project start
- **Description**: Production deployment with monitoring
- **Success Criteria**: System running in production with >99% uptime

### 3. Issue Labels System

#### Type Labels
- **🐛 bug**: Something isn't working correctly
- **✨ feature**: New functionality or enhancement
- **📚 documentation**: Documentation improvements
- **🧪 testing**: Test-related issues
- **🔧 maintenance**: Code maintenance and refactoring
- **🚀 deployment**: Deployment and infrastructure

#### Priority Labels
- **🔴 P0 - Critical**: Blocking issues, must fix immediately
- **🟠 P1 - High**: Important features, should complete this phase
- **🟡 P2 - Medium**: Nice to have, could move to next phase
- **🟢 P3 - Low**: Future consideration, won't fix this phase

#### Component Labels
- **🤖 agent**: Agent system and AI integration
- **🌐 web**: Web interface and frontend
- **🗄️ database**: Database and data persistence
- **📝 content**: Content creation and management
- **🔍 research**: Research tools and capabilities
- **⚙️ infrastructure**: Deployment and DevOps

#### Status Labels
- **🚫 blocked**: Cannot proceed due to dependencies
- **❓ needs-info**: Requires additional information or clarification
- **👥 needs-review**: Ready for code/design review
- **🔄 in-progress**: Currently being worked on

### 4. Issue Templates

#### Bug Report Template
```markdown
---
name: Bug Report
about: Report a bug or issue with the system
title: '[BUG] Brief description of the issue'
labels: '🐛 bug'
assignees: ''
---

## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. See error

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
What actually happened instead.

## Environment
- OS: [e.g. macOS, Ubuntu 20.04]
- Python version: [e.g. 3.13]
- Dime version: [e.g. v0.1.0]

## Additional Context
Add any other context about the problem here.

## Screenshots
If applicable, add screenshots to help explain your problem.
```

#### Feature Request Template
```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] Brief description of the feature'
labels: '✨ feature'
assignees: ''
---

## Feature Description
A clear and concise description of the feature you'd like to see.

## Problem Statement
What problem does this feature solve? Why is it needed?

## Proposed Solution
Describe the solution you'd like to see implemented.

## User Stories
- As a [user type], I want [feature] so that [benefit]
- As a [user type], I want [feature] so that [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Considerations
Any technical details, constraints, or implementation thoughts.

## Alternatives Considered
Describe alternatives you've considered and why this approach is preferred.

## Additional Context
Add any other context, mockups, or examples about the feature request.
```

#### Epic Template
```markdown
---
name: Epic
about: Large feature or initiative spanning multiple issues
title: '[EPIC] Brief description of the epic'
labels: '✨ feature'
assignees: ''
---

## Epic Overview
High-level description of this epic and its goals.

## Business Value
Why is this epic important? What value does it provide?

## Success Criteria
- [ ] Measurable outcome 1
- [ ] Measurable outcome 2
- [ ] Measurable outcome 3

## User Stories
List of user stories that make up this epic:
- [ ] #[issue-number] - User story title
- [ ] #[issue-number] - User story title
- [ ] #[issue-number] - User story title

## Technical Requirements
High-level technical requirements and constraints.

## Dependencies
- [ ] Dependency 1
- [ ] Dependency 2

## Definition of Done
- [ ] All user stories completed
- [ ] Documentation updated
- [ ] Tests written and passing
- [ ] Code reviewed and merged
- [ ] Feature deployed to production

## Timeline
Expected start and completion dates.

## Resources
Team members, budget, or other resources required.
```

### 5. Initial Issue Creation

#### Phase 0 Issues

**Epic: Foundation Fix (#1)**
```
Title: [EPIC] Fix current implementation and establish working baseline
Labels: ✨ feature, 🤖 agent, 🔴 P0 - Critical
Milestone: Phase 0: Foundation Fix
```

**Fix Agent Implementation (#2)**
```
Title: [BUG] Fix undefined agent references in publisher/agent.py
Labels: 🐛 bug, 🤖 agent, 🔴 P0 - Critical
Milestone: Phase 0: Foundation Fix
Parent Epic: #1

Description: The current agent implementation references undefined 'researcher' and 'writer' agents, causing runtime errors.
```

**Add Testing Framework (#3)**
```
Title: [FEATURE] Set up pytest testing framework
Labels: ✨ feature, 🧪 testing, 🟠 P1 - High
Milestone: Phase 0: Foundation Fix
Parent Epic: #1
```

**Create CLI Interface (#4)**
```
Title: [FEATURE] Create basic CLI for content creation
Labels: ✨ feature, 📝 content, 🟠 P1 - High
Milestone: Phase 0: Foundation Fix
Parent Epic: #1
```

**Update Documentation (#5)**
```
Title: [MAINTENANCE] Align documentation with actual implementation
Labels: 🔧 maintenance, 📚 documentation, 🟡 P2 - Medium
Milestone: Phase 0: Foundation Fix
Parent Epic: #1
```

#### Phase 1 Issues Template

**Epic: MVP Agent System with ADK Web Interface (#6)**
```
Title: [EPIC] Create minimal viable content creation system with ADK web interface
Labels: ✨ feature, 🤖 agent, 🌐 web, 🔴 P0 - Critical
Milestone: Phase 1: MVP Agent System with ADK Web Interface
```

**ADK Web Interface Setup (#7)**
```
Title: [FEATURE] Set up ADK agent web interface and development UI
Labels: ✨ feature, 🌐 web, 🤖 agent, 🟠 P1 - High
Milestone: Phase 1: MVP Agent System with ADK Web Interface
Parent Epic: #6

Description: Configure and deploy the Google ADK web interface for interactive agent conversations, including the development UI for debugging and testing.
```

**Enhanced Research Agent (#8)**
```
Title: [FEATURE] Implement enhanced research capabilities
Labels: ✨ feature, 🔍 research, 🟠 P1 - High
Milestone: Phase 1: MVP Agent System with ADK Web Interface
Parent Epic: #6
```

### 6. Branch Protection Rules

#### Main Branch Protection
- Require pull request reviews before merging
- Require status checks to pass before merging
- Require up-to-date branches before merging
- Include administrators in these restrictions

#### Required Status Checks
- Tests pass (pytest)
- Linting passes (ruff check)
- Formatting passes (ruff format)
- Type checking passes (pyright)
- Documentation builds successfully

### 7. GitHub Actions Workflows

#### CI/CD Pipeline (.github/workflows/ci.yml)
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.13]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
    
    - name: Install dependencies
      run: uv sync
    
    - name: Run tests
      run: uv run pytest
    
    - name: Run linting
      run: uv run ruff check .

    - name: Run formatting check
      run: uv run ruff format --check .

    - name: Run type checking
      run: uv run pyright
```

### 8. Project Management Workflow

#### Daily Workflow
1. **Morning Standup** (if team): Review project board, discuss blockers
2. **Development**: Move issues to "In Progress", work on assigned tasks
3. **Code Review**: Create PR, move to "Review" column
4. **Testing**: Validate functionality, update tests
5. **Deployment**: Merge PR, move issue to "Done"

#### Weekly Workflow
1. **Sprint Planning**: Review backlog, assign issues to current sprint
2. **Backlog Grooming**: Update issue priorities, add new requirements
3. **Progress Review**: Update milestone progress, adjust timelines
4. **Documentation**: Update docs based on completed work

#### Release Workflow
1. **Feature Freeze**: No new features, bug fixes only
2. **Release Testing**: Comprehensive testing of all features
3. **Release Notes**: Document changes and new features
4. **Deployment**: Deploy to production, monitor for issues
5. **Post-Release**: Address any deployment issues, plan next iteration

### 9. Communication Guidelines

#### Issue Communication
- Use clear, descriptive titles with appropriate prefixes ([BUG], [FEATURE])
- Provide detailed descriptions with context and requirements
- Use @mentions for specific feedback or review requests
- Update issues regularly with progress and blockers

#### Pull Request Guidelines
- Link to related issues using "Closes #123" or "Fixes #123"
- Provide clear description of changes and testing performed
- Request specific reviewers for code and design review
- Update documentation as part of the PR when necessary

#### Project Updates
- Weekly progress updates on main project board
- Milestone reviews at phase boundaries
- Regular stakeholder communication on major decisions
- Documentation of architectural decisions and rationale

---

**Next Steps for Setup:**

1. Create GitHub project board with specified columns
2. Set up milestones with dates and descriptions
3. Create issue and PR templates in `.github/` directory
4. Configure branch protection rules for main branch
5. Set up GitHub Actions for CI/CD pipeline
6. Create initial issues for Phase 0 work
7. Assign team members to appropriate issues

**Maintenance:**
- Review and update labels monthly
- Archive completed milestones
- Update project board automation as needed
- Regularly backup project configuration and data