# Lesson 15: Building a RESTful API for Remote Access

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Designing a RESTful API Architecture](#designing-a-restful-api-architecture)
4. [Implementing API Endpoints using FastAPI](#implementing-api-endpoints-using-fastapi)
5. [Creating an Authentication and Authorization System](#creating-an-authentication-and-authorization-system)
6. [Developing Rate Limiting and Throttling](#developing-rate-limiting-and-throttling)
7. [Implementing API Versioning](#implementing-api-versioning)
8. [Practical Exercise](#practical-exercise)
9. [Conclusion and Further Reading](#conclusion-and-further-reading)

## 1. Introduction

In this lesson, we'll extend our AI-assisted coding tool by building a RESTful API for remote access. This will allow developers to interact with our tool programmatically, opening up possibilities for integration with other services and creating web-based interfaces.

We'll use FastAPI, a modern, fast (high-performance) Python web framework for building APIs. FastAPI is based on Pydantic and type hints, which makes it easy to build APIs with Python 3.6+ that have automatic validation, serialization, and documentation.

By the end of this lesson, you'll have a fully functional RESTful API that provides remote access to the core features of our AI-assisted coding tool.

## 2. Project Structure

Before we dive into the implementation, let's look at the project structure we'll be working with:

```
aider/
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── files.py
│   │   └── ai_operations.py
│   ├── dependencies.py
│   └── core/
│       ├── __init__.py
│       ├── config.py
│       ├── security.py
│       └── rate_limiter.py
│
├── cli/
│   └── ... (existing CLI code)
│
├── ai/
│   └── ... (existing AI integration code)
│
├── utils/
│   └── ... (existing utility functions)
│
├── tests/
│   └── api/
│       ├── test_main.py
│       └── test_routes/
│           ├── test_auth.py
│           ├── test_files.py
│           └── test_ai_operations.py
│
├── requirements.txt
└── main.py
```

This structure separates our API-related code into its own directory, keeping it modular and easy to maintain.

## 3. Designing a RESTful API Architecture

When designing our RESTful API, we'll follow these principles:

1. Use HTTP methods appropriately (GET, POST, PUT, DELETE)
2. Use meaningful URLs and resource names
3. Implement proper status codes
4. Provide consistent error handling
5. Use JSON for data exchange

Let's define our main resources and their corresponding endpoints:

1. Authentication
   - POST /api/v1/auth/token (Login and get access token)
   - POST /api/v1/auth/refresh (Refresh access token)

2. Files
   - GET /api/v1/files (List files)
   - POST /api/v1/files (Add a new file)
   - GET /api/v1/files/{file_id} (Get file content)
   - PUT /api/v1/files/{file_id} (Update file content)
   - DELETE /api/v1/files/{file_id} (Delete a file)

3. AI Operations
   - POST /api/v1/ai/complete (Get code completion)
   - POST /api/v1/ai/explain (Get code explanation)
   - POST /api/v1/ai/refactor (Get refactoring suggestions)

Now, let's implement these endpoints using FastAPI.

## 4. Implementing API Endpoints using FastAPI

First, let's set up our main FastAPI application in `api/main.py`:

```python
from fastapi import FastAPI
from api.routes import auth, files, ai_operations
from api.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="AI-assisted coding tool API",
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(ai_operations.router, prefix="/api/v1/ai", tags=["ai-operations"])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI-assisted coding tool API"}
```

Now, let's implement the routes for each resource. We'll start with the authentication routes in `api/routes/auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from api.core.security import create_access_token, get_current_user
from api.models import Token, User

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(data={"sub": current_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

Next, let's implement the file operations in `api/routes/files.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from api.core.security import get_current_user
from api.models import User, File, FileContent

router = APIRouter()

@router.get("/", response_model=list[File])
async def list_files(current_user: User = Depends(get_current_user)):
    # Implementation to list files
    pass

@router.post("/", response_model=File)
async def add_file(file: FileContent, current_user: User = Depends(get_current_user)):
    # Implementation to add a new file
    pass

@router.get("/{file_id}", response_model=FileContent)
async def get_file(file_id: int, current_user: User = Depends(get_current_user)):
    # Implementation to get file content
    pass

@router.put("/{file_id}", response_model=File)
async def update_file(file_id: int, file: FileContent, current_user: User = Depends(get_current_user)):
    # Implementation to update file content
    pass

@router.delete("/{file_id}")
async def delete_file(file_id: int, current_user: User = Depends(get_current_user)):
    # Implementation to delete a file
    pass
```

Finally, let's implement the AI operations in `api/routes/ai_operations.py`:

```python
from fastapi import APIRouter, Depends
from api.core.security import get_current_user
from api.models import User, CodeCompletion, CodeExplanation, RefactoringSuggestion

router = APIRouter()

@router.post("/complete", response_model=CodeCompletion)
async def complete_code(code: str, current_user: User = Depends(get_current_user)):
    # Implementation for code completion
    pass

@router.post("/explain", response_model=CodeExplanation)
async def explain_code(code: str, current_user: User = Depends(get_current_user)):
    # Implementation for code explanation
    pass

@router.post("/refactor", response_model=RefactoringSuggestion)
async def suggest_refactoring(code: str, current_user: User = Depends(get_current_user)):
    # Implementation for refactoring suggestions
    pass
```

## 5. Creating an Authentication and Authorization System

For our authentication system, we'll use JWT (JSON Web Tokens). Let's implement the necessary functions in `api/core/security.py`:

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from api.core.config import settings
from api.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user
```

## 6. Developing Rate Limiting and Throttling

To prevent abuse of our API, we'll implement rate limiting. We'll use the `slowapi` library, which integrates well with FastAPI. First, install it:

```
pip install slowapi
```

Now, let's implement rate limiting in `api/core/rate_limiter.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

Then, apply rate limiting to our main FastAPI app in `api/main.py`:

```python
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from api.core.rate_limiter import limiter

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

Now, we can apply rate limiting to specific routes. For example, in `api/routes/ai_operations.py`:

```python
from fastapi import APIRouter, Depends
from api.core.security import get_current_user
from api.core.rate_limiter import limiter
from api.models import User, CodeCompletion

router = APIRouter()

@router.post("/complete", response_model=CodeCompletion)
@limiter.limit("5/minute")
async def complete_code(code: str, current_user: User = Depends(get_current_user)):
    # Implementation for code completion
    pass
```

This limits the `/complete` endpoint to 5 requests per minute per user.

## 7. Implementing API Versioning

We've already implemented basic versioning by including `v1` in our API routes. To make this more flexible, let's create a version prefix in `api/core/config.py`:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-assisted Coding Tool API"
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    # ... other settings

settings = Settings()
```

Now, update `api/main.py` to use this prefix:

```python
from fastapi import FastAPI
from api.routes import auth, files, ai_operations
from api.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
)

app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["authentication"])
app.include_router(files.router, prefix=f"{settings.API_PREFIX}/files", tags=["files"])
app.include_router(ai_operations.router, prefix=f"{settings.API_PREFIX}/ai", tags=["ai-operations"])
```

This approach makes it easy to introduce new API versions in the future by creating new route modules and updating the `API_VERSION` setting.

## 8. Practical Exercise

Now that we've covered the main components of our RESTful API, let's put it all together in a practical exercise.

Exercise: Implement a simple code completion endpoint

1. Update `api/models.py` to include a `CodeCompletionRequest` and `CodeCompletionResponse`:

```python
from pydantic import BaseModel

class CodeCompletionRequest(BaseModel):
    code: str
    language: str

class CodeCompletionResponse(BaseModel):
    completion: str
```

2. Modify the `complete_code` function in `api/routes/ai_operations.py`:

```python
from fastapi import APIRouter, Depends
from api.core.security import get_current_user
from api.core.rate_limiter import limiter
from api.models import User, CodeCompletionRequest, CodeCompletionResponse
from ai.code_completion import get_code_completion  # Assume this function exists in our AI module

router = APIRouter()

@router.post("/complete", response_model=CodeCompletionResponse)
@limiter.limit("5/minute")
async def complete_code(
    request: CodeCompletionRequest,
    current_user: User = Depends(get_current_user)
):
    completion = get_code_completion(request.code, request.language)
    return CodeCompletionResponse(completion=completion)
```

3. Implement a mock `get_code_completion` function in `ai/code_completion.py`:

```python
def get_code_completion(code: str, language: str) -> str:
    # In a real implementation, this would call our AI model
    return f"Completed code for {language}: {code}... [AI-generated completion]"
```

4. Run your FastAPI application:

```
uvicorn api.main:app --reload
```

5. Test your API using curl or a tool like Postman:

```
curl -X POST "http://localhost:8000/api/v1/ai/complete" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{"code": "def hello_world():", "language": "python"}'
```

This exercise demonstrates how to implement a basic endpoint that integrates with our AI-assisted coding features, while also incorporating authentication and rate limiting.

## 9. Conclusion and Further Reading

In this lesson, we've built a RESTful API for our AI-assisted coding tool using FastAPI. We've covered:

1. Designing a RESTful API architecture
2. Implementing API endpoints with FastAPI
3. Creating an authentication and authorization system using JWT
4. Developing rate limiting and throttling to prevent abuse
5. Implementing API versioning for future extensibility

To further improve your API, consider exploring these topics:

1. API documentation using Swagger UI (built-in with FastAPI)
2. Implementing CORS (Cross-Origin Resource Sharing) for web clients
3. Adding request validation and error handling
4. Implementing database integration (e.g., with SQLAlchemy)
5. Setting up automated testing for your API endpoints
6. Implementing caching strategies for improved performance
7. Exploring asynchronous background tasks for long-running operations

Further reading:

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [RESTful API Design: Best Practices](https://swagger.io/resources/articles/best-practices-in-api-design/)
- [JSON Web Tokens (JWT) Introduction](https://jwt.io/introduction)
- [API Security Best Practices](https://www.apiopscycle.com/api-security-best-practices/)

## 10. Advanced Topics

Now that we have covered the basics of building a RESTful API for our AI-assisted coding tool, let's explore some advanced topics that can enhance the functionality and robustness of our API.

### 10.1 Implementing Websockets for Real-time Updates

FastAPI supports WebSockets, which can be useful for providing real-time updates to clients, such as streaming code completions or live collaboration features.

Add the following to `api/routes/websockets.py`:

```python
from fastapi import APIRouter, WebSocket, Depends
from api.core.security import get_current_user_ws

router = APIRouter()

@router.websocket("/ws/code-completion")
async def websocket_code_completion(websocket: WebSocket, current_user: dict = Depends(get_current_user_ws)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process the received code and generate completion
            completion = f"Real-time completion for: {data}"
            await websocket.send_text(completion)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
```

Update `api/main.py` to include the WebSocket route:

```python
from api.routes import websockets

app.include_router(websockets.router, tags=["websockets"])
```

### 10.2 Implementing a Caching Layer

To improve performance, especially for frequently accessed resources, we can implement a caching layer using Redis. First, install the required packages:

```
pip install redis fastapi-cache2
```

Add the following to `api/core/cache.py`:

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

async def setup_cache():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

Update `api/main.py` to initialize the cache:

```python
from fastapi import FastAPI
from api.core.cache import setup_cache

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await setup_cache()

# ... rest of your FastAPI setup
```

Now you can use caching decorators in your route handlers:

```python
from fastapi_cache.decorator import cache

@router.get("/files", response_model=List[File])
@cache(expire=60)
async def list_files(current_user: User = Depends(get_current_user)):
    # Implementation to list files
    pass
```

### 10.3 Implementing Background Tasks

For long-running operations, it's often better to handle them as background tasks. FastAPI provides a simple way to do this using the `BackgroundTasks` class.

Add the following to `api/routes/ai_operations.py`:

```python
from fastapi import BackgroundTasks

def run_long_code_analysis(code: str, user_id: int):
    # Simulate a long-running task
    time.sleep(10)
    # Perform analysis and store results
    result = f"Analysis complete for code: {code[:20]}..."
    store_analysis_result(user_id, result)

@router.post("/analyze")
async def analyze_code(
    code: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    background_tasks.add_task(run_long_code_analysis, code, current_user.id)
    return {"message": "Analysis started in the background"}
```

### 10.4 API Documentation with Swagger UI and ReDoc

FastAPI automatically generates interactive API documentation using Swagger UI and ReDoc. To customize the documentation, you can add more details to your route handlers and models:

```python
from fastapi import APIRouter, Depends, HTTPException
from api.models import User, CodeCompletion

router = APIRouter()

@router.post("/complete", response_model=CodeCompletion, 
             summary="Get code completion",
             description="This endpoint provides AI-powered code completion based on the input code snippet.")
async def complete_code(
    code: str = Body(..., example="def factorial(n):"),
    language: str = Body(..., example="python"),
    current_user: User = Depends(get_current_user)
):
    """
    Complete the given code snippet.

    - **code**: The incomplete code snippet
    - **language**: The programming language of the code snippet
    """
    # Implementation for code completion
    pass
```

### 10.5 API Versioning with APIRouter

To make API versioning even more flexible, you can use APIRouter for each version:

```python
# api/v1/routes/__init__.py
from fastapi import APIRouter

router = APIRouter()

from .auth import router as auth_router
from .files import router as files_router
from .ai_operations import router as ai_operations_router

router.include_router(auth_router, prefix="/auth", tags=["authentication"])
router.include_router(files_router, prefix="/files", tags=["files"])
router.include_router(ai_operations_router, prefix="/ai", tags=["ai-operations"])

# api/v2/routes/__init__.py
from fastapi import APIRouter

router = APIRouter()

# Include new or updated route modules for v2

# api/main.py
from fastapi import FastAPI
from api.v1.routes import router as v1_router
from api.v2.routes import router as v2_router

app = FastAPI()

app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
```

This structure allows you to maintain multiple API versions simultaneously, making it easier to introduce breaking changes while supporting older clients.

## 11. Final Project Structure

After implementing these advanced features, your project structure might look like this:

```
aider/
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── v1/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── files.py
│   │       ├── ai_operations.py
│   │       └── websockets.py
│   ├── v2/
│   │   ├── __init__.py
│   │   └── routes/
│   │       └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── rate_limiter.py
│   │   └── cache.py
│   └── dependencies.py
│
├── ai/
│   ├── __init__.py
│   ├── code_completion.py
│   └── code_analysis.py
│
├── cli/
│   └── ... (existing CLI code)
│
├── utils/
│   └── ... (existing utility functions)
│
├── tests/
│   └── api/
│       ├── test_main.py
│       └── test_routes/
│           ├── test_auth.py
│           ├── test_files.py
│           ├── test_ai_operations.py
│           └── test_websockets.py
│
├── requirements.txt
└── main.py
```

This structure accommodates the new features while maintaining a clean and organized codebase.

By implementing these advanced features, you've created a robust, scalable, and feature-rich RESTful API for your AI-assisted coding tool. This API can now serve as a solid foundation for building web interfaces, integrating with other services, and expanding the tool's capabilities in the future.