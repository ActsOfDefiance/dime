# Logfire Configuration Guide

This document provides comprehensive guidance for configuring and using Pydantic Logfire in the Dime project.

## Overview

Logfire provides structured logging and observability for the Dime application with automatic instrumentation for FastAPI, SQLAlchemy, and custom agent operations.

## Installation

Logfire is included in the project dependencies with FastAPI and SQLAlchemy instrumentation:

```toml
# pyproject.toml
dependencies = [
    "logfire[fastapi,sqlalchemy]>=0.20.0",
    # other dependencies...
]
```

## Environment Configuration

Configure Logfire using environment variables in your `.env` file:

```bash
# Logfire Configuration
LOGFIRE_TOKEN=your-logfire-token
LOGFIRE_PROJECT_NAME=dime-development
LOGFIRE_ENVIRONMENT=development
LOGFIRE_SERVICE_NAME=dime-app
```

### Environment-Specific Settings

**Development:**
```bash
LOGFIRE_ENVIRONMENT=development
LOGFIRE_SERVICE_NAME=dime-app-dev
LOG_LEVEL=DEBUG
```

**Production:**
```bash
LOGFIRE_ENVIRONMENT=production
LOGFIRE_SERVICE_NAME=dime-app-prod
LOG_LEVEL=INFO
```

## Application Setup

### Basic Configuration

```python
# dime/config/logging.py
import os
import logfire
from pydantic import BaseModel

class LogfireConfig(BaseModel):
    token: str = os.getenv("LOGFIRE_TOKEN", "")
    project_name: str = os.getenv("LOGFIRE_PROJECT_NAME", "dime")
    environment: str = os.getenv("LOGFIRE_ENVIRONMENT", "development")
    service_name: str = os.getenv("LOGFIRE_SERVICE_NAME", "dime-app")

def configure_logfire():
    """Configure Logfire for the application."""
    config = LogfireConfig()

    if not config.token:
        logfire.configure(send_to_logfire=False)  # Development mode
        logfire.info("Logfire configured in development mode (no token)")
    else:
        logfire.configure(
            token=config.token,
            project_name=config.project_name,
            environment=config.environment,
            service_name=config.service_name,
        )
        logfire.info("Logfire configured for production",
                    project=config.project_name,
                    environment=config.environment)
```

### FastAPI Integration

```python
# dime/main.py
import logfire
from fastapi import FastAPI
from dime.config.logging import configure_logfire

def create_app() -> FastAPI:
    """Create and configure FastAPI application with Logfire."""

    # Configure Logfire first
    configure_logfire()

    # Create FastAPI app
    app = FastAPI(title="Dime Content Creation System")

    # Instrument FastAPI with Logfire
    logfire.instrument_fastapi(app)

    # Add custom middleware for request context
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        request_id = str(uuid.uuid4())

        with logfire.span("http_request") as span:
            span.set_attribute("request.id", request_id)
            span.set_attribute("request.method", request.method)
            span.set_attribute("request.url", str(request.url))

            response = await call_next(request)

            span.set_attribute("response.status_code", response.status_code)
            return response

    return app
```

### SQLAlchemy Integration

```python
# dime/database/connection.py
import logfire
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Instrument SQLAlchemy
logfire.instrument_sqlalchemy()

async def get_database_session() -> AsyncSession:
    """Get database session with Logfire instrumentation."""
    engine = create_async_engine(DATABASE_URL)

    async with AsyncSession(engine) as session:
        with logfire.span("database_session"):
            yield session
```

## Agent Instrumentation

### ADK Agent Logging

```python
# dime/agents/base.py
import logfire
from typing import Dict, Any
from pydantic import BaseModel
from google.adk import Agent

class AgentResult(BaseModel):
    success: bool
    content: str
    metadata: Dict[str, Any] = {}
    processing_time: float

class BaseAgent:
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Process input with comprehensive logging."""

        with logfire.span("agent_processing") as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("agent.model", self.config.get("model"))
            span.set_attribute("input.size", len(str(input_data)))

            try:
                logfire.info("Agent processing started",
                           agent_name=self.name,
                           input_keys=list(input_data.keys()))

                start_time = time.time()
                result = await self._execute_processing(input_data)
                processing_time = time.time() - start_time

                span.set_attribute("processing.time_seconds", processing_time)
                span.set_attribute("result.success", result.success)
                span.set_attribute("output.size", len(result.content))

                logfire.info("Agent processing completed",
                           agent_name=self.name,
                           success=result.success,
                           processing_time=processing_time)

                return result

            except Exception as e:
                span.record_exception(e)
                logfire.error("Agent processing failed",
                            agent_name=self.name,
                            error=str(e),
                            exc_info=True)
                raise
```

### Multi-Agent Workflow Logging

```python
# dime/services/workflow.py
import logfire
from typing import List
from pydantic import BaseModel

class WorkflowStep(BaseModel):
    agent_name: str
    status: str
    duration: float
    success: bool

class WorkflowResult(BaseModel):
    workflow_id: str
    steps: List[WorkflowStep]
    total_duration: float
    success: bool

class ArticleWorkflowService:
    async def process_article(self, article_id: str, topic: str) -> WorkflowResult:
        """Process article through multi-agent workflow with detailed logging."""

        workflow_id = f"workflow_{article_id}_{int(time.time())}"

        with logfire.span("article_workflow") as workflow_span:
            workflow_span.set_attribute("workflow.id", workflow_id)
            workflow_span.set_attribute("article.id", article_id)
            workflow_span.set_attribute("article.topic", topic)

            logfire.info("Article workflow started",
                       workflow_id=workflow_id,
                       article_id=article_id,
                       topic=topic)

            steps = []
            start_time = time.time()

            try:
                # Research phase
                research_result = await self._execute_research_phase(topic, workflow_id)
                steps.append(research_result)

                # Writing phase
                writing_result = await self._execute_writing_phase(research_result.content, workflow_id)
                steps.append(writing_result)

                # Fact-checking phase
                factcheck_result = await self._execute_factcheck_phase(writing_result.content, workflow_id)
                steps.append(factcheck_result)

                total_duration = time.time() - start_time
                workflow_success = all(step.success for step in steps)

                workflow_span.set_attribute("workflow.total_duration", total_duration)
                workflow_span.set_attribute("workflow.success", workflow_success)
                workflow_span.set_attribute("workflow.steps_count", len(steps))

                logfire.info("Article workflow completed",
                           workflow_id=workflow_id,
                           success=workflow_success,
                           total_duration=total_duration,
                           steps_completed=len(steps))

                return WorkflowResult(
                    workflow_id=workflow_id,
                    steps=steps,
                    total_duration=total_duration,
                    success=workflow_success
                )

            except Exception as e:
                workflow_span.record_exception(e)
                logfire.error("Article workflow failed",
                            workflow_id=workflow_id,
                            error=str(e),
                            steps_completed=len(steps),
                            exc_info=True)
                raise
```

## API Endpoint Logging

### Enhanced Endpoint Logging

```python
# dime/api/articles.py
import logfire
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

class ArticleCreateRequest(BaseModel):
    topic: str
    priority: str = "normal"

router = APIRouter(prefix="/api/articles", tags=["articles"])

@router.post("/", response_model=ArticleResponse)
async def create_article(request: ArticleCreateRequest):
    """Create new article with comprehensive logging."""

    with logfire.span("api_create_article") as span:
        span.set_attribute("article.topic", request.topic)
        span.set_attribute("article.priority", request.priority)

        logfire.info("Article creation request received",
                   topic=request.topic,
                   priority=request.priority)

        try:
            # Validate request
            if not request.topic.strip():
                logfire.warning("Invalid article creation request",
                              reason="empty_topic")
                raise HTTPException(status_code=400, detail="Topic cannot be empty")

            # Create article
            article = await article_service.create_article(request.topic)

            span.set_attribute("article.id", article.id)
            span.set_attribute("article.status", article.status)

            logfire.info("Article created successfully",
                       article_id=article.id,
                       topic=request.topic,
                       status=article.status)

            return ArticleResponse.from_article(article)

        except HTTPException:
            raise
        except Exception as e:
            span.record_exception(e)
            logfire.error("Article creation failed",
                        topic=request.topic,
                        error=str(e),
                        exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
```

## Performance Monitoring

### Custom Metrics

```python
# dime/monitoring/metrics.py
import logfire
import time
from functools import wraps
from typing import Callable, Any

def track_performance(operation_name: str):
    """Decorator to track operation performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()

            with logfire.span(f"performance_{operation_name}") as span:
                span.set_attribute("operation.name", operation_name)

                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time

                    span.set_attribute("performance.duration", duration)
                    span.set_attribute("performance.success", True)

                    logfire.info("Performance metric recorded",
                               operation=operation_name,
                               duration=duration,
                               success=True)

                    return result

                except Exception as e:
                    duration = time.time() - start_time
                    span.record_exception(e)
                    span.set_attribute("performance.duration", duration)
                    span.set_attribute("performance.success", False)

                    logfire.error("Performance metric recorded with error",
                                operation=operation_name,
                                duration=duration,
                                success=False,
                                error=str(e))
                    raise

        return wrapper
    return decorator

# Usage example
@track_performance("agent_research")
async def research_topic(topic: str) -> str:
    # Research implementation
    pass
```

## Security & Compliance

### Sensitive Data Protection

```python
# dime/logging/security.py
import logfire
import re
from typing import Dict, Any

class SecureLogger:
    """Secure logger that sanitizes sensitive data."""

    SENSITIVE_PATTERNS = [
        r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'secret["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit cards
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    ]

    @classmethod
    def sanitize_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data from logging payload."""
        sanitized = {}

        for key, value in data.items():
            if isinstance(value, str):
                sanitized_value = cls._sanitize_string(value)
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_data(value)
            else:
                sanitized[key] = value

        return sanitized

    @classmethod
    def _sanitize_string(cls, text: str) -> str:
        """Sanitize sensitive patterns in text."""
        for pattern in cls.SENSITIVE_PATTERNS:
            text = re.sub(pattern, r'\1***REDACTED***', text, flags=re.IGNORECASE)
        return text

    @classmethod
    def secure_log(cls, level: str, message: str, **kwargs):
        """Log with automatic sensitive data sanitization."""
        sanitized_kwargs = cls.sanitize_data(kwargs)

        log_func = getattr(logfire, level.lower())
        log_func(message, **sanitized_kwargs)

# Usage
SecureLogger.secure_log("info", "User login attempt",
                       username="user@example.com",
                       password="secret123")  # Will be sanitized
```

## Testing Integration

### Test Logging

```python
# tests/conftest.py
import pytest
import logfire
from unittest.mock import patch

@pytest.fixture(autouse=True)
def configure_test_logging():
    """Configure Logfire for testing."""
    with patch('logfire.configure') as mock_configure:
        logfire.configure(send_to_logfire=False)
        yield

@pytest.fixture
def logfire_capture():
    """Capture Logfire logs during tests."""
    logs = []

    def capture_log(*args, **kwargs):
        logs.append({'args': args, 'kwargs': kwargs})

    with patch('logfire.info', side_effect=capture_log), \
         patch('logfire.error', side_effect=capture_log), \
         patch('logfire.warning', side_effect=capture_log):
        yield logs
```

## Best Practices

### Do's
- ✅ Use structured logging with Pydantic models
- ✅ Include relevant context (request_id, user_id, agent_name)
- ✅ Log performance metrics for all agent operations
- ✅ Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Instrument external service calls
- ✅ Sanitize sensitive data before logging
- ✅ Use spans for tracking operation boundaries
- ✅ Include error context and stack traces for exceptions

### Don'ts
- ❌ Log sensitive data (passwords, API keys, PII)
- ❌ Log large payloads without truncation
- ❌ Use only string concatenation for log messages
- ❌ Ignore logging performance impact
- ❌ Mix business logic with logging logic
- ❌ Use generic error messages without context
- ❌ Log at inappropriate levels (e.g., ERROR for warnings)
- ❌ Forget to test logging in unit tests

### Example Usage Patterns

```python
# Good: Structured logging with context
logfire.info("Agent processing started",
           agent_name="researcher",
           topic="climate change",
           model="gemini-2.5-pro",
           request_id="req_123")

# Bad: String concatenation without structure
logfire.info(f"Agent {agent_name} started processing {topic}")

# Good: Performance tracking with metrics
with logfire.span("database_query") as span:
    result = await db.execute(query)
    span.set_attribute("query.rows", len(result))

# Bad: No performance context
result = await db.execute(query)
```

## Troubleshooting

### Common Issues

1. **Missing Token**: Configure `LOGFIRE_TOKEN` or use development mode
2. **High Log Volume**: Adjust log levels and sampling rates
3. **Sensitive Data**: Use `SecureLogger` for automatic sanitization
4. **Performance Impact**: Monitor logging overhead and optimize
5. **Test Failures**: Use proper test fixtures and mocking

### Monitoring Logfire Health

```python
# Health check endpoint
@router.get("/health/logging")
async def logging_health():
    """Check logging system health."""
    try:
        logfire.info("Health check executed")
        return {"status": "healthy", "logging": "operational"}
    except Exception as e:
        logfire.error("Health check failed", error=str(e))
        return {"status": "unhealthy", "logging": "failed"}
```