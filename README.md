# Terean Fullstack

This repo contains the code necessary to run the Terean web utilities. This project has a dependency on the tereancore
repository, which holds shared functions for processing seismic records.

# Setup & Install

## Docker

Docker images to build the components can be found under /docker

## tereancore dependency

The backend requires tereancore - a repository of utilities for working with seismic files. You must have access to this
repository in order to install the package.

The dependency tereancore can be installed several different ways:

- Installed from terean pypi located here: `https://dbarnes-terean.github.io/terean-pypi/`
    - Add the terean pypyi to your pip.conf
    - Install with pip using the extra url option:
      `pip install tereancore --extra-index-url https://dbarnes-terean.github.io/terean-pypi/`
    - Add the line `--extra-index-url https://dbarnes-terean.github.io/terean-pypi/` to `requirements.txt`, prior to
      install
- Directly installed from the github repo located here: `https://github.com/dbarnes-terean/terean-core`
    - `pip install git+ssh://git@github.com/dbarnes-terean/terean-core.git`
- Install from a cloned, local version of the repository
    - First, clone the repo `git clone git@github.com:dbarnes-terean/terean-core.git`
    - Install `pip install {clone-directory}`

## PyCuda

Some backend functions currently require cuda acceleration using pycuda. This requires a few additional setup steps

- Ensure you have cuda capable hardware installed
- Install appropriate cuda toolkit
- Ensure you have a C++ compiler installed.
- `pip install pycuda`

If running in docker, ensure that gpu's are passed through to the container. (ex: `--gpus all`)

The `pycuda_test_*` functions in the tereancore repository can be used to test if pycuda was installed correctly.

## Backend - FastAPI

Setup can be done using a venv as follows:
- Create a virtual environment
  - `python3.13 -m venv backend/.venv`
- Activate the virtual environment
- Install dependencies
  - `pip install -r backend/requirements.txt`
  - If you encounter issues with the `tereancore` dependency here, look under the tereancore subsection.
- Optional: If using pycuda, install pycuda
- Run the backend
  - `python3.13 -m uvicorn backend.main:app --host 0.0.0.0 --port 80 --workers 4`

Environment variables must be specified under backend/settings/.env prior to running

## Backend - ReMi1dConsumer

Setup can be done using a venv as follows:
- Create a virtual environment
    - `python3.13 -m venv backend/.venv`
- Activate the virtual environment
- Install dependencies
    - `pip install -r backend/requirements.txt`
    - If you encounter issues with the `tereancore` dependency here, look under the tereancore subsection.
- Run the Consumer
    - `python3.13 backend/ReMi1dConsumer.py`

Environment variables must be specified under backend/settings/.env prior to running

## Frontend

Setup can be done as follows
- Navigate to `frontend/.`
- Run `npm install`
- Run dev using `npm run dev`



