# PROJECT TODO - Code Review Findings

## Executive Summary

This document contains findings from a comprehensive code review of the Terean fullstack application. The review identified several critical issues that should be addressed:

### 🔴 Critical Issues (Immediate Action Required)
1. **Security Vulnerabilities**
   - CORS set to allow all origins (`*`)
   - JWT tokens stored in localStorage (XSS vulnerable)

2. **Data Loss Risk**
   - No database migrations system
   - No soft deletes
   - No backup strategy

### 🟡 High Priority Issues (Address Within 1-2 Weeks)
1. **Performance Problems**
   - No pagination on some endpoints
   - Synchronous file operations blocking event loop
   - Large files loaded entirely into memory

2. **Code Quality**
   - TypeScript disabled in main API file (`@ts-nocheck`)
   - Extensive console.log statements in production
   - 700+ line component files

3. **Missing Core Features**
   - No test coverage
   - No proper logging/monitoring

### 🟢 Medium Priority (Address Within 1 Month)
1. **Technical Debt**
   - Duplicate code across file upload endpoints
   - Inconsistent error handling

2. **Developer Experience**
   - Poor documentation
   - No development environment setup
   - Mixed coding patterns

### Quick Wins
- Enable TypeScript checking
- Add rate limiting middleware
- Extract file upload logic to shared utility
- Add health check endpoint

---

## 1. Unused/Underutilized Backend Endpoints

### Potentially Unused Endpoints
These endpoints appear to have no frontend usage:

1. **`GET /projects/{file_id}/sgy`** (`main.py:462`)
   - Downloads SGY files as zip
   - No frontend reference found
   - Path naming is confusing (uses `projects/` but parameter is `file_id`)

2. **`GET /projects/{file_id}/raw_data`** (`main.py:491`)
   - Downloads raw data zip
   - No frontend reference found
   - Same path confusion as above

3. **`GET /projects/{file_id}/processor_zip`** (`main.py:504`)
   - Downloads processor-ready zip
   - No frontend reference found

4. **`POST /generateResultsEmail`** (`main.py:519`)
   - Generates and sends email with velocity model results
   - Only used via the HTML form endpoint below

5. **`GET /projects/{file_id}/results_email_form`** (`main.py:570`)
   - Returns raw HTML form for email generation
   - Not integrated with React frontend

## 2. Potential Bugs & Error-Prone Areas

### Backend Issues

1. **Database Transaction Issues**
   - `project_router.py:730` - Updates project in DB within file upload loop
   - Should use single transaction for atomicity

2. **Error Handling Inconsistencies**
   - Some endpoints use `print()` for errors (e.g., `main.py:403`)
   - Should consistently use logger
   - Generic error messages hide actual problems

3. **Resource Leaks**
   - Temporary files created but not always cleaned up (e.g., `main.py:217`)
   - Background tasks used inconsistently for cleanup

### Frontend Issues

1. **TypeScript Disabled**
   - `api.ts:2` - `// @ts-nocheck` disables all type checking
   - Defeats purpose of using TypeScript

2. **Inconsistent Error Handling**
   - Some API calls have try-catch, others don't
   - No global error handler for API responses

3. **FormData Usage Issues**
   - `api.ts:164` - Manually setting Content-Type for multipart/form-data
   - Should let browser set it with boundary

4. **State Management**
   - Redux slices have inconsistent patterns
   - Some use `extraReducers`, others don't handle async properly

## 3. Code Quality & Technical Debt

### Backend

1. **Commented Out Code**
   - `main.py:14` - `# import pycuda.autoinit` - Remove or document why
   - Multiple TODO comments without tracking

2. **Hardcoded Values**
   - `main.py:119-123` - Hardcoded allowed origins
   - Should be in environment config

3. **Function Length**
   - `process_2dp` (100+ lines) and `process_2ds` (150+ lines) too long
   - Should be refactored into smaller functions

4. **Duplicate Code**
   - File upload logic duplicated across multiple endpoints
   - Should be extracted to utility functions

5. **Magic Numbers**
   - Default values scattered throughout (e.g., `smoothing=20`)
   - Should be constants

### Frontend

1. **Component Complexity**
   - `Quick2dSForm.tsx` and `Quick2dPForm.tsx` are 700+ lines
   - Should be broken into smaller components

2. **Inline Styles**
   - Mixed usage of CSS files and inline styles
   - Should have consistent styling approach

3. **Console Logs**
   - Extensive console.log statements in production code
   - Should use proper logging library

## 4. Security Concerns

1. **SQL Injection Risk**
   - Raw string interpolation in some queries
   - Though SQLAlchemy provides some protection

2. **Missing Rate Limiting**
   - No rate limiting on file uploads or processing endpoints
   - Could lead to DoS

3. **Token Storage**
   - JWT tokens stored in localStorage (XSS vulnerable)
   - Should consider httpOnly cookies

4. **CORS Too Permissive**
   - `allow_origins=["*"]` in production is dangerous
   - Should restrict to specific domains

## 5. Performance Issues

1. **Synchronous File Operations**
   - Some file operations not using async (`os.path.getsize()`)
   - Blocks event loop

2. **Large File Handling**
   - No streaming for large file uploads
   - Entire file loaded into memory

3. **Database Queries**
   - No pagination in some list endpoints
   - Could return thousands of records

4. **Missing Caching**
   - Frequently accessed data (projects, geometry) not cached
   - Every request hits database

## 6. Missing Features & Improvements

### High Priority

1. **Database Migrations**
   - Currently using `create_all()` - No migration system
   - Need Alembic for schema versioning

2. **API Documentation**
   - Inconsistent docstrings
   - Should generate OpenAPI docs properly

3. **Test Coverage**
   - Very few tests exist
   - Need unit and integration tests

4. **Logging & Monitoring**
   - No structured logging
   - No APM or error tracking

5. **Background Job Queue**
   - Long-running processes block requests
   - Need Celery or similar

### Medium Priority

1. **File Cleanup Job**
   - Orphaned files never cleaned up
   - Need periodic cleanup task

2. **Audit Trail**
   - No tracking of who changed what
   - Important for compliance

### Low Priority

1. **Email Templates**
   - HTML email hardcoded in Python
   - Should use template engine

## 7. Refactoring Recommendations

### Immediate Actions

1. **Fix Security Issues**
   - Restrict CORS
   - Add rate limiting


### Short Term (1-2 weeks)

1. **Extract Common Code**
   - File upload utilities
   - Path validation helpers
   - Response formatting

2. **Add Basic Tests**
   - Critical path tests
   - Security test cases
   - API contract tests

3. **Improve Type Safety**
   - Remove @ts-nocheck
   - Add proper types
   - Enable strict mode

### Long Term (1-2 months)

1. **Implement Proper Architecture**
   - Service layer pattern
   - Repository pattern for DB
   - Dependency injection

2. **Add Missing Infrastructure**
   - Message queue
   - Caching layer
   - Monitoring

3. **Refactor Large Components**
   - Break down forms
   - Extract business logic
   - Create reusable components

## 8. Database Schema Issues

1. **JSON Fields Overuse**
   - Complex data stored as JSON strings
   - Should consider proper relational design

2. **Missing Indexes**
   - No indexes on frequently queried fields
   - Will cause performance issues at scale

3. **No Soft Deletes**
   - Records permanently deleted
   - No recovery possible

## 9. DevOps & Deployment

1. **No Health Checks**
   - No endpoint to verify service health
   - Makes monitoring difficult

2. **Missing Environment Configs**
   - Dev/staging/prod not properly separated
   - Same config for all environments

3. **No CI/CD Pipeline**
   - Manual deployment process
   - No automated testing

## 10. Documentation Gaps

1. **API Documentation**
   - Endpoints not consistently documented
   - No examples provided

2. **Setup Instructions**
   - README lacks detailed setup
   - Dependencies not fully documented

3. **Architecture Diagrams**
   - No visual representation of system
   - Hard to understand data flow

## 11. Specific Bug-Prone Code Patterns

### Backend Patterns to Fix

1. **String Concatenation for Paths**
   ```python
   # BAD - Found in multiple places
   file_path = f"{data_dir}/Zips/{file_id}.zip"
   
   # GOOD
   file_path = os.path.join(data_dir, "Zips", f"{file_id}.zip")
   ```

2. **Print Instead of Logger**
   ```python
   # BAD - Found in main.py:403
   print("ERROR Reading file ", vel_model.filename)
   
   # GOOD
   logger.error(f"Error reading file: {vel_model.filename}")
   ```

3. **Bare Except Clauses**
   ```python
   # BAD
   except Exception as e:
       raise HTTPException(400, "Failed to parse excel file.")
   
   # GOOD
   except ValueError as e:
       logger.error(f"Excel parsing failed: {e}")
       raise HTTPException(400, f"Invalid Excel format: {str(e)}")
   ```

### Frontend Patterns to Fix

1. **Disabled TypeScript**
   ```typescript
   // BAD - api.ts:2
   // @ts-nocheck
   
   // GOOD - Fix types instead of disabling
   ```

2. **Console Logs in Production**
   ```typescript
   // BAD - Found throughout
   console.log("=== Upload Response ===");
   
   // GOOD - Use proper logging
   logger.debug("Upload response received", { status, data });
   ```

3. **Inconsistent Async Handling**
   ```typescript
   // BAD - No error handling
   const response = await api.get(`/project/${projectId}/options`);
   
   // GOOD
   try {
     const response = await api.get(`/project/${projectId}/options`);
     return response.data;
   } catch (error) {
     logger.error('Failed to fetch options', { projectId, error });
     throw new ApiError('Failed to fetch project options', error);
   }
   ```

4. **Manual FormData Headers**
   ```typescript
   // BAD - api.ts
   headers: { 'Content-Type': 'multipart/form-data' }
   
   // GOOD - Let browser set boundary
   // Don't set Content-Type for FormData
   ```

### Database Anti-Patterns

1. **Multiple Commits in Loop**
   ```python
   # BAD - project_router.py:730
   for file in files:
       # ... process file
       db.commit()  # Commits inside loop
   
   # GOOD - Single transaction
   for file in files:
       # ... process file
   db.commit()  # One commit after all processing
   ```

2. **No Connection Pooling**
   - Current setup creates new connections
   - Should use connection pool for better performance

3. **JSON String Storage**
   ```python
   # Current - Everything stored as JSON strings
   record_options = json.dumps(data)
   
   # Better - Use PostgreSQL JSONB or proper relations
   ```

## 12. Recommended Development Workflow Improvements

1. **Pre-commit Hooks**
   - ESLint/Prettier for frontend
   - Black/isort for backend
   - Security scanning

2. **API Contract Testing**
   - OpenAPI schema validation
   - Contract tests between frontend/backend

3. **Feature Flags**
   - Safely deploy incomplete features
   - A/B testing capability

4. **Observability**
   - Structured logging with correlation IDs
   - Distributed tracing
   - Performance metrics

5. **Development Environment**
   - Docker-compose for local development
   - Seed data scripts
   - Hot reloading for both frontend/backend


### Admin Endpoints Without Frontend

The admin router (`/admin/*`) has these endpoints with no frontend UI:
- `GET /admin/users` - Get all users
- `GET /admin/users/{username}` - Get specific user
- `POST /admin/register_user` - Create new user
- `PUT /admin/users/{username}` - Update user
- `PATCH /admin/disable_user/{username}` - Toggle user disabled status

All require auth_level 3 (admin) but have no admin interface in the React app. 
