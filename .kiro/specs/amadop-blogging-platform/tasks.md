# Implementation Plan: AMADOP Blogging Platform

## Overview

This implementation plan breaks down the AMADOP Blogging Platform into manageable, sequential tasks. The system consists of 4 Python/FastAPI microservices (Auth, Post, Comment, Notification) and a React/TypeScript frontend. Each task builds incrementally, with checkpoints to ensure stability before proceeding.

## Tasks

- [x] 1. Project setup and infrastructure
  - Create backend folder structure for 4 services (auth_service, post_service, comment_service, notification_service)
  - Create frontend folder structure with React/Vite
  - Set up PostgreSQL database
  - Create requirements.txt for each backend service
  - Create package.json for frontend
  - Create .env.example files for configuration
  - Create docker-compose.yml for local development
  - _Requirements: All services_

- [ ] 2. Shared utilities and database foundation
  - [x] 2.1 Create shared database configuration module
    - Implement database.py with SQLAlchemy engine and session management
    - Add connection pooling configuration
    - _Requirements: 10.3, 13.5_
  
  - [x] 2.2 Create shared authentication utilities
    - Implement JWT token creation function with HS256 algorithm
    - Implement JWT token verification function
    - Implement password hashing with bcrypt
    - Implement password verification function
    - _Requirements: 1.6, 2.4, 2.5, 2.6, 14.1, 14.3, 14.4_
  
  - [ ]* 2.3 Write property test for password hashing
    - **Property 1: Password Security**
    - **Validates: Requirements 1.6, 14.1, 14.6**
  
  - [ ]* 2.4 Write property test for JWT token validity
    - **Property 2: JWT Token Validity**
    - **Validates: Requirements 2.4, 2.5, 2.6, 14.3, 14.4**
  
  - [x] 2.5 Create shared metrics module
    - Implement Prometheus metrics collectors (request counter, latency histogram, error counter)
    - Create middleware for automatic metrics collection
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [ ] 3. Auth Service implementation
  - [x] 3.1 Create Auth Service data model
    - Define User model with SQLAlchemy (id, username, email, password_hash, created_at)
    - Add unique constraints and indexes
    - Create database initialization script
    - _Requirements: 1.1, 1.6, 1.7, 12.2, 12.3_
  
  - [x] 3.2 Implement user registration endpoint
    - Create Pydantic schemas for UserRegister and UserResponse
    - Implement POST /register route handler
    - Add username uniqueness validation
    - Add email uniqueness validation
    - Add password length validation (min 8 characters)
    - Hash password with bcrypt before storage
    - Return 201 status with user data (excluding password)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_
  
  - [ ]* 3.3 Write unit tests for user registration
    - Test successful registration
    - Test duplicate username error
    - Test duplicate email error
    - Test invalid email format error
    - Test short password error
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 3.4 Implement user login endpoint
    - Create Pydantic schemas for UserLogin and Token
    - Implement POST /login route handler
    - Verify username exists
    - Verify password with bcrypt
    - Generate JWT token with 30-minute expiration
    - Include user_id and username in token payload
    - Return token with "bearer" type
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 3.5 Write unit tests for user login
    - Test successful login returns JWT token
    - Test invalid username returns 401
    - Test invalid password returns 401
    - Test token contains correct claims
    - Test token expiration is 30 minutes
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 3.6 Implement current user endpoint
    - Create JWT dependency for route protection
    - Implement GET /me route handler
    - Verify JWT token and extract user_id
    - Query database for user details
    - Return UserResponse
    - _Requirements: 2.6, 2.7_
  
  - [x] 3.7 Add health check and metrics endpoints
    - Implement GET /health endpoint (check database connection)
    - Implement GET /metrics endpoint (Prometheus format)
    - Add metrics middleware to track all requests
    - _Requirements: 10.1, 10.2, 10.4, 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [x] 3.8 Create Auth Service main application
    - Initialize FastAPI app
    - Configure CORS middleware for frontend
    - Register all routes
    - Add metrics middleware
    - Configure Uvicorn to run on port 8001
    - _Requirements: All Auth Service requirements_

- [x] 4. Checkpoint - Auth Service validation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Post Service implementation
  - [x] 5.1 Create Post Service data model
    - Define Post model with SQLAlchemy (id, title, content, author_id, created_at)
    - Add indexes on author_id and created_at
    - Create database initialization script
    - _Requirements: 3.1, 3.6, 3.7, 12.4, 12.5_
  
  - [x] 5.2 Implement post creation endpoint
    - Create Pydantic schemas for PostCreate and PostResponse
    - Implement POST /posts route handler with JWT authentication
    - Validate title length (1-200 characters)
    - Validate content is non-empty
    - Extract author_id from JWT token
    - Store post in database
    - Return 201 status with post data
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [ ]* 5.3 Write unit tests for post creation
    - Test successful post creation
    - Test unauthorized access returns 401
    - Test invalid token returns 401
    - Test empty title returns 422
    - Test title too long returns 422
    - Test empty content returns 422
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 5.4 Implement get all posts endpoint
    - Implement GET /posts route handler
    - Add pagination with skip and limit parameters (max 100)
    - Order posts by created_at descending
    - Return list of PostResponse
    - _Requirements: 4.1, 4.2, 4.5, 4.6_
  
  - [ ]* 5.5 Write property test for post ordering
    - **Property 7: Chronological Ordering**
    - **Validates: Requirement 4.1**
  
  - [x] 5.6 Implement get single post endpoint
    - Implement GET /posts/{post_id} route handler
    - Query post by ID
    - Return 404 if post not found
    - Return PostResponse if found
    - _Requirements: 4.3, 4.4, 4.5_
  
  - [x] 5.7 Implement delete post endpoint
    - Implement DELETE /posts/{post_id} route handler with JWT authentication
    - Verify user is the post author
    - Return 403 if user is not the author
    - Return 404 if post not found
    - Return 401 if not authenticated
    - Delete post and return 204 status
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [ ]* 5.8 Write unit tests for post deletion
    - Test author can delete own post
    - Test non-author cannot delete post (403)
    - Test deleting non-existent post returns 404
    - Test unauthenticated deletion returns 401
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 5.9 Add health check and metrics endpoints
    - Implement GET /health endpoint
    - Implement GET /metrics endpoint
    - Add metrics middleware
    - _Requirements: 10.1, 10.2, 10.5, 11.1, 11.5, 11.6_
  
  - [x] 5.10 Create Post Service main application
    - Initialize FastAPI app
    - Configure CORS middleware
    - Register all routes
    - Add metrics middleware
    - Configure Uvicorn to run on port 8002
    - _Requirements: All Post Service requirements_

- [x] 6. Checkpoint - Post Service validation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Notification Service implementation
  - [x] 7.1 Create Notification Service data model
    - Define Notification model with SQLAlchemy (id, user_id, message, read, created_at)
    - Add indexes on user_id and composite index on (user_id, read)
    - Create database initialization script
    - _Requirements: 8.3, 8.5, 9.3, 12.7_
  
  - [x] 7.2 Implement create notification endpoint
    - Create Pydantic schemas for NotificationCreate and NotificationResponse
    - Implement POST /notifications route handler
    - Validate message length (1-500 characters)
    - Store notification with read=False
    - Return 201 status with notification data
    - _Requirements: 8.3, 8.5, 12.7_
  
  - [x] 7.3 Implement get user notifications endpoint
    - Implement GET /notifications/{user_id} route handler
    - Add optional unread_only query parameter
    - Filter by user_id and optionally by read=False
    - Order by created_at descending
    - Return list of NotificationResponse
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [x] 7.4 Implement mark notification as read endpoint
    - Implement PATCH /notifications/{notification_id}/read route handler
    - Update read flag to True
    - Return 404 if notification not found
    - Return 204 status on success
    - _Requirements: 9.5_
  
  - [ ]* 7.5 Write unit tests for notification service
    - Test notification creation
    - Test get all notifications for user
    - Test get unread notifications only
    - Test mark notification as read
    - Test empty notification list
    - _Requirements: 8.3, 9.1, 9.2, 9.4, 9.5_
  
  - [x] 7.6 Add health check and metrics endpoints
    - Implement GET /health endpoint
    - Implement GET /metrics endpoint
    - Add metrics middleware
    - _Requirements: 10.1, 10.2, 10.7, 11.1, 11.8_
  
  - [x] 7.7 Create Notification Service main application
    - Initialize FastAPI app
    - Configure CORS middleware
    - Register all routes
    - Add metrics middleware
    - Configure Uvicorn to run on port 8004
    - _Requirements: All Notification Service requirements_

- [ ] 8. Comment Service implementation
  - [x] 8.1 Create Comment Service data model
    - Define Comment model with SQLAlchemy (id, post_id, user_id, content, created_at)
    - Add indexes on post_id and user_id
    - Add composite index on (post_id, created_at)
    - Create database initialization script
    - _Requirements: 6.1, 6.6, 6.7, 12.6_
  
  - [x] 8.2 Create notification service client
    - Implement async HTTP client for notification service
    - Create function to trigger notification with timeout (2 seconds)
    - Implement graceful degradation (log error, don't fail)
    - _Requirements: 8.1, 8.4_
  
  - [x] 8.3 Implement create comment endpoint
    - Create Pydantic schemas for CommentCreate and CommentResponse
    - Implement POST /comments route handler with JWT authentication
    - Validate comment content length (1-1000 characters)
    - Verify post exists (call Post Service or query database)
    - Extract user_id from JWT token
    - Store comment in database
    - Get post author_id
    - If commenter != post author, trigger notification to post author
    - Return 201 status with comment data
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 8.1, 8.2, 8.4_
  
  - [ ]* 8.4 Write unit tests for comment creation
    - Test successful comment creation
    - Test unauthorized access returns 401
    - Test empty content returns 422
    - Test content too long returns 422
    - Test comment on non-existent post returns 404
    - Test notification triggered for other user's post
    - Test notification not triggered for own post
    - Test comment succeeds even if notification fails
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.1, 8.2, 8.4_
  
  - [ ]* 8.5 Write property test for notification delivery
    - **Property 5: Notification Delivery**
    - **Validates: Requirements 8.1, 8.3**
  
  - [x] 8.6 Implement get comments for post endpoint
    - Implement GET /comments/{post_id} route handler
    - Query all comments for post_id
    - Order by created_at ascending
    - Return empty list if no comments
    - Return list of CommentResponse
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [ ]* 8.7 Write unit tests for comment retrieval
    - Test get comments for post with comments
    - Test get comments for post with no comments
    - Test comments ordered by creation time
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 8.8 Add health check and metrics endpoints
    - Implement GET /health endpoint
    - Implement GET /metrics endpoint
    - Add metrics middleware
    - _Requirements: 10.1, 10.2, 10.6, 11.1, 11.7_
  
  - [x] 8.9 Create Comment Service main application
    - Initialize FastAPI app
    - Configure CORS middleware
    - Register all routes
    - Add metrics middleware
    - Configure Uvicorn to run on port 8003
    - _Requirements: All Comment Service requirements_

- [x] 9. Checkpoint - Backend services complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Frontend project setup
  - [x] 10.1 Initialize React project with Vite
    - Run `npm create vite@latest frontend -- --template react-ts`
    - Install dependencies: react-router-dom, axios
    - Install dev dependencies: tailwindcss, postcss, autoprefixer
    - Configure TailwindCSS with postcss.config.js and tailwind.config.js
    - Create src folder structure (components, pages, services, hooks, types, context, utils)
    - _Requirements: Frontend infrastructure_
  
  - [x] 10.2 Create TypeScript type definitions
    - Define User interface (id, username, email, created_at)
    - Define Post interface (id, title, content, author_id, author_username, created_at)
    - Define Comment interface (id, post_id, user_id, username, content, created_at)
    - Define Notification interface (id, user_id, message, read, created_at)
    - Define Token interface (access_token, token_type)
    - _Requirements: Type safety_
  
  - [x] 10.3 Create API service layer
    - Create axios instance with base configuration
    - Add request interceptor to attach JWT token from localStorage
    - Add response interceptor to handle 401 errors (redirect to login)
    - Create authService with register, login, getCurrentUser functions
    - Create postService with createPost, getAllPosts, getPost, deletePost functions
    - Create commentService with createComment, getCommentsForPost functions
    - Create notificationService with getUserNotifications, markNotificationRead functions
    - _Requirements: API communication_

- [ ] 11. Frontend authentication implementation
  - [x] 11.1 Create authentication context
    - Create AuthContext with user state and authentication functions
    - Implement login function (call API, store token, update state)
    - Implement logout function (clear token, clear state)
    - Implement register function (call API, auto-login)
    - Create useAuth hook for consuming context
    - _Requirements: 1.1, 2.1_
  
  - [x] 11.2 Create login page
    - Create LoginPage component with form (username, password)
    - Add form validation
    - Call authService.login on submit
    - Store token in localStorage
    - Redirect to home page on success
    - Display error message on failure
    - Style with TailwindCSS
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 11.3 Create registration page
    - Create RegisterPage component with form (username, email, password)
    - Add form validation (email format, password length)
    - Call authService.register on submit
    - Auto-login after successful registration
    - Redirect to home page on success
    - Display error messages on failure
    - Style with TailwindCSS
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 11.4 Create protected route component
    - Create ProtectedRoute component that checks authentication
    - Redirect to login if not authenticated
    - Render children if authenticated
    - _Requirements: Authorization_

- [ ] 12. Frontend blog post features
  - [x] 12.1 Create navigation bar component
    - Create Navbar component with links (Home, Create Post, Notifications)
    - Show login/register links if not authenticated
    - Show username and logout button if authenticated
    - Style with TailwindCSS
    - _Requirements: Navigation_
  
  - [x] 12.2 Create home page with post feed
    - Create HomePage component
    - Fetch all posts on mount using postService.getAllPosts
    - Display loading spinner while fetching
    - Render list of PostCard components
    - Show error message if fetch fails
    - Style with TailwindCSS
    - _Requirements: 4.1, 4.2_
  
  - [x] 12.3 Create post card component
    - Create PostCard component to display post summary
    - Show title, content preview (first 200 chars), author, date
    - Add "Read more" link to full post page
    - Style with TailwindCSS
    - _Requirements: 4.5_
  
  - [x] 12.4 Create post creation page
    - Create CreatePostPage component (protected route)
    - Add form with title and content fields
    - Add form validation (title length, content not empty)
    - Call postService.createPost on submit
    - Redirect to new post page on success
    - Display error message on failure
    - Style with TailwindCSS
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 12.5 Create single post page
    - Create PostPage component
    - Fetch post by ID from URL parameter
    - Display full post (title, content, author, date)
    - Show delete button if current user is author
    - Fetch and display comments below post
    - Show comment form if authenticated
    - Handle post not found (404)
    - Style with TailwindCSS
    - _Requirements: 4.3, 4.4, 5.1, 7.1_

- [ ] 13. Frontend comment features
  - [x] 13.1 Create comment list component
    - Create CommentList component to display comments
    - Show each comment with username, content, date
    - Order comments by creation time
    - Show "No comments yet" if empty
    - Style with TailwindCSS
    - _Requirements: 7.1, 7.2_
  
  - [x] 13.2 Create comment form component
    - Create CommentForm component (requires authentication)
    - Add textarea for comment content
    - Add character counter (max 1000)
    - Call commentService.createComment on submit
    - Refresh comment list after successful submission
    - Display error message on failure
    - Style with TailwindCSS
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 14. Frontend notification features
  - [x] 14.1 Create notifications page
    - Create NotificationsPage component (protected route)
    - Fetch user notifications on mount
    - Display list of notifications with message and date
    - Highlight unread notifications
    - Add "Mark as read" button for unread notifications
    - Show "No notifications" if empty
    - Style with TailwindCSS
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 14.2 Add notification badge to navbar
    - Fetch unread notification count
    - Display badge with count on notifications link
    - Update count when notifications are read
    - _Requirements: 9.2_

- [ ] 15. Frontend routing and app integration
  - [x] 15.1 Create main App component with routing
    - Set up React Router with routes for all pages
    - Add route for login (/login)
    - Add route for register (/register)
    - Add route for home (/)
    - Add route for create post (/posts/new) - protected
    - Add route for single post (/posts/:id)
    - Add route for notifications (/notifications) - protected
    - Wrap app with AuthContext provider
    - Include Navbar on all pages
    - _Requirements: All frontend requirements_
  
  - [x] 15.2 Create utility functions
    - Create formatDate function for displaying timestamps
    - Create tokenStorage functions (get, set, remove)
    - Create error handling utilities
    - _Requirements: Utilities_
  
  - [ ]* 15.3 Write frontend component tests
    - Test LoginPage form submission
    - Test RegisterPage form validation
    - Test PostCard rendering
    - Test CommentForm submission
    - Test protected route redirects
    - _Requirements: Frontend testing_

- [x] 16. Checkpoint - Frontend complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Integration and documentation
  - [x] 17.1 Create Docker Compose configuration
    - Define postgres service with volume
    - Define auth_service with environment variables
    - Define post_service with dependencies
    - Define comment_service with dependencies
    - Define notification_service with dependencies
    - Define frontend service
    - Configure service networking
    - _Requirements: Deployment_
  
  - [x] 17.2 Create environment configuration files
    - Create .env.example for backend services
    - Create .env.example for frontend
    - Document all required environment variables
    - _Requirements: Configuration_
  
  - [x] 17.3 Write README documentation
    - Document system architecture
    - Add prerequisites and installation instructions
    - Add local development setup steps
    - Add Docker setup instructions
    - Document API endpoints for each service
    - Add testing instructions
    - Add troubleshooting section
    - _Requirements: Documentation_
  
  - [ ]* 17.4 Write integration tests
    - Test complete user journey (register, login, create post, comment, notification)
    - Test cross-service communication
    - Test health checks for all services
    - Test metrics collection
    - _Requirements: Integration testing_
  
  - [ ]* 17.5 Write property tests for data integrity
    - **Property 3: Post Ownership**
    - **Validates: Requirement 13.1**
    - **Property 4: Comment Referential Integrity**
    - **Validates: Requirements 13.2, 13.3**

- [x] 18. Final checkpoint - System complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and allow for user feedback
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: shared utilities → backend services → frontend
- Services can be developed in parallel after shared utilities are complete
- Frontend development can begin once backend APIs are available
