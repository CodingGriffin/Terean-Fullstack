Setup:
- Prior to setup, ensure that you have a CUDA capable GPU with drivers correctly installed.
- Create virtual environment, working directory `terean-full-stack`: `python -m venv ".venv"`
- Activate the virtual environment: `source .venv/Scripts activate` (Linux) or `.\.venv\Scripts\activate.ps1` (Windows)
- Install requirements: `pip install -r backend/requirements_specific.txt`
- Configure environment variables:
  - Copy `backend/env.example` to `backend/.env` (or `backend/settings/.env`)
  - Edit the `.env` file with your specific configuration values
  - The centralized configuration in `src/config.py` will automatically load these values
- Launch backend: `python -m uvicorn backend.main:app --reload --port 35198`
- Verify backend is functioning by going to `http://127.0.0.1:35198/` and `http://127.0.0.1:35198/docs`

Environment Configuration:
- All environment variables are centrally managed through `src/config.py`
- The configuration module automatically loads the `.env` file from either:
  - `backend/settings/.env` (preferred location)
  - `backend/.env` (fallback location)
- This approach ensures consistent environment variable loading regardless of where the application is run from
- See `backend/env.example` for all available configuration options

Docker/Production Deployment:
- Set `LOAD_FROM_ENV=true` to skip loading from `.env` files
- When this is set, the application will use existing environment variables only
- This is useful for Docker containers and production deployments where environment variables are injected directly
- Example: `docker run -e LOAD_FROM_ENV=true -e DATABASE_URL=postgresql://... myapp`

Running Notebooks:
- Ensure that juypter notebook is installed (`pip install notebook`)
- From `backend` directory, run the commmand `jupyter notebook`
- Note the first cell, which is run to ensure that imports work correctly. If creating a new notebook, be sure to add one.
```python
from set_notebook_path import check_path
check_path()
```

Structure:
- `models`, `schemas`, and their associated `crud` functions are located in the directories with the same names.
- The `router` directory contains endpoints.
- main.py contains the fastapi app, and additional endpoints that should be moved to `router`.
- `utils` contains various utility functions.
- `cuda` contains cuda kernels and test scripts.

Overview:

This backend currently supports basic authentication and generation of 2D Geometry visualizations requested by the frontend. 
These visualizations are currently only generated using the `plot_2d` function in `utils/plotting_utils.py`. This function
generates a two dimensional visualization of shear wave (or s wave) velocities along an array, interpolating between a number
of one dimensional models at specific locations.