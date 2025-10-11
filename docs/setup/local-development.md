# Local Development Setup Guide

This guide will walk you through setting up the Dime Content Creation System for local development on your machine.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python 3.13 or higher**: [Download from python.org](https://www.python.org/downloads/)
- **uv**: Python package manager ([Installation Guide](https://github.com/astral-sh/uv#installation))
- **Git**: Version control system
- **direnv** (recommended): Automatic environment variable loading

### Required Accounts
- **Google Cloud Account**: For Google ADK API access
- **Google ADK API Key**: Get from [Google AI Studio](https://aistudio.google.com/)

### System Requirements
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 1GB for dependencies and virtual environment
- **Operating System**: Linux, macOS, or Windows (with WSL2)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/ActsOfDefiance/dime.git
cd dime
```

### 2. Install uv Package Manager

If you don't have `uv` installed:

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 3. Set Up Python Environment

```bash
# Install dependencies
uv sync

# Verify Python version
uv run python --version  # Should be 3.13 or higher
```

This command creates a virtual environment in `.venv/` and installs all required dependencies.

### 4. Configure Environment Variables

The application requires several environment variables for configuration. You'll need to create a `.envrc` file in the project root.

#### Create .envrc File

```bash
cat > .envrc << 'EOF'
# Database Configuration (required)
export DATABASE_URL="postgresql://user:password@localhost:5432/dime_dev"

# Google ADK Configuration (required)
export GOOGLE_ADK_PROJECT_ID="your-google-cloud-project-id"
export GOOGLE_ADK_API_KEY="your-google-adk-api-key"

# Authentication Configuration (required, but placeholders OK for development)
export AUTH_GOOGLE_OAUTH_CLIENT_ID="placeholder-for-development"
export AUTH_GOOGLE_OAUTH_CLIENT_SECRET="placeholder-for-development"
export AUTH_JWT_SECRET_KEY="dev-secret-key-change-in-production"

# Optional: Application Configuration
export APP_ENVIRONMENT="development"
export APP_DEBUG="true"
export APP_HOST="0.0.0.0"
export APP_PORT="8000"

# Optional: Logfire Configuration (for observability)
export LOGFIRE_TOKEN=""  # Leave empty to disable
export LOGFIRE_PROJECT_NAME="dime-development"
EOF
```

#### Update with Your Values

Edit `.envrc` and replace the placeholder values:
- `your-google-cloud-project-id`: Your Google Cloud project ID
- `your-google-adk-api-key`: Your API key from Google AI Studio
- `DATABASE_URL`: PostgreSQL connection string (placeholder OK for Phase 0)

#### Load Environment Variables

If using direnv:
```bash
direnv allow
```

If not using direnv:
```bash
source .envrc
```

**Note**: `.envrc` is git-ignored and should never be committed to version control.

### 5. Verify Configuration

Run the health check to verify your configuration:

```bash
uv run python -m dime health
```

You should see output similar to:
```
✅ Configuration loaded successfully
📁 Database: postgresql://user:***@localhost:5432/dime_dev
🤖 Agent: dime_agent
🌍 Environment: development
```

If you see errors, check that:
- All required environment variables are set
- Your Google ADK API key is valid
- Database URL is properly formatted

### 6. Start the Application

```bash
# Start with default settings (localhost:8000)
uv run python -m dime start

# Or with custom host/port
uv run python -m dime start --host 127.0.0.1 --port 3000
```

The server will start and you should see:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 7. Access the Application

Open your browser and navigate to:

- **Main ADK Web Interface**: http://localhost:8000/
- **Developer Tools**: http://localhost:8000/dev-ui/

You can now interact with the agents through the web interface!

## Running Tests

The project includes a comprehensive test suite with 93% code coverage.

### Run All Tests
```bash
uv run pytest
```

### Run with Coverage Report
```bash
uv run pytest --cov
```

### Run with Verbose Output
```bash
uv run pytest -v
```

### Run Specific Test File
```bash
uv run pytest tests/test_config.py
```

### Generate HTML Coverage Report
```bash
uv run pytest --cov --cov-report=html
# Open htmlcov/index.html in your browser
```

### Expected Output
```
============================= test session starts ==============================
...
tests/test_agents.py::test_research_topic_tool PASSED                    [  5%]
tests/test_agents.py::test_write_content_tool PASSED                     [ 10%]
...
======================== 20 passed, 1 warning in 2.33s =========================

Name                            Stmts   Miss  Cover
-------------------------------------------------------------
agents/dime_agent/__init__.py       0      0   100%
agents/dime_agent/agent.py          9      0   100%
dime/__init__.py                    1      0   100%
dime/__main__.py                   21      1    95%
dime/app.py                        12      0   100%
dime/config/__init__.py             2      0   100%
dime/config/settings.py           122     21    83%
-------------------------------------------------------------
TOTAL                             167     22    87%
```

## Code Quality Checks

### Format Code
```bash
uv run ruff format .
```

### Lint Code
```bash
uv run ruff check .
```

### Auto-fix Linting Issues
```bash
uv run ruff check --fix .
```

### Check Formatting (without changing files)
```bash
uv run ruff format --check .
```

## Development Workflow

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
3. **Run tests**:
   ```bash
   uv run pytest
   ```

4. **Format and lint**:
   ```bash
   uv run ruff format .
   uv run ruff check --fix .
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   ```

6. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Troubleshooting

### Common Issues

#### Issue: "ModuleNotFoundError: No module named 'dime'"
**Solution**: Make sure you're running commands with `uv run`:
```bash
uv run python -m dime health  # Correct
python -m dime health          # Wrong - don't use python directly
```

#### Issue: "Configuration validation failed: DATABASE_URL is required"
**Solution**: Ensure your `.envrc` file exists and is loaded:
```bash
# Check if environment variables are set
echo $DATABASE_URL

# If empty, load .envrc
source .envrc  # or: direnv allow
```

#### Issue: "Configuration validation failed: GOOGLE_ADK_API_KEY is required"
**Solution**: Make sure you've set your Google ADK API key in `.envrc`:
```bash
export GOOGLE_ADK_API_KEY="your-actual-api-key"
source .envrc
```

#### Issue: Port 8000 already in use
**Solution**: Use a different port:
```bash
uv run python -m dime start --port 3000
```

#### Issue: Tests failing
**Solution**: Ensure your environment is properly set up:
```bash
# Reinstall dependencies
uv sync

# Clear any cached files
rm -rf .pytest_cache __pycache__

# Run tests again
uv run pytest
```

### Getting Help

If you encounter issues not covered here:

1. Check the [CLAUDE.md](../../CLAUDE.md) development guide
2. Review the [Project Structure](../development/project-structure.md) documentation
3. Check existing [GitHub Issues](https://github.com/ActsOfDefiance/dime/issues)
4. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Your environment details (OS, Python version, etc.)
   - Error messages or logs

## Next Steps

Once you have the development environment running:

1. **Explore the Code**: Start with `dime/__main__.py` and `dime/app.py`
2. **Read CLAUDE.md**: Comprehensive development guide
3. **Review Tests**: Check `tests/` directory for examples
4. **Try the Web Interface**: Experiment with agent conversations at http://localhost:8000
5. **Review Issues**: Check [GitHub Issues](../../docs/github_issues/) for tasks to work on

## Additional Resources

- **[CLAUDE.md](../../CLAUDE.md)**: AI-assisted development guide
- **[Project Structure](../development/project-structure.md)**: Codebase organization
- **[Technical Requirements](../development/technical-requirements.md)**: System specifications
- **[API Reference](../technical/api-reference.md)**: API documentation
- **[Google ADK Documentation](https://ai.google.dev/adk)**: Official ADK docs

---

**Last Updated**: 2025-01-30
**Document Owner**: Development Team
**Status**: Phase 0 Complete
