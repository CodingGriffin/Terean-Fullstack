# Project Context

## Tech Stack
- **Frontend**: React 18, TypeScript, Vite (not Create React App), Redux Toolkit
- **Backend**: FastAPI, SQLAlchemy, Pydantic, Python 3.x
- **Database**: SQLAlchemy ORM (database type not specified in session)
- **File Storage**: Local filesystem in `{MQ_SAVE_DIR}/SGYFiles/{project_id}/`
- **Authentication**: OAuth2 with JWT tokens

## Project Structure
```
terean-fullstack/
├── backend/
│   ├── crud/           # Database CRUD operations
│   ├── models/         # SQLAlchemy models
│   ├── router/         # FastAPI route definitions
│   ├── schemas/        # Pydantic schemas
│   ├── settings/       # Configuration files (.env)
│   ├── utils/          # Utility functions
│   └── main.py         # Main FastAPI application
├── frontend/
│   ├── src/
│   │   ├── services/   # API client functions
│   │   ├── store/      # Redux store, slices, and thunks
│   │   ├── types/      # TypeScript type definitions
│   │   ├── Features/   # Feature components
│   │   ├── Pages/      # Page components
│   │   ├── Components/ # Reusable components
│   │   └── Contexts/   # React contexts
│   └── vite.config.ts  # Vite configuration
└── PROJECT_CONTEXT.md  # This file
```

## Key Architectural Decisions

### 1. File Upload Architecture
- **ID Generation**: Backend generates unique IDs using `generate_time_based_uid()`
- **Storage Pattern**: Files stored in `{MQ_SAVE_DIR}/SGYFiles/{project_id}/{file_id}.{extension}`
- **Metadata Storage**: Projects store file metadata in `record_options` JSON field
- **Flow**: Frontend uploads → Backend generates IDs → Files saved → Record options updated → Response sent

### 2. Data Model Patterns
- **Projects**: Core entity with JSON fields for complex data (geometry, record_options, picks, etc.)
- **SGY Files**: Separate model for uploaded SGY files with relationship to projects
- **Record Options**: JSON array storing `{id, enabled, weight, fileName}` for each file

## Data Models and Relationships

### Database Models
- **UserDBModel** (`users` table)
  - id: int (primary key)
  - username: str (unique, indexed)
  - hashed_password: str
  - disabled: bool
  - auth_level: int (permission level)
  - email: str | None
  - full_name: str | None
  - expiration: datetime | None

- **ProjectDBModel** (`projects` table)
  - project_id: str (primary key) 
  - name: str
  - area: str | None
  - survey_date: date | None
  - received_date: date | None
  - client_id: int | None (foreign key to clients)
  - contact_id: int | None (foreign key to contacts)
  - status: str | None
  - survey_type: str | None
  - remark: str | None
  - has_sgy: bool | None
  - geometry: str | None (JSON)
  - record_options: str | None (JSON)
  - process_options: str | None (JSON)
  - picks: str | None (JSON)
  - created_at: datetime | None
  - updated_at: datetime | None

- **SGYFileDBModel** (`sgy_files` table)
  - id: str (primary key)
  - project_id: str (foreign key to projects)
  - filename: str
  - file_path: str
  - uploaded_at: datetime | None

- **FileDBModel** (`files` table)
  - id: str (primary key)
  - project_id: str (foreign key to projects)
  - filename: str
  - file_path: str
  - uploaded_at: datetime | None

- **ClientDBModel** (`clients` table)
  - id: int (primary key)
  - name: str

- **ContactDBModel** (`contacts` table)
  - id: int (primary key)
  - name: str
  - email: str | None
  - phone: str | None

### 3. API Design
- **File Uploads**: Use multipart/form-data with FormData
- **Project Creation**: Can include initial files that are processed during creation
- **Processing Endpoint**: `/process/grids` requires project_id to locate files

## Common Patterns

### Frontend Patterns
- API calls use axios with interceptors for auth tokens
- File uploads use FormData with multipart encoding
- Redux thunks handle async operations and loading states
- Components use hooks (useAppDispatch, useAppSelector)

### Backend Patterns
- SQLAlchemy models use Mapped[] type hints
- Pydantic schemas handle validation and serialization
- CRUD functions return SQLAlchemy models
- Routers convert models to Pydantic schemas before returning

### Data Serialization Flow
```
SQLAlchemy Model → Pydantic Schema → JSON Response
                 ↑
    model_validate(obj, from_attributes=True)
```

## Environment Variables

### Frontend (Vite)
```typescript
// Access with: import.meta.env.VITE_*
VITE_BACKEND_URL  // Backend API URL
```

### Backend
```python
# Loaded from backend/settings/.env
MQ_SAVE_DIR              # Root directory for file storage
INITIAL_USERS            # Initial user configuration
YOUR_GOOGLE_EMAIL        # Email configuration
YOUR_GOOGLE_EMAIL_APP_PASSWORD
```

## Database Configuration

- **Type**: SQLite (development) - `sqlite:///db/sql_app.db`
- **ORM**: SQLAlchemy with declarative base
- **Session Management**: SessionLocal with autocommit=False, autoflush=False
- **TODO**: Database URL should be moved to .env file for production

## Authentication & Authorization

### JWT Token Structure
- **Access Token Expiry**: Configurable via ACCESS_TOKEN_EXPIRE_MINUTES
- **Refresh Token Expiry**: Configurable via REFRESH_TOKEN_EXPIRE_MINUTES
- **Token Payload**:
  ```json
  {
    "sub": "username:{username}",
    "id": user_id,
    "username": username,
    "disabled": boolean,
    "auth_level": int,
    "email": email,
    "psig": password_signature_hash,
    "jti": unique_token_id
  }
  ```

### Auth Levels
- Permission levels checked with `check_permissions(user, level)`
- Higher auth_level = more permissions
- Auth endpoints:
  - `POST /token` - Login
  - `POST /refresh-token` - Refresh access token
  - `GET /users/me` - Get current user
  - `PUT /change-password` - Change password

## Redux State Management

### Store Slices
- **geometrySlice**: Manages survey geometry data
- **initializationSlice**: Handles app initialization state
- **cacheSlice**: Manages cached data
- **freqSlice**: Frequency-related state
- **plotSlice**: Plot configuration and display state
- **recordSlice**: SGY record management
- **slowSlice**: Slowness/velocity data
- **toastSlice**: UI notifications

### State Structure Pattern
```typescript
interface SliceState {
  data: T | null;
  loading: boolean;
  error: string | null;
}
```

## Dependencies

### Backend (Python)
```
tereancore>=2025.4.24  # Custom package from private PyPI
fastapi[standard]
SQLAlchemy
pydantic
segyio              # SEG-Y file processing
scipy
matplotlib
pandas
bcrypt              # Password hashing
python-jose         # JWT handling
python-multipart    # File uploads
aiofiles           # Async file operations
```

### Frontend (npm)
```json
// Core
"react": "^19.0.0"
"typescript": "~5.7.2"
"vite": "^6.1.0"
"@reduxjs/toolkit": "^2.7.0"

// UI Components
"primereact": "^10.9.1"    // UI component library
"bootstrap": "^5.3.3"       // CSS framework
"pixi.js": "^8.6.6"        // 2D graphics rendering

// Utilities
"axios": "^1.7.9"          // HTTP client
"jwt-decode": "^4.0.0"     // JWT decoding
"npyjs": "^0.6.0"          // NumPy file reading
"xlsx": "^0.18.5"          // Excel file handling
```

## API Endpoints

### Key Endpoints
- `POST /project/create` - Create project with optional file uploads
- `POST /sgy-files/project/{project_id}/upload` - Upload files to existing project
- `POST /process/grids` - Process uploaded SGY files
- `GET /project/{project_id}` - Get project details
- `GET /project/{project_id}/options` - Get project options (geometry, records, limits)
- `POST /project/{project_id}/options` - Save project options

### Additional Processing Endpoints
- `POST /process/slownesses` - Process slowness data with form parameters
- `POST /process/frequencies` - Process frequency data with form parameters
  - Both endpoints accept: project_id, geometry_id, file_ids, test_mode flag
  - Additional params for slownesses: v_min, v_max, v_step, aspect_ratio
  - Additional params for frequencies: f_min, f_max, f_step

### Response Formats
- Most endpoints return data directly: `{ field1: value1, ... }`
- Process grids returns: `{ grids: [...], freq: {...}, slow: {...} }`
- File uploads return: `{ status: "success", file_infos: [...] }`

## Docker Deployment

### Docker Compose Services
- **backend**: FastAPI application
  - Port: 5050
  - Volume: `./db:/app/db:rw` (SQLite database)
  - Dockerfile options: 
    - `docker/backend/fastapi-nocuda/Dockerfile` (default)
    - `docker/backend/fastapi-cuda/Dockerfile` (GPU support)
- **frontend**: React application  
  - Port: 3000
  - Environment: VITE_BACKEND_URL configurable
  - Dockerfile: `docker/frontend/Dockerfile`

### Deployment Scripts
- `dev.sh`: Runs development environment
- `prod.sh`: Runs production environment
- `compose.dev.yml`: Development-specific overrides
- `compose.cuda_test.yml`: GPU testing configuration

## Testing Patterns

### Backend Testing
- Test files: `*_test.py` (e.g., `project_fix_test.py`, `token_manager_test.py`)
- Framework: pytest
- Key test patterns:
  - Mock SQLAlchemy models for Pydantic conversion tests
  - Test database CRUD operations
  - API endpoint integration tests

### Frontend Testing
- Framework: React Testing Library + Jest
- Test files: `*.test.{js,tsx}`
- Key patterns:
  - Component rendering tests
  - Redux store integration tests
  - API service mocking

## Utility Functions and Helpers

### Backend Utilities (`backend/utils/`)
- **authentication.py**: JWT token handling, user verification
- **project_utils.py**: Project-specific helper functions
- **consumer_utils.py**: Message queue consumer utilities
- **email_utils.py**: Email sending with attachments
- **token_manager.py**: Token refresh and management
- **create_dummy_project.py**: Test data generation

### Frontend Utilities (`frontend/src/utils/`)
- Form validation helpers
- Plot utilities for data visualization
- Dispersion calculation utilities

## Known Issues/Gotchas

### 1. Pydantic/SQLAlchemy Conversion
- Must use `model_validate(obj, from_attributes=True)` for proper conversion
- Pydantic models need `Config: from_attributes = True` to accept SQLAlchemy objects
- SQLAlchemy internal attributes (like `_sa_instance_state`) must be excluded

### 2. File Path Handling
- Windows paths may use backslashes, causing mixed separators
- Files are searched in project-specific directory first, then global directory
- The process/grids endpoint needs project_id to find files correctly

### 3. Frontend Environment Variables
- **DO NOT** use `process.env.REACT_APP_*` (that's for Create React App)
- **DO** use `import.meta.env.VITE_*` for Vite projects

### 4. Response Format Inconsistencies
- Some endpoints wrap data in a `data` field, others don't
- Always check the actual response structure when debugging

## Development Workflow

### Running the Project
```bash
# Backend
cd backend
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

### Common Debugging Steps
1. Check browser console for frontend errors
2. Check backend logs for detailed error messages and stack traces
3. Verify file paths and IDs match between frontend and backend
4. Ensure proper environment variables are set
5. Check network tab for actual API request/response data

## Testing
- Backend tests use pytest
- Test files like `project_fix_test.py` can verify specific functionality
- Mock SQLAlchemy models for testing Pydantic conversions

## Security Considerations
- Authentication required for most endpoints (OAuth2/JWT)
- Permission levels checked with `check_permissions(user, level)`
- File uploads restricted to authenticated users
- Project IDs are generated using secure random functions

## Common File Patterns and Naming Conventions

### Backend
- Models: `{entity}_model.py` → `{Entity}DBModel` class
- Schemas: `{entity}_schema.py` → Pydantic models for validation
- CRUD: `{entity}_crud.py` → Database operations
- Routers: `{entity}_router.py` → API endpoints

### Frontend
- Components: PascalCase (`Table.tsx`, `AddGeometry.tsx`)
- Services: camelCase (`api.ts`)
- Redux: `{feature}Slice.ts`, `{feature}Thunks.ts`
- Types: `{feature}.d.ts`

## Debugging Tips

### Common Debug Scenarios
1. **File Upload Issues**
   - Check `MQ_SAVE_DIR` environment variable
   - Verify file paths use correct separators (Windows vs Unix)
   - Check project_id in file storage path
   - Verify multipart form data encoding

2. **Authentication Failures**
   - Check token expiration
   - Verify password signature (psig) matches after password changes
   - Ensure auth_level is sufficient for endpoint

3. **Data Conversion Errors**
   - Ensure `model_validate(obj, from_attributes=True)` for SQLAlchemy → Pydantic
   - Check JSON field parsing (geometry, record_options, etc.)
   - Verify datetime serialization format

4. **Frontend State Issues**
   - Check Redux DevTools for state shape
   - Verify thunk dispatch and error handling
   - Check for stale closures in React components

## Recommended Additional Tools

### Development Tools
1. **API Documentation**
   - FastAPI automatic docs at `/docs` (Swagger UI)
   - ReDoc at `/redoc`

2. **Database Management**
   - SQLite browser for direct database inspection
   - Alembic for database migrations (not currently implemented)

3. **Monitoring & Logging**
   - Structured logging with correlation IDs
   - Request/response middleware for debugging
   - Performance monitoring for slow endpoints

### Missing Features to Consider
1. **Backend**
   - Database migrations system (Alembic)
   - Background task queue (Celery/RQ)
   - API rate limiting
   - Comprehensive error handling middleware
   - Health check endpoints
   - Automated backup system

2. **Frontend**
   - Error boundary components
   - Progressive Web App (PWA) support
   - Internationalization (i18n)
   - Comprehensive loading states
   - Offline capability
   - Analytics integration

3. **DevOps**
   - CI/CD pipeline configuration
   - Environment-specific configurations
   - Automated testing in Docker
   - Production logging aggregation
   - Monitoring and alerting setup

## File Processing Notes

### SEG-Y File Handling
- Uses `segyio` library for reading SEG-Y files
- Files processed through `tereancore` package
- Processing modes: grids, frequencies, slownesses
- Test mode available for debugging without full processing

### Data Flow for Processing
1. Upload files → Generate unique IDs
2. Store in `{MQ_SAVE_DIR}/SGYFiles/{project_id}/`
3. Update project's record_options JSON
4. Process through appropriate endpoint
5. Return processed data (grids, frequencies, slownesses)

## Performance Considerations
- Large file uploads may timeout - consider chunking
- JSON fields in database can impact query performance
- Redux state normalization for large datasets
- Consider pagination for list endpoints
- Implement caching for frequently accessed data 