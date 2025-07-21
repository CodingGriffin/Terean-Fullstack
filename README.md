# Terean Fullstack

A comprehensive web-based platform for seismic data analysis and visualization, specializing in surface wave processing and dispersion analysis for geotechnical engineering applications.

## Overview

Terean Fullstack provides a complete solution for processing seismic records, generating velocity models, and performing dispersion analysis. The platform supports both 1D and 2D seismic modeling with CUDA acceleration for high-performance computing.

### Key Features

- **Seismic Data Processing**: Load and process SEG-Y files with advanced filtering and preprocessing
- **Velocity Modeling**: Generate 1D and 2D shear wave velocity models
- **Dispersion Analysis**: Interactive dispersion curve analysis and modeling
- **CUDA Acceleration**: GPU-accelerated processing for large datasets
- **Project Management**: Organize seismic surveys with client management
- **Multi-format Support**: Handle various seismic file formats and export options
- **Real-time Visualization**: Interactive plots and analysis tools

## Architecture

- **Backend**: FastAPI with SQLAlchemy ORM, CUDA-accelerated processing
- **Frontend**: React with TypeScript, responsive Bootstrap UI
- **Database**: SQLite with support for PostgreSQL
- **Message Queue**: RabbitMQ for background processing
- **Containerization**: Docker with GPU support

## Prerequisites

### System Requirements
- Python 3.8+ (recommended: 3.13)
- Node.js 18+ and npm
- CUDA-capable GPU (optional, for acceleration)
- Git access to `tereancore` repository

### Hardware Recommendations
- 16GB+ RAM for large seismic datasets
- NVIDIA GPU with CUDA support for optimal performance
- SSD storage for faster I/O operations

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd terean-fullstack
```

### 2. Install tereancore Dependency

The backend requires the `tereancore` package. Choose one installation method:

**Option A: From Terean PyPI (Recommended)**
```bash
pip install tereancore --extra-index-url https://dbarnes-terean.github.io/terean-pypi/
```

**Option B: Direct from GitHub**
```bash
pip install git+ssh://git@github.com/dbarnes-terean/terean-core.git
```

**Option C: Local Development**
```bash
git clone git@github.com:dbarnes-terean/terean-core.git
pip install ./terean-core
```

### 3. Backend Setup

```bash
# Create virtual environment
python3.13 -m venv backend/.venv

# Activate environment
# Linux/Mac:
source backend/.venv/bin/activate
# Windows:
backend\.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp backend/env.example backend/.env
# Edit backend/.env with your configuration
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

### 5. Optional: CUDA Setup

For GPU acceleration:
```bash
# Ensure CUDA toolkit is installed
# Install PyCuda
pip install pycuda

# Test CUDA installation
python -c "from tereancore import pycuda_test_basic; pycuda_test_basic()"
```

## Configuration

### Environment Variables

Copy `backend/env.example` to `backend/.env` and configure:

```bash
# Database
DATABASE_URL=sqlite:///db/sql_app.db

# Authentication
SECRET_KEY=your-secure-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=240

# File Storage
MQ_SAVE_DIR=/path/to/data/directory

# RabbitMQ (optional)
MQ_HOST_NAME=localhost
MQ_PORT=5672
MQ_USER_NAME=guest
MQ_PASSWORD=guest

# Email notifications (optional)
YOUR_GOOGLE_EMAIL=your-email@gmail.com
YOUR_GOOGLE_EMAIL_APP_PASSWORD=your-app-password
```

## Running the Application

### Development Mode

**Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Background Consumer (optional):**
```bash
cd backend
python ReMi1dConsumer.py
```

### Production with Docker

```bash
# Build and run with GPU support
docker-compose up --build

# Without GPU support
docker-compose -f compose.yml -f compose.nocuda.yml up --build
```

### Access Points

- **Frontend**: http://localhost:3000 (dev) or http://localhost:35201 (docker)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage

### Basic Workflow

1. **Create Project**: Set up a new seismic survey project
2. **Upload Data**: Import SEG-Y files and configure geometry
3. **Process Records**: Apply preprocessing and filtering
4. **Generate Models**: Create 1D/2D velocity models
5. **Dispersion Analysis**: Analyze dispersion curves and pick modes
6. **Export Results**: Generate reports and export data

### API Integration

The REST API provides programmatic access to all functionality:

```python
import requests

# Authentication
response = requests.post("http://localhost:8000/auth/login", 
                        data={"username": "user", "password": "pass"})
token = response.json()["access_token"]

# Create project
headers = {"Authorization": f"Bearer {token}"}
project_data = {"name": "My Survey", "client_id": 1}
response = requests.post("http://localhost:8000/projects/", 
                        json=project_data, headers=headers)
```

## Development

### Project Structure

```
terean-fullstack/
├── backend/                 # FastAPI backend
│   ├── src/                # Source code
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── crud/           # Database operations
│   │   ├── router/         # API endpoints
│   │   └── utils/          # Utility functions
│   ├── tests/              # Test suite
│   ├── Notebooks/          # Jupyter examples
│   └── cuda/               # CUDA kernels
├── frontend/               # React frontend
│   ├── src/
│   │   ├── Components/     # React components
│   │   ├── Pages/          # Page components
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utility functions
├── docker/                 # Docker configurations
└── nginx/                  # Nginx configuration
```

### Testing

**Backend:**
```bash
cd backend
pytest
pytest --cov=src --cov-report=html  # With coverage
```

**Frontend:**
```bash
cd frontend
npm test
npm run lint
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Run test suite: `pytest` and `npm test`
5. Commit changes: `git commit -am 'Add new feature'`
6. Push to branch: `git push origin feature/new-feature`
7. Submit a Pull Request

## Troubleshooting

### Common Issues

**CUDA Installation:**
- Ensure NVIDIA drivers are installed
- Verify CUDA toolkit version compatibility
- Test with `nvidia-smi` command

**tereancore Dependency:**
- Verify access to private repository
- Check SSH key configuration
- Try alternative installation methods

**Database Issues:**
- Ensure database directory exists and is writable
- Check DATABASE_URL configuration
- Run database migrations if needed

**Performance:**
- Monitor memory usage with large datasets
- Enable GPU acceleration for better performance
- Adjust worker processes based on system resources

### Support

For technical support and questions:
- Check the API documentation at `/docs`
- Review example notebooks in `backend/Notebooks/`
- Consult the test suite for usage examples

## License

[License information to be added]

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - Frontend library
- [tereancore](https://github.com/dbarnes-terean/terean-core) - Seismic processing core
- [CUDA](https://developer.nvidia.com/cuda-zone) - GPU acceleration
