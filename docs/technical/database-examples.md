# Database Usage Examples

This document provides practical examples of how to use the dime content creation database models and utilities.

## Table of Contents
- [Basic Setup](#basic-setup)
- [Creating Models](#creating-models)
- [Querying Data](#querying-data)
- [Advanced Operations](#advanced-operations)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Basic Setup

### Database Connection


### Environment Configuration

Set up your `.envrc` file:

```bash
# PostgreSQL Database Configuration
export DATABASE_URL="postgresql+asyncpg://username:password@localhost:5432/dime_dev"

# Optional: Override individual components
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_USER="dime"
export DB_PASSWORD="password"
export DB_NAME="dime_dev"
```

## Creating Models

### Managing Processing Jobs

```python
from dime.database.models import ProcessingJob, JobType, JobStatus

async def create_and_manage_job(content_id):
    async with get_async_session() as session:
        # Create a new job
        job = ProcessingJob(
            content_id=content_id,
            job_type=JobType.CREATE_CONTENT,
            status=JobStatus.PENDING,
            progress=0
        )
        
        session.add(job)
        await session.commit()
        
        # Start processing
        job.start_processing()
        print(f"Job started at: {job.started_at}")
        
        # Simulate progress updates
        job.progress = 50
        await session.commit()
        
        try:
            # Simulate successful completion
            job.complete_successfully()
            print(f"Job completed at: {job.completed_at}")
        except Exception as e:
            # Handle failure
            job.fail_with_error(str(e))
            print(f"Job failed: {job.error_message}")
        
        await session.commit()
        return job.id
```

## Querying Data

### Connection Pooling

```python
from dime.database.connection import get_async_engine

async def custom_engine_setup():
    # Create engine with custom pool settings
    engine = get_async_engine(
        pool_size=20,           # Connection pool size
        max_overflow=30,        # Additional connections beyond pool_size
        pool_timeout=30,        # Seconds to wait for connection
        pool_recycle=3600,      # Recycle connections after 1 hour
        pool_pre_ping=True      # Validate connections before use
    )
    
    return engine
```

## Error Handling

### Connection Errors

```python
from sqlalchemy.exc import OperationalError, TimeoutError
from asyncpg.exceptions import ConnectionDoesNotExistError

async def robust_database_operation():
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            async with get_async_session() as session:
                # Your database operation
                result = await session.execute(select(Content))
                content = result.scalars().all()
                return content
                
        except (OperationalError, ConnectionDoesNotExistError, TimeoutError) as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
            else:
                print(f"Database operation failed after {max_retries} attempts")
                raise
```

### Model Validation


## Best Practices

### 1. Always Use Context Managers

```python
# ✅ Good: Automatic session cleanup
async with get_async_session() as session:
    # Operations
    pass

# ❌ Bad: Manual session management
session = get_async_session_factory()()
# Operations
await session.close()
```

### 2. Batch Database Operations


### 3. Use Proper Indexing


### 4. Handle Timezone Properly

```python
from datetime import datetime, timezone

# ✅ Good: Use timezone-aware datetime
published_at = datetime.now(timezone.utc)

# ❌ Bad: Naive datetime
published_at = datetime.now()
```

### 5. Monitor Database Performance

## Testing Your Database Code


This documentation provides comprehensive examples for using the database models and utilities in your dime content creation system. Remember to always use async/await patterns and proper error handling in production code.
