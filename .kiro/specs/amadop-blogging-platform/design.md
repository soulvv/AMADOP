# Design Document: AMADOP Blogging Platform

## Overview

The AMADOP (Autonomous Multi-Agent DevOps Orchestration Platform) Blogging Platform is a modern, microservices-based blogging system designed to be monitored and controlled by DevOps automation agents. This document covers the application layer (50% of the full AMADOP project), consisting of four independent backend microservices built with Python/FastAPI and a React frontend. The system emphasizes observability through structured logging, health checks, and Prometheus metrics endpoints, enabling future integration with autonomous DevOps orchestration layers.

The platform provides core blogging functionality including user authentication, post management, commenting, and notifications, all architected as independently deployable services communicating via REST APIs. Each service maintains its own data models and exposes standardized monitoring endpoints for operational visibility.

## Architecture

### System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[React Frontend<br/>Vite + TailwindCSS]
    end
    
    subgraph "API Gateway / Load Balancer"
        LB[Load Balancer<br/>Port Routing]
    end
    
    subgraph "Microservices Layer"
        AUTH[Auth Service<br/>:8001<br/>JWT + User Management]
        POST[Post Service<br/>:8002<br/>Blog Post CRUD]
        COMMENT[Comment Service<br/>:8003<br/>Comment Management]
        NOTIF[Notification Service<br/>:8004<br/>Notification Storage]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Database)]
    end
    
    subgraph "Observability Layer"
        PROM[Prometheus<br/>Metrics Collection]
        LOGS[Structured Logs]
    end
    
    FE -->|HTTP/REST| LB
    LB --> AUTH
    LB --> POST
    LB --> COMMENT
    LB --> NOTIF
    
    AUTH --> DB
    POST --> DB
    COMMENT --> DB
    NOTIF --> DB
    
    AUTH -.->|/metrics| PROM
    POST -.->|/metrics| PROM
    COMMENT -.->|/metrics| PROM
    NOTIF -.->|/metrics| PROM
    
    AUTH -.->|logs| LOGS
    POST -.->|logs| LOGS
    COMMENT -.->|logs| LOGS
    NOTIF -.->|logs| LOGS
```


### Service Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant AuthService
    participant PostService
    participant CommentService
    participant NotifService
    participant Database
    
    User->>Frontend: Register/Login
    Frontend->>AuthService: POST /register or /login
    AuthService->>Database: Store/Verify User
    Database-->>AuthService: User Data
    AuthService-->>Frontend: JWT Token
    Frontend->>Frontend: Store Token
    
    User->>Frontend: Create Post
    Frontend->>PostService: POST /posts (with JWT)
    PostService->>AuthService: Verify JWT
    AuthService-->>PostService: User ID
    PostService->>Database: Insert Post
    Database-->>PostService: Post Created
    PostService-->>Frontend: Post Data
    
    User->>Frontend: Add Comment
    Frontend->>CommentService: POST /comments (with JWT)
    CommentService->>AuthService: Verify JWT
    AuthService-->>CommentService: User ID
    CommentService->>Database: Insert Comment
    CommentService->>NotifService: Trigger Notification
    NotifService->>Database: Store Notification
    Database-->>CommentService: Comment Created
    CommentService-->>Frontend: Comment Data
    
    User->>Frontend: View Notifications
    Frontend->>NotifService: GET /notifications/{user_id}
    NotifService->>Database: Fetch Notifications
    Database-->>NotifService: Notification List
    NotifService-->>Frontend: Notifications
```

## Components and Interfaces

### Component 1: Auth Service

**Purpose**: Handles user authentication, registration, and JWT token management. Provides user identity verification for other services.

**Port**: 8001

**Interface**:
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Request/Response Schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

# API Routes
router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserRegister) -> UserResponse:
    """Register a new user with hashed password"""
    pass

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin) -> Token:
    """Authenticate user and return JWT token"""
    pass

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Get current authenticated user details"""
    pass

@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint for monitoring"""
    pass

@router.get("/metrics")
async def metrics() -> str:
    """Prometheus metrics endpoint"""
    pass
```

**Responsibilities**:
- User registration with password hashing (bcrypt)
- User authentication and JWT token generation
- JWT token verification for other services
- User profile retrieval
- Health and metrics reporting


### Component 2: Post Service

**Purpose**: Manages blog post lifecycle including creation, retrieval, and deletion operations.

**Port**: 8002

**Interface**:
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Request/Response Schemas
class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    author_username: Optional[str] = None
    created_at: datetime

# API Routes
router = APIRouter()

@router.post("/posts", response_model=PostResponse, status_code=201)
async def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)) -> PostResponse:
    """Create a new blog post"""
    pass

@router.get("/posts", response_model=List[PostResponse])
async def get_all_posts(skip: int = 0, limit: int = 100) -> List[PostResponse]:
    """Retrieve all blog posts with pagination"""
    pass

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int) -> PostResponse:
    """Retrieve a specific blog post by ID"""
    pass

@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(post_id: int, current_user: dict = Depends(get_current_user)) -> None:
    """Delete a blog post (author only)"""
    pass

@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint for monitoring"""
    pass

@router.get("/metrics")
async def metrics() -> str:
    """Prometheus metrics endpoint"""
    pass
```

**Responsibilities**:
- Create new blog posts with author attribution
- Retrieve all posts or specific post by ID
- Delete posts (with author authorization)
- Validate post data using Pydantic schemas
- Health and metrics reporting

### Component 3: Comment Service

**Purpose**: Manages comment creation and retrieval for blog posts, triggers notifications.

**Port**: 8003

**Interface**:
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Request/Response Schemas
class CommentCreate(BaseModel):
    post_id: int
    content: str

class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    username: Optional[str] = None
    content: str
    created_at: datetime

# API Routes
router = APIRouter()

@router.post("/comments", response_model=CommentResponse, status_code=201)
async def create_comment(comment: CommentCreate, current_user: dict = Depends(get_current_user)) -> CommentResponse:
    """Create a new comment on a post"""
    pass

@router.get("/comments/{post_id}", response_model=List[CommentResponse])
async def get_comments_for_post(post_id: int) -> List[CommentResponse]:
    """Retrieve all comments for a specific post"""
    pass

@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint for monitoring"""
    pass

@router.get("/metrics")
async def metrics() -> str:
    """Prometheus metrics endpoint"""
    pass
```

**Responsibilities**:
- Create comments on blog posts
- Retrieve comments for specific posts
- Trigger notification service when comments are added
- Validate comment data
- Health and metrics reporting


### Component 4: Notification Service

**Purpose**: Generates and stores notifications for user activities, primarily comment notifications.

**Port**: 8004

**Interface**:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Request/Response Schemas
class NotificationCreate(BaseModel):
    user_id: int
    message: str

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    created_at: datetime
    read: bool = False

# API Routes
router = APIRouter()

@router.post("/notifications", response_model=NotificationResponse, status_code=201)
async def create_notification(notification: NotificationCreate) -> NotificationResponse:
    """Create a new notification (internal service call)"""
    pass

@router.get("/notifications/{user_id}", response_model=List[NotificationResponse])
async def get_user_notifications(user_id: int, unread_only: bool = False) -> List[NotificationResponse]:
    """Retrieve notifications for a specific user"""
    pass

@router.patch("/notifications/{notification_id}/read", status_code=204)
async def mark_notification_read(notification_id: int) -> None:
    """Mark a notification as read"""
    pass

@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint for monitoring"""
    pass

@router.get("/metrics")
async def metrics() -> str:
    """Prometheus metrics endpoint"""
    pass
```

**Responsibilities**:
- Store notifications for users
- Retrieve user-specific notifications
- Mark notifications as read
- Generate notifications from service events
- Health and metrics reporting

### Component 5: Frontend Application

**Purpose**: React-based web interface for user interaction with the blogging platform.

**Port**: 5173 (Vite dev server)

**Interface**:
```typescript
// API Service Layer
interface AuthAPI {
  register(username: string, email: string, password: string): Promise<User>;
  login(username: string, password: string): Promise<TokenResponse>;
  getCurrentUser(): Promise<User>;
}

interface PostAPI {
  createPost(title: string, content: string): Promise<Post>;
  getAllPosts(skip?: number, limit?: number): Promise<Post[]>;
  getPost(postId: number): Promise<Post>;
  deletePost(postId: number): Promise<void>;
}

interface CommentAPI {
  createComment(postId: number, content: string): Promise<Comment>;
  getCommentsForPost(postId: number): Promise<Comment[]>;
}

interface NotificationAPI {
  getUserNotifications(userId: number, unreadOnly?: boolean): Promise<Notification[]>;
  markNotificationRead(notificationId: number): Promise<void>;
}

// React Components
const App: React.FC = () => { /* Main app component */ };
const LoginPage: React.FC = () => { /* Login page */ };
const RegisterPage: React.FC = () => { /* Registration page */ };
const HomePage: React.FC = () => { /* Blog feed */ };
const CreatePostPage: React.FC = () => { /* Post creation */ };
const PostPage: React.FC = () => { /* Single post view */ };
const NotificationsPage: React.FC = () => { /* Notifications */ };
```

**Responsibilities**:
- User authentication UI (login/register)
- Blog post feed display
- Post creation and viewing
- Comment submission and display
- Notification viewing
- JWT token management
- Responsive design with TailwindCSS


## Data Models

### Model 1: User (Auth Service)

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Validation Rules**:
- `username`: 3-50 characters, alphanumeric with underscores, unique
- `email`: Valid email format, unique
- `password`: Minimum 8 characters (hashed with bcrypt before storage)
- `created_at`: Auto-generated timestamp

**Indexes**:
- Primary key on `id`
- Unique index on `username`
- Unique index on `email`

### Model 2: Post (Post Service)

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Validation Rules**:
- `title`: 1-200 characters, non-empty
- `content`: Non-empty text
- `author_id`: Valid user ID (verified via Auth Service)
- `created_at`: Auto-generated timestamp

**Indexes**:
- Primary key on `id`
- Index on `author_id` for author queries
- Index on `created_at` for chronological sorting

### Model 3: Comment (Comment Service)

```python
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Validation Rules**:
- `post_id`: Valid post ID (verified via Post Service)
- `user_id`: Valid user ID (verified via Auth Service)
- `content`: 1-1000 characters, non-empty
- `created_at`: Auto-generated timestamp

**Indexes**:
- Primary key on `id`
- Index on `post_id` for post comment queries
- Index on `user_id` for user comment queries
- Composite index on `(post_id, created_at)` for sorted retrieval

### Model 4: Notification (Notification Service)

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(String(500), nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Validation Rules**:
- `user_id`: Valid user ID
- `message`: 1-500 characters, non-empty
- `read`: Boolean flag, defaults to False
- `created_at`: Auto-generated timestamp

**Indexes**:
- Primary key on `id`
- Index on `user_id` for user notification queries
- Composite index on `(user_id, read)` for unread queries
- Index on `created_at` for chronological sorting


## Main Algorithm/Workflow

### User Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth Service
    participant DB as Database
    
    U->>F: Enter credentials
    F->>A: POST /login {username, password}
    A->>DB: SELECT user WHERE username=?
    DB-->>A: User record with password_hash
    A->>A: bcrypt.verify(password, password_hash)
    alt Password Valid
        A->>A: generate_jwt_token(user_id, username)
        A-->>F: {access_token, token_type}
        F->>F: localStorage.setItem('token', access_token)
        F-->>U: Redirect to home page
    else Password Invalid
        A-->>F: 401 Unauthorized
        F-->>U: Display error message
    end
```

### Post Creation Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant P as Post Service
    participant A as Auth Service
    participant DB as Database
    
    U->>F: Submit post (title, content)
    F->>P: POST /posts {title, content}<br/>Authorization: Bearer <token>
    P->>A: Verify JWT token
    A-->>P: {user_id, username}
    P->>DB: INSERT INTO posts (title, content, author_id)
    DB-->>P: Post record with id
    P-->>F: PostResponse {id, title, content, author_id, created_at}
    F-->>U: Display success & redirect to post
```

### Comment Creation with Notification Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant C as Comment Service
    participant N as Notification Service
    participant P as Post Service
    participant A as Auth Service
    participant DB as Database
    
    U->>F: Submit comment
    F->>C: POST /comments {post_id, content}<br/>Authorization: Bearer <token>
    C->>A: Verify JWT token
    A-->>C: {user_id, username}
    C->>P: GET /posts/{post_id}
    P-->>C: Post details {author_id}
    C->>DB: INSERT INTO comments
    DB-->>C: Comment record
    C->>N: POST /notifications<br/>{user_id: author_id, message}
    N->>DB: INSERT INTO notifications
    DB-->>N: Notification created
    N-->>C: Success
    C-->>F: CommentResponse
    F-->>U: Display comment
```


## Key Functions with Formal Specifications

### Function 1: register_user()

```python
async def register_user(username: str, email: str, password: str, db: Session) -> User:
    """
    Register a new user with hashed password.
    
    Args:
        username: Unique username (3-50 chars)
        email: Valid email address
        password: Plain text password (min 8 chars)
        db: Database session
        
    Returns:
        User: Created user object
        
    Raises:
        HTTPException: 400 if username/email exists, 422 if validation fails
    """
    pass
```

**Preconditions**:
- `username` is non-empty string, 3-50 characters, alphanumeric with underscores
- `email` is valid email format
- `password` is non-empty string, minimum 8 characters
- `db` is valid database session
- No existing user with same `username` or `email`

**Postconditions**:
- User record created in database with unique `id`
- `password_hash` stored (never plain password)
- `created_at` timestamp set to current time
- Returns User object with all fields populated
- User can authenticate with provided credentials

**Loop Invariants**: N/A (no loops)

### Function 2: authenticate_user()

```python
async def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """
    Authenticate user credentials.
    
    Args:
        username: Username to authenticate
        password: Plain text password
        db: Database session
        
    Returns:
        User object if authentication successful, None otherwise
    """
    pass
```

**Preconditions**:
- `username` is non-empty string
- `password` is non-empty string
- `db` is valid database session

**Postconditions**:
- If user exists and password matches: returns User object
- If user doesn't exist or password invalid: returns None
- No side effects on database
- Password comparison uses constant-time algorithm (bcrypt)

**Loop Invariants**: N/A (no loops)

### Function 3: create_jwt_token()

```python
def create_jwt_token(user_id: int, username: str, expires_delta: timedelta = None) -> str:
    """
    Generate JWT access token.
    
    Args:
        user_id: User's unique identifier
        username: User's username
        expires_delta: Token expiration time (default: 30 minutes)
        
    Returns:
        Encoded JWT token string
    """
    pass
```

**Preconditions**:
- `user_id` is positive integer
- `username` is non-empty string
- `expires_delta` is None or positive timedelta
- SECRET_KEY environment variable is set

**Postconditions**:
- Returns valid JWT token string
- Token contains claims: `sub` (user_id), `username`, `exp` (expiration)
- Token signed with SECRET_KEY using HS256 algorithm
- Token expires after specified delta (default 30 minutes)
- Token can be decoded and verified by `verify_jwt_token()`

**Loop Invariants**: N/A (no loops)

### Function 4: verify_jwt_token()

```python
def verify_jwt_token(token: str) -> dict:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload with user_id and username
        
    Raises:
        HTTPException: 401 if token invalid or expired
    """
    pass
```

**Preconditions**:
- `token` is non-empty string
- SECRET_KEY environment variable matches token signing key

**Postconditions**:
- If token valid and not expired: returns dict with `user_id` and `username`
- If token invalid, expired, or malformed: raises HTTPException(401)
- No side effects on database or system state

**Loop Invariants**: N/A (no loops)


### Function 5: create_post()

```python
async def create_post(title: str, content: str, author_id: int, db: Session) -> Post:
    """
    Create a new blog post.
    
    Args:
        title: Post title (1-200 chars)
        content: Post content (non-empty)
        author_id: ID of post author
        db: Database session
        
    Returns:
        Created Post object
    """
    pass
```

**Preconditions**:
- `title` is non-empty string, 1-200 characters
- `content` is non-empty string
- `author_id` is positive integer corresponding to existing user
- `db` is valid database session

**Postconditions**:
- Post record created in database with unique `id`
- `created_at` timestamp set to current time
- Returns Post object with all fields populated
- Post is immediately queryable via `get_post()` or `get_all_posts()`

**Loop Invariants**: N/A (no loops)

### Function 6: get_all_posts()

```python
async def get_all_posts(db: Session, skip: int = 0, limit: int = 100) -> List[Post]:
    """
    Retrieve all blog posts with pagination.
    
    Args:
        db: Database session
        skip: Number of posts to skip (offset)
        limit: Maximum number of posts to return
        
    Returns:
        List of Post objects ordered by created_at descending
    """
    pass
```

**Preconditions**:
- `db` is valid database session
- `skip` is non-negative integer
- `limit` is positive integer, maximum 100

**Postconditions**:
- Returns list of Post objects (may be empty)
- Posts ordered by `created_at` descending (newest first)
- Returns at most `limit` posts
- Skips first `skip` posts
- No side effects on database

**Loop Invariants**: 
- For database query iteration: All retrieved posts have `created_at` >= next post's `created_at`

### Function 7: create_comment()

```python
async def create_comment(post_id: int, user_id: int, content: str, db: Session) -> Comment:
    """
    Create a comment on a blog post.
    
    Args:
        post_id: ID of post to comment on
        user_id: ID of commenting user
        content: Comment text (1-1000 chars)
        db: Database session
        
    Returns:
        Created Comment object
        
    Raises:
        HTTPException: 404 if post doesn't exist
    """
    pass
```

**Preconditions**:
- `post_id` is positive integer corresponding to existing post
- `user_id` is positive integer corresponding to existing user
- `content` is non-empty string, 1-1000 characters
- `db` is valid database session

**Postconditions**:
- Comment record created in database with unique `id`
- `created_at` timestamp set to current time
- Returns Comment object with all fields populated
- Comment is immediately queryable via `get_comments_for_post()`
- If post doesn't exist, raises HTTPException(404)

**Loop Invariants**: N/A (no loops)

### Function 8: trigger_notification()

```python
async def trigger_notification(user_id: int, message: str, notification_service_url: str) -> bool:
    """
    Send notification to notification service.
    
    Args:
        user_id: ID of user to notify
        message: Notification message
        notification_service_url: Base URL of notification service
        
    Returns:
        True if notification created successfully, False otherwise
    """
    pass
```

**Preconditions**:
- `user_id` is positive integer
- `message` is non-empty string, 1-500 characters
- `notification_service_url` is valid HTTP URL
- Notification service is reachable

**Postconditions**:
- HTTP POST request sent to notification service
- If request successful (2xx status): returns True
- If request fails (network error, 4xx/5xx): returns False
- Does not raise exceptions (graceful degradation)
- Notification creation is asynchronous (doesn't block comment creation)

**Loop Invariants**: N/A (no loops)


## Algorithmic Pseudocode

### Main Processing Algorithm: User Registration

```python
ALGORITHM register_user_workflow(username, email, password, db)
INPUT: username (string), email (string), password (string), db (Session)
OUTPUT: user (User object) or HTTPException

BEGIN
  # Precondition checks
  ASSERT len(username) >= 3 AND len(username) <= 50
  ASSERT is_valid_email(email)
  ASSERT len(password) >= 8
  
  # Step 1: Validate uniqueness
  existing_user_by_username ← db.query(User).filter(User.username == username).first()
  IF existing_user_by_username IS NOT NULL THEN
    RAISE HTTPException(status_code=400, detail="Username already exists")
  END IF
  
  existing_user_by_email ← db.query(User).filter(User.email == email).first()
  IF existing_user_by_email IS NOT NULL THEN
    RAISE HTTPException(status_code=400, detail="Email already registered")
  END IF
  
  # Step 2: Hash password
  password_hash ← bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
  
  # Step 3: Create user record
  new_user ← User(
    username=username,
    email=email,
    password_hash=password_hash.decode('utf-8')
  )
  
  # Step 4: Persist to database
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  
  # Postcondition checks
  ASSERT new_user.id IS NOT NULL
  ASSERT new_user.created_at IS NOT NULL
  ASSERT new_user.password_hash != password
  
  RETURN new_user
END
```

**Preconditions**:
- Input parameters are non-null
- Database session is active and connected
- Username and email are not already in use

**Postconditions**:
- User record exists in database with unique ID
- Password is hashed, never stored in plain text
- User can authenticate with provided credentials

**Loop Invariants**: N/A

### Authentication Algorithm: User Login

```python
ALGORITHM authenticate_and_generate_token(username, password, db)
INPUT: username (string), password (string), db (Session)
OUTPUT: token (dict) or HTTPException

BEGIN
  # Step 1: Retrieve user from database
  user ← db.query(User).filter(User.username == username).first()
  
  IF user IS NULL THEN
    RAISE HTTPException(status_code=401, detail="Invalid credentials")
  END IF
  
  # Step 2: Verify password using constant-time comparison
  password_bytes ← password.encode('utf-8')
  stored_hash ← user.password_hash.encode('utf-8')
  password_valid ← bcrypt.checkpw(password_bytes, stored_hash)
  
  IF NOT password_valid THEN
    RAISE HTTPException(status_code=401, detail="Invalid credentials")
  END IF
  
  # Step 3: Generate JWT token
  expiration_time ← datetime.utcnow() + timedelta(minutes=30)
  payload ← {
    "sub": user.id,
    "username": user.username,
    "exp": expiration_time
  }
  
  token ← jwt.encode(payload, SECRET_KEY, algorithm="HS256")
  
  # Postcondition checks
  ASSERT token IS NOT NULL
  ASSERT len(token) > 0
  
  RETURN {
    "access_token": token,
    "token_type": "bearer"
  }
END
```

**Preconditions**:
- Username and password are non-empty strings
- Database session is active
- SECRET_KEY is configured

**Postconditions**:
- If credentials valid: returns JWT token with 30-minute expiration
- If credentials invalid: raises HTTPException(401)
- Token can be verified and decoded

**Loop Invariants**: N/A


### Post Creation Algorithm

```python
ALGORITHM create_post_workflow(title, content, token, db)
INPUT: title (string), content (string), token (JWT string), db (Session)
OUTPUT: post (Post object) or HTTPException

BEGIN
  # Step 1: Verify JWT token and extract user info
  TRY
    payload ← jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id ← payload["sub"]
    username ← payload["username"]
  CATCH JWTError
    RAISE HTTPException(status_code=401, detail="Invalid token")
  END TRY
  
  # Step 2: Validate input
  ASSERT len(title) >= 1 AND len(title) <= 200
  ASSERT len(content) >= 1
  
  # Step 3: Create post record
  new_post ← Post(
    title=title,
    content=content,
    author_id=user_id
  )
  
  # Step 4: Persist to database
  db.add(new_post)
  db.commit()
  db.refresh(new_post)
  
  # Postcondition checks
  ASSERT new_post.id IS NOT NULL
  ASSERT new_post.created_at IS NOT NULL
  ASSERT new_post.author_id == user_id
  
  RETURN new_post
END
```

**Preconditions**:
- Token is valid JWT with user_id claim
- Title is 1-200 characters
- Content is non-empty
- Database session is active

**Postconditions**:
- Post record created with unique ID
- Post associated with authenticated user
- Post immediately queryable

**Loop Invariants**: N/A

### Comment Creation with Notification Algorithm

```python
ALGORITHM create_comment_with_notification(post_id, content, token, db)
INPUT: post_id (int), content (string), token (JWT string), db (Session)
OUTPUT: comment (Comment object) or HTTPException

BEGIN
  # Step 1: Verify JWT token
  TRY
    payload ← jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id ← payload["sub"]
  CATCH JWTError
    RAISE HTTPException(status_code=401, detail="Invalid token")
  END TRY
  
  # Step 2: Verify post exists and get author
  post ← db.query(Post).filter(Post.id == post_id).first()
  IF post IS NULL THEN
    RAISE HTTPException(status_code=404, detail="Post not found")
  END IF
  
  post_author_id ← post.author_id
  
  # Step 3: Validate comment content
  ASSERT len(content) >= 1 AND len(content) <= 1000
  
  # Step 4: Create comment record
  new_comment ← Comment(
    post_id=post_id,
    user_id=user_id,
    content=content
  )
  
  db.add(new_comment)
  db.commit()
  db.refresh(new_comment)
  
  # Step 5: Trigger notification asynchronously (non-blocking)
  IF user_id != post_author_id THEN
    notification_message ← f"New comment on your post: {post.title}"
    
    TRY
      # Make async HTTP call to notification service
      response ← http_client.post(
        url=f"{NOTIFICATION_SERVICE_URL}/notifications",
        json={
          "user_id": post_author_id,
          "message": notification_message
        },
        timeout=2.0
      )
      
      IF response.status_code >= 200 AND response.status_code < 300 THEN
        log.info(f"Notification sent for post {post_id}")
      ELSE
        log.warning(f"Notification failed with status {response.status_code}")
      END IF
    CATCH RequestException
      # Graceful degradation - don't fail comment creation
      log.error(f"Failed to send notification for post {post_id}")
    END TRY
  END IF
  
  # Postcondition checks
  ASSERT new_comment.id IS NOT NULL
  ASSERT new_comment.created_at IS NOT NULL
  ASSERT new_comment.post_id == post_id
  ASSERT new_comment.user_id == user_id
  
  RETURN new_comment
END
```

**Preconditions**:
- Token is valid JWT
- Post with post_id exists
- Content is 1-1000 characters
- Database session is active

**Postconditions**:
- Comment record created and persisted
- If commenter != post author: notification triggered (best effort)
- Comment creation succeeds even if notification fails
- Comment immediately queryable

**Loop Invariants**: N/A


### Metrics Collection Algorithm

```python
ALGORITHM collect_and_expose_metrics()
INPUT: None
OUTPUT: prometheus_metrics (string in Prometheus format)

BEGIN
  # Initialize Prometheus metrics collectors (at service startup)
  request_counter ← Counter(
    name="http_requests_total",
    documentation="Total HTTP requests",
    labelnames=["method", "endpoint", "status"]
  )
  
  request_latency ← Histogram(
    name="http_request_duration_seconds",
    documentation="HTTP request latency",
    labelnames=["method", "endpoint"]
  )
  
  error_counter ← Counter(
    name="http_errors_total",
    documentation="Total HTTP errors",
    labelnames=["method", "endpoint", "error_type"]
  )
  
  # Middleware to track metrics for each request
  FUNCTION track_request_metrics(request, call_next)
    start_time ← time.time()
    method ← request.method
    endpoint ← request.url.path
    
    TRY
      response ← call_next(request)
      duration ← time.time() - start_time
      
      # Record metrics
      request_counter.labels(
        method=method,
        endpoint=endpoint,
        status=response.status_code
      ).inc()
      
      request_latency.labels(
        method=method,
        endpoint=endpoint
      ).observe(duration)
      
      IF response.status_code >= 400 THEN
        error_counter.labels(
          method=method,
          endpoint=endpoint,
          error_type=f"http_{response.status_code}"
        ).inc()
      END IF
      
      RETURN response
      
    CATCH Exception as e
      duration ← time.time() - start_time
      
      # Record error metrics
      error_counter.labels(
        method=method,
        endpoint=endpoint,
        error_type=type(e).__name__
      ).inc()
      
      request_latency.labels(
        method=method,
        endpoint=endpoint
      ).observe(duration)
      
      RAISE e
    END TRY
  END FUNCTION
  
  # Expose metrics at /metrics endpoint
  FUNCTION get_metrics()
    RETURN generate_latest(REGISTRY)
  END FUNCTION
END
```

**Preconditions**:
- Prometheus client library installed
- Metrics collectors initialized at service startup
- Middleware registered in FastAPI application

**Postconditions**:
- All HTTP requests tracked with method, endpoint, status
- Request latencies recorded in histogram
- Errors counted by type
- Metrics exposed in Prometheus format at /metrics endpoint
- Metrics can be scraped by Prometheus server

**Loop Invariants**: 
- For each request: metrics are recorded before response is returned
- Metric counters are monotonically increasing


## Example Usage

### Backend Service Examples

#### Auth Service - User Registration and Login

```python
# Example 1: Register a new user
import requests

response = requests.post(
    "http://localhost:8001/register",
    json={
        "username": "johndoe",
        "email": "john@example.com",
        "password": "securepass123"
    }
)

if response.status_code == 201:
    user = response.json()
    print(f"User created: {user['username']} (ID: {user['id']})")
else:
    print(f"Error: {response.json()['detail']}")

# Example 2: Login and get JWT token
response = requests.post(
    "http://localhost:8001/login",
    json={
        "username": "johndoe",
        "password": "securepass123"
    }
)

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"Login successful. Token: {access_token[:20]}...")
else:
    print("Login failed")

# Example 3: Get current user info
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("http://localhost:8001/me", headers=headers)

if response.status_code == 200:
    user = response.json()
    print(f"Current user: {user['username']} ({user['email']})")
```

#### Post Service - Create and Retrieve Posts

```python
# Example 4: Create a blog post
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.post(
    "http://localhost:8002/posts",
    headers=headers,
    json={
        "title": "My First Blog Post",
        "content": "This is the content of my first blog post. It's about microservices architecture."
    }
)

if response.status_code == 201:
    post = response.json()
    post_id = post["id"]
    print(f"Post created: {post['title']} (ID: {post_id})")

# Example 5: Get all posts
response = requests.get("http://localhost:8002/posts?skip=0&limit=10")

if response.status_code == 200:
    posts = response.json()
    print(f"Retrieved {len(posts)} posts:")
    for post in posts:
        print(f"  - {post['title']} by user {post['author_id']}")

# Example 6: Get specific post
response = requests.get(f"http://localhost:8002/posts/{post_id}")

if response.status_code == 200:
    post = response.json()
    print(f"Post: {post['title']}")
    print(f"Content: {post['content'][:100]}...")
```

#### Comment Service - Add and Retrieve Comments

```python
# Example 7: Add a comment to a post
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.post(
    "http://localhost:8003/comments",
    headers=headers,
    json={
        "post_id": post_id,
        "content": "Great post! Very informative."
    }
)

if response.status_code == 201:
    comment = response.json()
    print(f"Comment added: {comment['content']}")

# Example 8: Get all comments for a post
response = requests.get(f"http://localhost:8003/comments/{post_id}")

if response.status_code == 200:
    comments = response.json()
    print(f"Post has {len(comments)} comments:")
    for comment in comments:
        print(f"  - User {comment['user_id']}: {comment['content']}")
```

#### Notification Service - Retrieve Notifications

```python
# Example 9: Get user notifications
user_id = 1
response = requests.get(f"http://localhost:8004/notifications/{user_id}")

if response.status_code == 200:
    notifications = response.json()
    print(f"User has {len(notifications)} notifications:")
    for notif in notifications:
        status = "unread" if not notif["read"] else "read"
        print(f"  - [{status}] {notif['message']}")

# Example 10: Get only unread notifications
response = requests.get(f"http://localhost:8004/notifications/{user_id}?unread_only=true")

if response.status_code == 200:
    unread = response.json()
    print(f"User has {len(unread)} unread notifications")
```


### Frontend Examples

#### React Component - Login Page

```typescript
// Example 11: Login page component
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await axios.post('http://localhost:8001/login', {
        username,
        password
      });

      // Store token in localStorage
      localStorage.setItem('token', response.data.access_token);
      
      // Redirect to home page
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-6">Login</h2>
        
        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border rounded"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border rounded"
              required
            />
          </div>
          
          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
```

#### React Component - Home Feed

```typescript
// Example 12: Home feed with blog posts
import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Post {
  id: number;
  title: string;
  content: string;
  author_id: number;
  created_at: string;
}

const HomePage: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await axios.get('http://localhost:8002/posts');
        setPosts(response.data);
      } catch (err) {
        console.error('Failed to fetch posts', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  if (loading) {
    return <div className="text-center mt-8">Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Blog Posts</h1>
      
      <div className="space-y-4">
        {posts.map((post) => (
          <div key={post.id} className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-2">{post.title}</h2>
            <p className="text-gray-600 mb-2">
              {post.content.substring(0, 200)}...
            </p>
            <div className="text-sm text-gray-500">
              By User {post.author_id} • {new Date(post.created_at).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HomePage;
```

#### React Component - Create Post

```typescript
// Example 13: Create post page
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const CreatePostPage: React.FC = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      const response = await axios.post(
        'http://localhost:8002/posts',
        { title, content },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      // Redirect to the new post
      navigate(`/posts/${response.data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create post');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Create New Post</h1>
      
      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow">
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border rounded"
            maxLength={200}
            required
          />
        </div>
        
        <div className="mb-6">
          <label className="block text-gray-700 mb-2">Content</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full px-3 py-2 border rounded h-64"
            required
          />
        </div>
        
        <button
          type="submit"
          className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
        >
          Publish Post
        </button>
      </form>
    </div>
  );
};

export default CreatePostPage;
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Password Security

For any user registration or password storage operation, the stored password hash must be different from the original password, and the bcrypt verification function must successfully verify the original password against the stored hash.

**Validates: Requirements 1.6, 14.1, 14.6**

### Property 2: JWT Token Validity

For any valid JWT token, the token must not be expired, have a valid signature when verified with the secret key, reference an existing user ID in the payload, include the username in the payload, and have an expiration time of 30 minutes from creation.

**Validates: Requirements 2.4, 2.5, 2.6, 14.3, 14.4**

### Property 3: Post Ownership

For any post in the system, there must exist a user whose ID matches the post's author_id field.

**Validates: Requirement 13.1**

### Property 4: Comment Referential Integrity

For any comment in the system, there must exist a post whose ID matches the comment's post_id field, and there must exist a user whose ID matches the comment's user_id field.

**Validates: Requirements 13.2, 13.3**

### Property 5: Notification Delivery

For any comment where the commenter's user ID differs from the post author's user ID, there must exist a notification record for the post author that references the post.

**Validates: Requirements 8.1, 8.3**

### Property 6: Authentication Required for Mutations

For any data-modifying operation (create post, create comment, delete post), the operation must require a valid JWT token that can be successfully verified.

**Validates: Requirements 3.2, 5.4, 6.2**

### Property 7: Chronological Ordering

For any two posts where post1 was created before post2, when retrieving all posts, post2 must appear before post1 in the returned list (descending order by creation time).

**Validates: Requirement 4.1**

### Property 8: Metrics Monotonicity

For any two points in time t1 and t2 where t1 is before t2, the total request counter and total error counter at t2 must be greater than or equal to their values at t1.

**Validates: Requirements 11.2, 11.3, 11.4**

### Property 9: Health Check Availability

For any service (auth, post, comment, notification) that is running and operational, a GET request to the service's /health endpoint must return a 200 status code.

**Validates: Requirements 10.2, 10.4, 10.5, 10.6, 10.7**

### Property 10: Data Validation

For any user, the username must be between 3 and 50 characters, the email must match a valid email format, and the password hash must be non-empty. For any post, the title must be between 1 and 200 characters and the content must be non-empty. For any comment, the content must be between 1 and 1000 characters.

**Validates: Requirements 12.2, 12.3, 12.4, 12.5, 12.6**


## Error Handling

### Error Scenario 1: Invalid Credentials

**Condition**: User provides incorrect username or password during login

**Response**: 
- HTTP 401 Unauthorized
- JSON response: `{"detail": "Invalid credentials"}`
- No information leaked about whether username or password was incorrect (security)

**Recovery**: 
- User can retry with correct credentials
- No account lockout on failed attempts (can be added later)
- Frontend displays error message to user

### Error Scenario 2: Duplicate Username/Email

**Condition**: User attempts to register with username or email that already exists

**Response**:
- HTTP 400 Bad Request
- JSON response: `{"detail": "Username already exists"}` or `{"detail": "Email already registered"}`

**Recovery**:
- User must choose different username/email
- Frontend displays specific error message
- Existing user data remains unchanged

### Error Scenario 3: Expired JWT Token

**Condition**: User makes authenticated request with expired token

**Response**:
- HTTP 401 Unauthorized
- JSON response: `{"detail": "Token expired"}`

**Recovery**:
- Frontend detects 401 response
- Redirects user to login page
- Clears expired token from localStorage
- User must re-authenticate

### Error Scenario 4: Post Not Found

**Condition**: User requests post or tries to comment on non-existent post

**Response**:
- HTTP 404 Not Found
- JSON response: `{"detail": "Post not found"}`

**Recovery**:
- Frontend displays "Post not found" message
- User redirected to home page
- No data corruption

### Error Scenario 5: Unauthorized Post Deletion

**Condition**: User attempts to delete post they didn't author

**Response**:
- HTTP 403 Forbidden
- JSON response: `{"detail": "Not authorized to delete this post"}`

**Recovery**:
- Post remains unchanged
- Frontend displays error message
- User can only delete their own posts

### Error Scenario 6: Database Connection Failure

**Condition**: Service cannot connect to PostgreSQL database

**Response**:
- HTTP 503 Service Unavailable
- JSON response: `{"detail": "Service temporarily unavailable"}`
- Health check endpoint returns unhealthy status

**Recovery**:
- Service attempts to reconnect to database
- Requests fail until connection restored
- Frontend displays maintenance message
- DevOps agents alerted via health check failures

### Error Scenario 7: Notification Service Unavailable

**Condition**: Comment service cannot reach notification service

**Response**:
- Comment creation succeeds (graceful degradation)
- Warning logged: "Failed to send notification for post {post_id}"
- No exception raised to user

**Recovery**:
- Comment is saved successfully
- Notification delivery attempted on best-effort basis
- User experience not impacted
- DevOps monitoring detects notification service issues

### Error Scenario 8: Invalid Input Validation

**Condition**: User submits data that fails Pydantic validation (e.g., title too long, invalid email)

**Response**:
- HTTP 422 Unprocessable Entity
- JSON response with detailed validation errors:
  ```json
  {
    "detail": [
      {
        "loc": ["body", "title"],
        "msg": "ensure this value has at most 200 characters",
        "type": "value_error.any_str.max_length"
      }
    ]
  }
  ```

**Recovery**:
- Frontend displays validation errors to user
- User corrects input and resubmits
- No data persisted until validation passes

### Error Scenario 9: Metrics Collection Failure

**Condition**: Prometheus metrics collection encounters error

**Response**:
- Error logged but not propagated to user
- Request processing continues normally
- Metrics endpoint may return partial data

**Recovery**:
- Metrics collection is non-blocking
- Service remains operational
- DevOps monitoring detects metrics gaps
- Metrics resume on next successful collection

### Error Scenario 10: CORS Policy Violation

**Condition**: Frontend makes request from unauthorized origin

**Response**:
- Browser blocks request
- CORS error in browser console

**Recovery**:
- Configure CORS middleware in FastAPI with allowed origins
- Development: Allow localhost origins
- Production: Whitelist specific frontend domains
- Update CORS configuration and restart service


## Testing Strategy

### Unit Testing Approach

**Framework**: pytest for Python backend, Jest/Vitest for React frontend

**Coverage Goals**: Minimum 80% code coverage for all services

**Key Test Cases**:

#### Auth Service Unit Tests
- `test_register_user_success()`: Valid registration creates user with hashed password
- `test_register_duplicate_username()`: Duplicate username returns 400 error
- `test_register_duplicate_email()`: Duplicate email returns 400 error
- `test_register_invalid_email()`: Invalid email format returns 422 error
- `test_register_short_password()`: Password < 8 chars returns 422 error
- `test_login_success()`: Valid credentials return JWT token
- `test_login_invalid_username()`: Non-existent username returns 401
- `test_login_invalid_password()`: Wrong password returns 401
- `test_jwt_token_generation()`: Token contains correct claims and expiration
- `test_jwt_token_verification()`: Valid token decodes successfully
- `test_jwt_token_expired()`: Expired token raises exception
- `test_jwt_token_invalid_signature()`: Tampered token raises exception
- `test_get_current_user()`: Valid token returns user details
- `test_password_hashing()`: Password never stored in plain text

#### Post Service Unit Tests
- `test_create_post_success()`: Authenticated user creates post
- `test_create_post_unauthorized()`: Missing token returns 401
- `test_create_post_invalid_token()`: Invalid token returns 401
- `test_create_post_empty_title()`: Empty title returns 422
- `test_create_post_title_too_long()`: Title > 200 chars returns 422
- `test_get_all_posts()`: Returns posts in descending order
- `test_get_all_posts_pagination()`: Skip and limit work correctly
- `test_get_post_by_id()`: Returns specific post
- `test_get_post_not_found()`: Non-existent post returns 404
- `test_delete_post_success()`: Author can delete own post
- `test_delete_post_unauthorized()`: Non-author cannot delete post
- `test_delete_post_not_found()`: Deleting non-existent post returns 404

#### Comment Service Unit Tests
- `test_create_comment_success()`: Authenticated user creates comment
- `test_create_comment_unauthorized()`: Missing token returns 401
- `test_create_comment_post_not_found()`: Invalid post_id returns 404
- `test_create_comment_empty_content()`: Empty content returns 422
- `test_create_comment_content_too_long()`: Content > 1000 chars returns 422
- `test_get_comments_for_post()`: Returns all comments for post
- `test_get_comments_empty()`: Post with no comments returns empty list
- `test_notification_triggered()`: Comment triggers notification to post author
- `test_notification_not_triggered_self()`: No notification when commenting own post
- `test_notification_failure_graceful()`: Comment succeeds even if notification fails

#### Notification Service Unit Tests
- `test_create_notification_success()`: Notification created successfully
- `test_get_user_notifications()`: Returns all notifications for user
- `test_get_user_notifications_empty()`: User with no notifications returns empty list
- `test_get_unread_notifications()`: Filter returns only unread notifications
- `test_mark_notification_read()`: Notification marked as read
- `test_mark_notification_not_found()`: Invalid notification_id returns 404

#### Frontend Unit Tests
- `test_login_form_submission()`: Form submits with valid data
- `test_login_form_validation()`: Empty fields show validation errors
- `test_token_storage()`: Token stored in localStorage on successful login
- `test_authenticated_requests()`: Token included in Authorization header
- `test_post_creation_form()`: Post form submits with title and content
- `test_comment_submission()`: Comment form submits with content
- `test_post_list_rendering()`: Posts rendered correctly from API data
- `test_loading_states()`: Loading indicators shown during API calls
- `test_error_handling()`: Error messages displayed on API failures

### Property-Based Testing Approach

**Property Test Library**: Hypothesis (Python), fast-check (TypeScript)

**Property Tests**:

#### Property Test 1: Password Hashing Consistency
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=8, max_size=100))
def test_password_hashing_consistency(password):
    """Password hashing should be deterministic for verification"""
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # Hashes should be different (salt)
    assert hash1 != hash2
    
    # But both should verify against original password
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)
```

#### Property Test 2: JWT Token Round-Trip
```python
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
)
def test_jwt_token_roundtrip(user_id, username):
    """JWT token encoding and decoding should be reversible"""
    token = create_jwt_token(user_id, username)
    decoded = verify_jwt_token(token)
    
    assert decoded["sub"] == user_id
    assert decoded["username"] == username
```

#### Property Test 3: Post Ordering Invariant
```python
@given(st.lists(st.builds(Post), min_size=2, max_size=100))
def test_post_ordering_invariant(posts):
    """Posts should always be ordered by created_at descending"""
    # Insert posts in random order
    for post in posts:
        db.add(post)
    db.commit()
    
    # Retrieve posts
    retrieved = get_all_posts(db)
    
    # Check ordering
    for i in range(len(retrieved) - 1):
        assert retrieved[i].created_at >= retrieved[i + 1].created_at
```

#### Property Test 4: Input Validation Consistency
```python
@given(
    title=st.text(min_size=0, max_size=300),
    content=st.text(min_size=0, max_size=10000)
)
def test_post_validation_consistency(title, content):
    """Post validation should consistently accept/reject based on rules"""
    is_valid_title = 1 <= len(title) <= 200
    is_valid_content = len(content) >= 1
    should_accept = is_valid_title and is_valid_content
    
    try:
        validate_post_data(title, content)
        assert should_accept, "Validation accepted invalid data"
    except ValidationError:
        assert not should_accept, "Validation rejected valid data"
```

#### Property Test 5: Metrics Monotonicity
```python
@given(st.lists(st.builds(HTTPRequest), min_size=1, max_size=1000))
def test_metrics_monotonicity(requests):
    """Request counter should monotonically increase"""
    initial_count = get_request_count()
    
    for request in requests:
        process_request(request)
    
    final_count = get_request_count()
    
    assert final_count >= initial_count + len(requests)
```

### Integration Testing Approach

**Framework**: pytest with TestClient (FastAPI), Playwright (E2E)

**Integration Test Scenarios**:

#### Integration Test 1: Complete User Journey
```python
def test_complete_user_journey():
    """Test full user flow from registration to commenting"""
    # 1. Register user
    response = client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    
    # 2. Login
    response = client.post("/login", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 3. Create post
    response = client.post("/posts", 
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Post", "content": "Test content"}
    )
    assert response.status_code == 201
    post_id = response.json()["id"]
    
    # 4. Add comment
    response = client.post("/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"post_id": post_id, "content": "Test comment"}
    )
    assert response.status_code == 201
    
    # 5. Check notifications (should be empty - own post)
    user_id = 1
    response = client.get(f"/notifications/{user_id}")
    assert response.status_code == 200
```

#### Integration Test 2: Cross-Service Communication
```python
def test_comment_notification_integration():
    """Test that comments trigger notifications across services"""
    # Create two users
    user1_token = create_and_login_user("user1", "user1@example.com")
    user2_token = create_and_login_user("user2", "user2@example.com")
    
    # User1 creates post
    post_response = create_post(user1_token, "User1 Post", "Content")
    post_id = post_response["id"]
    user1_id = post_response["author_id"]
    
    # User2 comments on User1's post
    create_comment(user2_token, post_id, "Nice post!")
    
    # Check User1 received notification
    notifications = get_notifications(user1_id)
    assert len(notifications) == 1
    assert "comment" in notifications[0]["message"].lower()
```

#### Integration Test 3: Health Check Monitoring
```python
def test_all_services_healthy():
    """Test that all services report healthy status"""
    services = [
        ("http://localhost:8001/health", "Auth Service"),
        ("http://localhost:8002/health", "Post Service"),
        ("http://localhost:8003/health", "Comment Service"),
        ("http://localhost:8004/health", "Notification Service")
    ]
    
    for url, name in services:
        response = requests.get(url)
        assert response.status_code == 200, f"{name} is unhealthy"
        assert response.json()["status"] == "healthy"
```

#### Integration Test 4: Metrics Collection
```python
def test_metrics_collection():
    """Test that metrics are collected and exposed"""
    # Make some requests
    for _ in range(10):
        client.get("/posts")
    
    # Check metrics endpoint
    response = client.get("/metrics")
    assert response.status_code == 200
    
    metrics_text = response.text
    assert "http_requests_total" in metrics_text
    assert "http_request_duration_seconds" in metrics_text
```


## Performance Considerations

### Database Optimization

**Indexing Strategy**:
- Primary key indexes on all `id` columns (automatic)
- Unique indexes on `users.username` and `users.email` for fast lookups
- Index on `posts.author_id` for author-based queries
- Index on `posts.created_at` for chronological sorting
- Composite index on `(comments.post_id, comments.created_at)` for efficient comment retrieval
- Index on `notifications.user_id` for user notification queries
- Composite index on `(notifications.user_id, notifications.read)` for unread filtering

**Query Optimization**:
- Use pagination (skip/limit) for all list endpoints to prevent large result sets
- Implement connection pooling in SQLAlchemy (default pool size: 5-10 connections)
- Use `select_related` or eager loading to prevent N+1 query problems
- Add database query logging in development to identify slow queries

**Expected Performance**:
- User registration/login: < 200ms (bcrypt hashing is intentionally slow for security)
- Post creation: < 50ms
- Post retrieval (paginated): < 100ms for 100 posts
- Comment creation: < 100ms (includes notification trigger)
- Notification retrieval: < 50ms

### API Response Time Targets

**Service-Level Objectives (SLOs)**:
- P50 (median) response time: < 100ms
- P95 response time: < 500ms
- P99 response time: < 1000ms
- Health check endpoints: < 10ms

**Optimization Techniques**:
- Use async/await for all I/O operations (database, HTTP calls)
- Implement request timeout limits (default: 30 seconds)
- Use HTTP connection pooling for inter-service communication
- Enable gzip compression for large responses
- Implement response caching for frequently accessed data (future enhancement)

### Scalability Considerations

**Horizontal Scaling**:
- All services are stateless and can be scaled horizontally
- Multiple instances can run behind a load balancer
- JWT tokens enable distributed authentication without session storage
- Database connection pooling supports multiple service instances

**Vertical Scaling**:
- Each service can handle ~1000 requests/second on a single core
- Increase worker processes (Uvicorn workers) based on CPU cores
- Recommended: 2-4 workers per service for production

**Database Scaling**:
- PostgreSQL can handle 10,000+ concurrent connections with proper tuning
- Implement read replicas for read-heavy workloads (future enhancement)
- Consider database sharding if user base exceeds 1 million users
- Use database connection pooling to limit connections per service

### Caching Strategy (Future Enhancement)

**Redis Caching Opportunities**:
- Cache frequently accessed posts (TTL: 5 minutes)
- Cache user profile data (TTL: 10 minutes)
- Cache post comment counts (TTL: 1 minute)
- Implement cache invalidation on updates

**CDN for Static Assets**:
- Serve React frontend through CDN
- Cache static assets (JS, CSS, images) at edge locations
- Reduce latency for global users

### Resource Limits

**Memory Usage**:
- Each service: ~100-200 MB base memory
- Database connection pool: ~10 MB per connection
- Expected total per service: ~300-500 MB under load

**CPU Usage**:
- Password hashing (bcrypt): CPU-intensive by design
- JWT operations: Minimal CPU usage
- Database queries: I/O bound, not CPU bound
- Expected: < 50% CPU utilization under normal load

**Network Bandwidth**:
- Average request size: 1-10 KB
- Average response size: 1-50 KB (posts with content)
- Expected bandwidth: < 10 Mbps for 100 concurrent users

### Monitoring and Alerting

**Key Performance Metrics**:
- Request latency (P50, P95, P99)
- Request throughput (requests/second)
- Error rate (errors/total requests)
- Database query time
- Service uptime

**Alert Thresholds**:
- P95 latency > 1 second: Warning
- P99 latency > 5 seconds: Critical
- Error rate > 5%: Warning
- Error rate > 10%: Critical
- Service down: Critical (immediate alert)


## Security Considerations

### Authentication and Authorization

**Password Security**:
- Passwords hashed using bcrypt with automatic salt generation
- Minimum password length: 8 characters (configurable)
- Password complexity requirements can be added (uppercase, numbers, special chars)
- Passwords never logged or exposed in API responses
- Password hashes use cost factor 12 (2^12 iterations) for bcrypt

**JWT Token Security**:
- Tokens signed with HS256 algorithm using SECRET_KEY
- SECRET_KEY must be strong (minimum 32 characters) and kept secret
- Token expiration: 30 minutes (configurable)
- Tokens include user_id and username claims
- No sensitive data stored in token payload (tokens are not encrypted, only signed)
- Token verification on every authenticated request

**Authorization Model**:
- Users can only delete their own posts
- Users can comment on any post
- Post authors receive notifications for comments
- No admin/moderator roles in initial version (can be added)

### Input Validation and Sanitization

**Pydantic Validation**:
- All request bodies validated using Pydantic schemas
- Type checking enforced (string, int, email, etc.)
- Length constraints on all string fields
- Email format validation using EmailStr
- Automatic 422 Unprocessable Entity for invalid input

**SQL Injection Prevention**:
- SQLAlchemy ORM used for all database queries
- Parameterized queries prevent SQL injection
- No raw SQL queries with user input
- Input validation before database operations

**XSS Prevention**:
- React automatically escapes rendered content
- No `dangerouslySetInnerHTML` used in frontend
- Content-Security-Policy headers can be added
- User-generated content sanitized before display

### CORS Configuration

**Development**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Rate Limiting (Future Enhancement)

**Recommended Rate Limits**:
- Login endpoint: 5 requests per minute per IP
- Registration endpoint: 3 requests per minute per IP
- Post creation: 10 requests per minute per user
- Comment creation: 20 requests per minute per user
- General API: 100 requests per minute per user

**Implementation**:
- Use slowapi or fastapi-limiter library
- Store rate limit counters in Redis
- Return 429 Too Many Requests when limit exceeded

### HTTPS and Transport Security

**Production Requirements**:
- All services must use HTTPS in production
- TLS 1.2 or higher required
- Valid SSL certificates (Let's Encrypt recommended)
- HTTP Strict Transport Security (HSTS) headers
- Secure cookie flags (HttpOnly, Secure, SameSite)

**Certificate Management**:
- Use reverse proxy (Nginx, Traefik) for SSL termination
- Automatic certificate renewal with certbot
- Monitor certificate expiration dates

### Secrets Management

**Environment Variables**:
```bash
# Required secrets
SECRET_KEY=<strong-random-string-min-32-chars>
DATABASE_URL=postgresql://user:password@localhost/dbname
POSTGRES_PASSWORD=<strong-database-password>

# Service URLs
AUTH_SERVICE_URL=http://localhost:8001
POST_SERVICE_URL=http://localhost:8002
COMMENT_SERVICE_URL=http://localhost:8003
NOTIFICATION_SERVICE_URL=http://localhost:8004
```

**Best Practices**:
- Never commit secrets to version control
- Use `.env` files for local development (add to `.gitignore`)
- Use secrets management service in production (AWS Secrets Manager, HashiCorp Vault)
- Rotate secrets regularly (every 90 days recommended)
- Use different secrets for development, staging, and production

### Database Security

**Connection Security**:
- Use SSL/TLS for database connections in production
- Restrict database access to application servers only
- Use strong database passwords (minimum 16 characters)
- Create separate database users per service with minimal privileges

**Data Protection**:
- Regular database backups (daily recommended)
- Encrypt backups at rest
- Test backup restoration procedures
- Implement point-in-time recovery capability

**Access Control**:
- Principle of least privilege for database users
- Auth service user: SELECT, INSERT on users table
- Post service user: SELECT, INSERT, DELETE on posts table
- Comment service user: SELECT, INSERT on comments table
- Notification service user: SELECT, INSERT, UPDATE on notifications table

### Logging and Audit Trail

**Security Logging**:
- Log all authentication attempts (success and failure)
- Log authorization failures (403 responses)
- Log suspicious activity (multiple failed logins, unusual patterns)
- Never log passwords, tokens, or sensitive data

**Log Format**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "auth-service",
  "event": "login_success",
  "user_id": 123,
  "username": "johndoe",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

**Log Retention**:
- Security logs: 90 days minimum
- Application logs: 30 days
- Access logs: 7 days
- Comply with data retention regulations (GDPR, etc.)

### Vulnerability Management

**Dependency Scanning**:
- Use `pip-audit` or `safety` for Python dependencies
- Use `npm audit` for JavaScript dependencies
- Run security scans in CI/CD pipeline
- Update dependencies regularly

**Security Headers**:
```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### Compliance Considerations

**GDPR Compliance** (if applicable):
- User data deletion capability (right to be forgotten)
- Data export capability (data portability)
- Privacy policy and terms of service
- Cookie consent for tracking
- Data processing agreements

**Data Privacy**:
- Minimize data collection (only collect what's needed)
- Encrypt sensitive data at rest (future enhancement)
- Implement data retention policies
- Provide user data access and deletion APIs


## Dependencies

### Backend Dependencies (Python)

#### Core Framework
- **FastAPI** (^0.104.0): Modern web framework for building APIs
- **Uvicorn** (^0.24.0): ASGI server for running FastAPI applications
- **Pydantic** (^2.5.0): Data validation using Python type annotations

#### Database
- **SQLAlchemy** (^2.0.0): SQL toolkit and ORM
- **psycopg2-binary** (^2.9.9): PostgreSQL adapter for Python
- **alembic** (^1.13.0): Database migration tool (optional, for schema changes)

#### Authentication
- **python-jose[cryptography]** (^3.3.0): JWT token creation and verification
- **passlib[bcrypt]** (^1.7.4): Password hashing with bcrypt
- **python-multipart** (^0.0.6): Form data parsing for FastAPI

#### Observability
- **prometheus-client** (^0.19.0): Prometheus metrics collection
- **python-json-logger** (^2.0.7): Structured JSON logging

#### HTTP Client
- **httpx** (^0.25.0): Async HTTP client for inter-service communication

#### Development
- **pytest** (^7.4.0): Testing framework
- **pytest-asyncio** (^0.21.0): Async test support
- **pytest-cov** (^4.1.0): Code coverage reporting
- **hypothesis** (^6.92.0): Property-based testing
- **black** (^23.12.0): Code formatting
- **flake8** (^6.1.0): Linting
- **mypy** (^1.7.0): Static type checking

#### requirements.txt Example
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0.post1
pydantic==2.5.2
pydantic[email]==2.5.2
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
prometheus-client==0.19.0
python-json-logger==2.0.7
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
hypothesis==6.92.1
```

### Frontend Dependencies (JavaScript/TypeScript)

#### Core Framework
- **React** (^18.2.0): UI library
- **React DOM** (^18.2.0): React rendering for web
- **React Router DOM** (^6.20.0): Client-side routing

#### Build Tool
- **Vite** (^5.0.0): Fast build tool and dev server
- **@vitejs/plugin-react** (^4.2.0): React plugin for Vite

#### Styling
- **TailwindCSS** (^3.3.0): Utility-first CSS framework
- **PostCSS** (^8.4.32): CSS processing
- **Autoprefixer** (^10.4.16): CSS vendor prefixing

#### HTTP Client
- **Axios** (^1.6.2): Promise-based HTTP client

#### TypeScript
- **TypeScript** (^5.3.0): Type-safe JavaScript
- **@types/react** (^18.2.0): React type definitions
- **@types/react-dom** (^18.2.0): React DOM type definitions

#### Development
- **ESLint** (^8.55.0): JavaScript linting
- **@typescript-eslint/eslint-plugin** (^6.14.0): TypeScript ESLint rules
- **@typescript-eslint/parser** (^6.14.0): TypeScript parser for ESLint
- **Prettier** (^3.1.0): Code formatting
- **Vitest** (^1.0.0): Unit testing framework
- **@testing-library/react** (^14.1.0): React testing utilities
- **@testing-library/jest-dom** (^6.1.0): Custom Jest matchers

#### package.json Example
```json
{
  "name": "amadop-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint . --ext ts,tsx",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\""
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.55.0",
    "postcss": "^8.4.32",
    "prettier": "^3.1.1",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "vitest": "^1.0.4",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5"
  }
}
```

### Infrastructure Dependencies

#### Database
- **PostgreSQL** (^15.0): Relational database
  - Installation: `brew install postgresql` (macOS) or `apt-get install postgresql` (Ubuntu)
  - Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15`

#### Monitoring (Optional)
- **Prometheus** (^2.45.0): Metrics collection and storage
  - Docker: `docker run -d -p 9090:9090 prom/prometheus`
- **Grafana** (^10.0.0): Metrics visualization
  - Docker: `docker run -d -p 3000:3000 grafana/grafana`

#### Reverse Proxy (Production)
- **Nginx** (^1.24.0): Reverse proxy and load balancer
- **Traefik** (^2.10.0): Modern reverse proxy with automatic HTTPS

#### Container Runtime (Optional)
- **Docker** (^24.0.0): Container platform
- **Docker Compose** (^2.20.0): Multi-container orchestration

### System Requirements

#### Development Environment
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **npm**: 9.0 or higher
- **PostgreSQL**: 15.0 or higher
- **Operating System**: macOS, Linux, or Windows with WSL2

#### Production Environment
- **CPU**: 2+ cores per service (8+ cores total recommended)
- **RAM**: 512 MB per service minimum (4 GB total recommended)
- **Storage**: 20 GB minimum (SSD recommended)
- **Network**: 100 Mbps minimum bandwidth
- **PostgreSQL**: Dedicated database server with 4 GB RAM minimum

### External Services (Future Enhancements)

#### Email Service (for notifications)
- **SendGrid**: Email delivery service
- **AWS SES**: Amazon Simple Email Service
- **Mailgun**: Email API service

#### Object Storage (for user avatars, images)
- **AWS S3**: Object storage
- **MinIO**: Self-hosted S3-compatible storage
- **Cloudinary**: Image hosting and transformation

#### Caching Layer
- **Redis** (^7.0.0): In-memory data store for caching
  - Docker: `docker run -d -p 6379:6379 redis:7`

#### Message Queue (for async processing)
- **RabbitMQ** (^3.12.0): Message broker
- **Apache Kafka** (^3.5.0): Distributed event streaming


## Project Structure

### Backend Structure

```
backend/
├── auth_service/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization, CORS, middleware
│   ├── models.py            # SQLAlchemy User model
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── routes.py            # API route handlers
│   ├── database.py          # Database connection and session management
│   ├── auth.py              # JWT token creation/verification, password hashing
│   ├── metrics.py           # Prometheus metrics setup
│   ├── config.py            # Configuration and environment variables
│   ├── requirements.txt     # Python dependencies
│   └── tests/
│       ├── __init__.py
│       ├── test_auth.py     # Unit tests for authentication
│       └── test_routes.py   # Integration tests for routes
│
├── post_service/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── models.py            # SQLAlchemy Post model
│   ├── schemas.py           # Pydantic schemas
│   ├── routes.py            # API route handlers
│   ├── database.py          # Database connection
│   ├── auth.py              # JWT verification (shared with auth_service)
│   ├── metrics.py           # Prometheus metrics
│   ├── config.py            # Configuration
│   ├── requirements.txt
│   └── tests/
│       ├── __init__.py
│       ├── test_posts.py
│       └── test_routes.py
│
├── comment_service/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── models.py            # SQLAlchemy Comment model
│   ├── schemas.py           # Pydantic schemas
│   ├── routes.py            # API route handlers
│   ├── database.py          # Database connection
│   ├── auth.py              # JWT verification
│   ├── metrics.py           # Prometheus metrics
│   ├── notifications.py     # Notification service client
│   ├── config.py            # Configuration
│   ├── requirements.txt
│   └── tests/
│       ├── __init__.py
│       ├── test_comments.py
│       └── test_notifications.py
│
├── notification_service/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── models.py            # SQLAlchemy Notification model
│   ├── schemas.py           # Pydantic schemas
│   ├── routes.py            # API route handlers
│   ├── database.py          # Database connection
│   ├── metrics.py           # Prometheus metrics
│   ├── config.py            # Configuration
│   ├── requirements.txt
│   └── tests/
│       ├── __init__.py
│       └── test_notifications.py
│
├── shared/                  # Shared utilities (optional)
│   ├── __init__.py
│   ├── auth_utils.py        # Shared JWT utilities
│   └── logging_config.py    # Shared logging configuration
│
├── docker-compose.yml       # Multi-service Docker setup
├── .env.example             # Example environment variables
└── README.md                # Backend setup instructions
```

### Frontend Structure

```
frontend/
├── public/
│   └── vite.svg             # Favicon and static assets
│
├── src/
│   ├── components/          # Reusable React components
│   │   ├── Navbar.tsx       # Navigation bar with auth state
│   │   ├── PostCard.tsx     # Blog post card component
│   │   ├── CommentList.tsx  # Comment list component
│   │   ├── CommentForm.tsx  # Comment submission form
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorMessage.tsx
│   │   └── ProtectedRoute.tsx  # Route guard for authenticated pages
│   │
│   ├── pages/               # Page components
│   │   ├── LoginPage.tsx    # Login page
│   │   ├── RegisterPage.tsx # Registration page
│   │   ├── HomePage.tsx     # Blog feed (all posts)
│   │   ├── CreatePostPage.tsx  # Post creation page
│   │   ├── PostPage.tsx     # Single post view with comments
│   │   └── NotificationsPage.tsx  # User notifications
│   │
│   ├── services/            # API service layer
│   │   ├── api.ts           # Axios instance with interceptors
│   │   ├── authService.ts   # Auth API calls
│   │   ├── postService.ts   # Post API calls
│   │   ├── commentService.ts  # Comment API calls
│   │   └── notificationService.ts  # Notification API calls
│   │
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts       # Authentication state hook
│   │   ├── usePosts.ts      # Posts data fetching hook
│   │   └── useNotifications.ts  # Notifications hook
│   │
│   ├── types/               # TypeScript type definitions
│   │   ├── user.ts          # User types
│   │   ├── post.ts          # Post types
│   │   ├── comment.ts       # Comment types
│   │   └── notification.ts  # Notification types
│   │
│   ├── context/             # React context providers
│   │   └── AuthContext.tsx  # Authentication context
│   │
│   ├── utils/               # Utility functions
│   │   ├── formatDate.ts    # Date formatting
│   │   └── tokenStorage.ts  # LocalStorage token management
│   │
│   ├── App.tsx              # Main app component with routing
│   ├── main.tsx             # React entry point
│   ├── index.css            # Global styles and Tailwind imports
│   └── vite-env.d.ts        # Vite type definitions
│
├── .eslintrc.json           # ESLint configuration
├── .prettierrc              # Prettier configuration
├── tailwind.config.js       # TailwindCSS configuration
├── postcss.config.js        # PostCSS configuration
├── tsconfig.json            # TypeScript configuration
├── vite.config.ts           # Vite configuration
├── package.json             # Node dependencies and scripts
└── README.md                # Frontend setup instructions
```

### Configuration Files

#### Backend .env Example
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/amadop_db

# JWT
SECRET_KEY=your-secret-key-min-32-characters-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service URLs (for inter-service communication)
AUTH_SERVICE_URL=http://localhost:8001
POST_SERVICE_URL=http://localhost:8002
COMMENT_SERVICE_URL=http://localhost:8003
NOTIFICATION_SERVICE_URL=http://localhost:8004

# CORS
CORS_ORIGINS=http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

#### Frontend .env Example
```bash
VITE_AUTH_SERVICE_URL=http://localhost:8001
VITE_POST_SERVICE_URL=http://localhost:8002
VITE_COMMENT_SERVICE_URL=http://localhost:8003
VITE_NOTIFICATION_SERVICE_URL=http://localhost:8004
```

#### docker-compose.yml Example
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: amadop_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  auth_service:
    build: ./auth_service
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/amadop_db
      SECRET_KEY: your-secret-key-here
    depends_on:
      - postgres

  post_service:
    build: ./post_service
    ports:
      - "8002:8002"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/amadop_db
      AUTH_SERVICE_URL: http://auth_service:8001
    depends_on:
      - postgres

  comment_service:
    build: ./comment_service
    ports:
      - "8003:8003"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/amadop_db
      AUTH_SERVICE_URL: http://auth_service:8001
      NOTIFICATION_SERVICE_URL: http://notification_service:8004
    depends_on:
      - postgres

  notification_service:
    build: ./notification_service
    ports:
      - "8004:8004"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/amadop_db
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      VITE_AUTH_SERVICE_URL: http://localhost:8001
      VITE_POST_SERVICE_URL: http://localhost:8002
      VITE_COMMENT_SERVICE_URL: http://localhost:8003
      VITE_NOTIFICATION_SERVICE_URL: http://localhost:8004

volumes:
  postgres_data:
```


## Development Setup

### Prerequisites Installation

#### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Install Node.js 18+
brew install node@18

# Install PostgreSQL 15
brew install postgresql@15
brew services start postgresql@15

# Install Docker (optional)
brew install --cask docker
```

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install PostgreSQL 15
sudo apt install postgresql-15 postgresql-contrib
sudo systemctl start postgresql

# Install Docker (optional)
sudo apt install docker.io docker-compose
sudo systemctl start docker
```

### Database Setup

```bash
# Create database
psql -U postgres
CREATE DATABASE amadop_db;
CREATE USER amadop_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE amadop_db TO amadop_user;
\q

# Or use Docker
docker run -d \
  --name amadop-postgres \
  -e POSTGRES_DB=amadop_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15
```

### Backend Setup

#### Auth Service
```bash
cd backend/auth_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations (create tables)
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# In a new terminal, run tests
pytest tests/ -v --cov=.
```

#### Post Service
```bash
cd backend/post_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run database migrations
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Run tests
pytest tests/ -v --cov=.
```

#### Comment Service
```bash
cd backend/comment_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run database migrations
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8003 --reload

# Run tests
pytest tests/ -v --cov=.
```

#### Notification Service
```bash
cd backend/notification_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run database migrations
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8004 --reload

# Run tests
pytest tests/ -v --cov=.
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Edit .env with service URLs

# Run development server
npm run dev

# In a new terminal, run tests
npm run test

# Run linting
npm run lint

# Format code
npm run format

# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker Setup (Alternative)

```bash
# From project root
cd backend

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Verification Steps

#### 1. Check Service Health
```bash
# Auth Service
curl http://localhost:8001/health

# Post Service
curl http://localhost:8002/health

# Comment Service
curl http://localhost:8003/health

# Notification Service
curl http://localhost:8004/health
```

#### 2. Check Metrics Endpoints
```bash
# Auth Service metrics
curl http://localhost:8001/metrics

# Post Service metrics
curl http://localhost:8002/metrics
```

#### 3. Test API Endpoints
```bash
# Register a user
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# Create a post (replace TOKEN with actual token from login)
curl -X POST http://localhost:8002/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"title": "Test Post", "content": "This is a test post"}'

# Get all posts
curl http://localhost:8002/posts
```

#### 4. Access Frontend
```
Open browser to http://localhost:5173
```

### Troubleshooting

#### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check database exists
psql -U postgres -l | grep amadop_db

# Reset database (WARNING: deletes all data)
psql -U postgres -c "DROP DATABASE amadop_db;"
psql -U postgres -c "CREATE DATABASE amadop_db;"
```

#### Port Already in Use
```bash
# Find process using port 8001
lsof -i :8001

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8005
```

#### CORS Issues
```bash
# Verify CORS_ORIGINS in .env matches frontend URL
# Default: http://localhost:5173

# Check browser console for CORS errors
# Update CORS middleware in main.py if needed
```

#### Module Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.11+
```

### Development Workflow

#### Making Changes
```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make code changes

# 3. Run tests
pytest tests/ -v

# 4. Run linting
black . && flake8 .

# 5. Commit changes
git add .
git commit -m "Add your feature"

# 6. Push to remote
git push origin feature/your-feature-name
```

#### Running All Tests
```bash
# Backend tests (from each service directory)
pytest tests/ -v --cov=. --cov-report=html

# Frontend tests
npm run test

# Integration tests (requires all services running)
pytest tests/integration/ -v
```

#### Code Quality Checks
```bash
# Backend
black .                    # Format code
flake8 .                   # Lint code
mypy .                     # Type checking

# Frontend
npm run lint               # ESLint
npm run format             # Prettier
npm run type-check         # TypeScript checking
```


## Deployment Considerations

### Production Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer / CDN"
        LB[Nginx / Traefik<br/>SSL Termination]
        CDN[CloudFlare / CloudFront<br/>Static Assets]
    end
    
    subgraph "Application Servers"
        AUTH1[Auth Service<br/>Instance 1]
        AUTH2[Auth Service<br/>Instance 2]
        POST1[Post Service<br/>Instance 1]
        POST2[Post Service<br/>Instance 2]
        COMMENT1[Comment Service<br/>Instance 1]
        NOTIF1[Notification Service<br/>Instance 1]
    end
    
    subgraph "Data Layer"
        DB_PRIMARY[(PostgreSQL<br/>Primary)]
        DB_REPLICA[(PostgreSQL<br/>Read Replica)]
    end
    
    subgraph "Monitoring"
        PROM[Prometheus]
        GRAF[Grafana]
        ALERT[AlertManager]
    end
    
    LB --> AUTH1
    LB --> AUTH2
    LB --> POST1
    LB --> POST2
    LB --> COMMENT1
    LB --> NOTIF1
    
    CDN --> LB
    
    AUTH1 --> DB_PRIMARY
    AUTH2 --> DB_PRIMARY
    POST1 --> DB_PRIMARY
    POST2 --> DB_REPLICA
    COMMENT1 --> DB_PRIMARY
    NOTIF1 --> DB_PRIMARY
    
    PROM --> AUTH1
    PROM --> AUTH2
    PROM --> POST1
    PROM --> POST2
    PROM --> COMMENT1
    PROM --> NOTIF1
    
    GRAF --> PROM
    ALERT --> PROM
```

### Container Deployment (Docker)

#### Dockerfile Example (Auth Service)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
```

#### Dockerfile Example (Frontend)
```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Kubernetes Deployment

#### Deployment YAML Example (Auth Service)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  labels:
    app: auth-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: amadop/auth-service:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: auth-service
spec:
  selector:
    app: auth-service
  ports:
  - protocol: TCP
    port: 8001
    targetPort: 8001
  type: ClusterIP
```

### Environment-Specific Configuration

#### Development
```bash
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://postgres:password@localhost:5432/amadop_dev
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### Staging
```bash
# .env.staging
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@staging-db.example.com:5432/amadop_staging
CORS_ORIGINS=https://staging.amadop.com
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

#### Production
```bash
# .env.production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/amadop_prod
CORS_ORIGINS=https://amadop.com,https://www.amadop.com
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
RATE_LIMIT_ENABLED=true
```

### CI/CD Pipeline

#### GitHub Actions Example
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend/auth_service
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend/auth_service
        pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/auth_service/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run tests
      run: |
        cd frontend
        npm run test
    
    - name: Build
      run: |
        cd frontend
        npm run build

  deploy-staging:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to staging
      run: |
        # Deploy to staging environment
        echo "Deploying to staging..."

  deploy-production:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Deploy to production environment
        echo "Deploying to production..."
```

### Monitoring and Observability Setup

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:8001']
    metrics_path: '/metrics'
  
  - job_name: 'post-service'
    static_configs:
      - targets: ['post-service:8002']
    metrics_path: '/metrics'
  
  - job_name: 'comment-service'
    static_configs:
      - targets: ['comment-service:8003']
    metrics_path: '/metrics'
  
  - job_name: 'notification-service'
    static_configs:
      - targets: ['notification-service:8004']
    metrics_path: '/metrics'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts.yml'
```

#### Alert Rules
```yaml
# alerts.yml
groups:
  - name: service_alerts
    interval: 30s
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "{{ $labels.job }} has been down for more than 1 minute"
      
      - alert: HighErrorRate
        expr: rate(http_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value }} errors/sec"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency on {{ $labels.job }}"
          description: "P95 latency is {{ $value }} seconds"
```

### Backup and Disaster Recovery

#### Database Backup Script
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="amadop_prod"

# Create backup
pg_dump -U postgres -h db-host $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://amadop-backups/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

#### Restore Script
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: ./restore.sh <backup_file>"
  exit 1
fi

# Restore from backup
gunzip -c $BACKUP_FILE | psql -U postgres -h db-host amadop_prod

echo "Restore completed from $BACKUP_FILE"
```

### Scaling Strategies

#### Horizontal Scaling
- Add more service instances behind load balancer
- Use Kubernetes HorizontalPodAutoscaler
- Scale based on CPU, memory, or custom metrics (request rate)

#### Vertical Scaling
- Increase CPU and memory for service containers
- Upgrade database instance size
- Optimize database queries and indexes

#### Database Scaling
- Implement read replicas for read-heavy operations
- Use connection pooling (PgBouncer)
- Consider database sharding for very large datasets
- Implement caching layer (Redis) for frequently accessed data


## Future Enhancements

### Phase 2 Features

#### User Profile Management
- User profile pages with bio, avatar, social links
- Edit profile functionality
- User post history and statistics
- Follow/unfollow users
- User activity feed

#### Rich Text Editor
- Markdown support for post content
- WYSIWYG editor (TipTap, Quill, or Draft.js)
- Image upload and embedding
- Code syntax highlighting
- Preview mode

#### Advanced Commenting
- Nested comments (replies to comments)
- Comment editing and deletion
- Comment voting (upvote/downvote)
- Comment sorting (newest, oldest, most voted)
- Mention users with @username

#### Search and Filtering
- Full-text search for posts
- Search by author, tags, date range
- Filter posts by category or tags
- Elasticsearch integration for advanced search

#### Tagging System
- Add tags to posts
- Tag-based post filtering
- Popular tags widget
- Tag autocomplete

#### Real-Time Features
- WebSocket support for live notifications
- Real-time comment updates
- Online user presence indicators
- Live post view counts

### Phase 3 Features

#### Content Moderation
- Admin dashboard for content moderation
- Flag inappropriate content
- User reporting system
- Automated content filtering (profanity, spam)
- Moderator roles and permissions

#### Analytics and Insights
- Post view tracking
- User engagement metrics
- Popular posts dashboard
- Author analytics (views, comments, engagement)
- Export analytics data

#### Email Notifications
- Email notifications for comments
- Daily/weekly digest emails
- Email verification for registration
- Password reset via email
- Configurable notification preferences

#### Social Features
- Share posts on social media
- Social login (OAuth with Google, GitHub, Twitter)
- Post bookmarking/favorites
- Reading lists
- Post recommendations based on user interests

#### Performance Optimizations
- Redis caching layer
- CDN integration for static assets
- Database query optimization
- Lazy loading for images
- Infinite scroll for post feed

### DevOps Integration (AMADOP Phase)

#### Autonomous Monitoring
- AI-powered anomaly detection
- Predictive scaling based on traffic patterns
- Automated performance optimization
- Self-healing service recovery

#### Intelligent Alerting
- Context-aware alert prioritization
- Automated incident response
- Root cause analysis
- Alert fatigue reduction

#### Automated Deployment
- Canary deployments with automatic rollback
- Blue-green deployment strategy
- Feature flag management
- A/B testing infrastructure

#### Cost Optimization
- Resource usage optimization
- Automated scaling policies
- Cost anomaly detection
- Infrastructure right-sizing recommendations

### Technical Debt and Improvements

#### Code Quality
- Increase test coverage to 90%+
- Add more property-based tests
- Implement mutation testing
- Add E2E tests with Playwright

#### Security Enhancements
- Implement rate limiting
- Add CAPTCHA for registration/login
- Two-factor authentication (2FA)
- Security audit and penetration testing
- Implement Content Security Policy (CSP)

#### API Improvements
- GraphQL API as alternative to REST
- API versioning strategy
- API documentation with OpenAPI/Swagger
- API rate limiting per user
- Webhook support for integrations

#### Database Optimizations
- Implement database migrations with Alembic
- Add database indexes based on query patterns
- Implement soft deletes for data recovery
- Add database query logging and analysis
- Implement database connection pooling optimization

### Integration Opportunities

#### Third-Party Services
- AWS S3 for file storage
- SendGrid/Mailgun for email delivery
- Cloudinary for image processing
- Stripe for premium features/subscriptions
- Google Analytics for user tracking

#### API Integrations
- RSS feed generation
- REST API for mobile apps
- Webhook endpoints for external integrations
- Import/export functionality (Medium, WordPress)

### Mobile Application

#### React Native App
- Native mobile app for iOS and Android
- Push notifications
- Offline reading mode
- Mobile-optimized UI
- Camera integration for image uploads

### Accessibility Improvements

#### WCAG 2.1 AA Compliance
- Screen reader optimization
- Keyboard navigation support
- High contrast mode
- Focus indicators
- ARIA labels and roles
- Alt text for images
- Accessible forms with proper labels

### Internationalization (i18n)

#### Multi-Language Support
- UI translation framework (react-i18next)
- Language selection
- RTL (Right-to-Left) language support
- Date/time localization
- Number formatting localization

## Conclusion

This design document provides a comprehensive blueprint for the AMADOP Blogging Platform application layer. The microservices architecture ensures scalability, maintainability, and observability, while the modern tech stack (Python/FastAPI, React, PostgreSQL) provides a solid foundation for rapid development and deployment.

The platform is designed with DevOps automation in mind, featuring standardized health checks, Prometheus metrics, and structured logging across all services. This observability layer will enable the future AMADOP orchestration system to monitor, analyze, and autonomously manage the platform.

Key design principles followed:
- **Separation of Concerns**: Each service has a single, well-defined responsibility
- **Stateless Services**: All services are stateless, enabling horizontal scaling
- **API-First Design**: RESTful APIs with clear contracts and validation
- **Security by Default**: JWT authentication, password hashing, input validation
- **Observability**: Health checks, metrics, and structured logging throughout
- **Testability**: Comprehensive testing strategy with unit, property-based, and integration tests
- **Production-Ready**: Error handling, graceful degradation, and monitoring

The implementation can proceed incrementally, starting with core services (Auth, Post) and expanding to additional features (Comments, Notifications) and enhancements (search, real-time updates, analytics) in subsequent phases.
