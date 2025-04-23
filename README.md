# Terean Fullstack Toolkit

This repo contains code to build and Terean tools for working with Refraction Microtremor (ReMi) datasets. 
This is still a work in progress, and there are several tools which can be found within the repo.

## Python environment:
- Python 3.13.2
- Requirements.txt available at `/backend/requirements.txt`. This contains more packages than necessary however, and will
need to be pruned at some point as some are no longer being used.

## Tools
- 2dS and 2dP Form website (Frontend and backend)
  - This is currently hosted at http://www.app.terean.com, and provides the ability for users to generate 2dS and 2dP plots
using matplotlib. Data is entered in a form, and the plot is then generated. Currently, CUDA is used to accelerate plot
generation though the use of the PyCuda library.
  - The frontend (under `/frontend`) is built using Vite + React + Bootstrap. This was my first frontend work - it was initially started using create-react-app, with raw javascript
and then was converted to use Vite with typescript. As such, most files are not fully typescript compatible - just the 
extension was updated.
  - Run the frontend by first running `npm install`, then `npm dev start`
  - The backend uses FastAPI, running from `/backend/main.py`. The `/backend` directory also contains additional tools, mentioned later. 
- 1dS Backend
  - The backend for the 1dS Pick and Disper pages found in [this repo](https://github.com/dbarnes-terean/pixi-js-stuff/).
It shares a lot of common code in utils, hence living here. Hastily made and hosted, its endpoints should be merged with
the main backend, and properly secured.
  - Runs from `/backend/OneDEndpoint.py`.
- VsSurfQa
  - Python script that is bundled into an executable
  - Built using the command `pyinstaller .\backend\VsSurfQa.py -F -n VsSurfQa-1.0.30.exe --exclude-module pycuda --exclude-module obspy`
  - Currently bundled with Vibrascope, and automatically runs analysis as data is collected, writing the results to file
  - Also shares a lot of common code in utils, hence it being developed here.
- ReMi1dConsumer-v2 & FastApiFileDownload
  - A very temporary solution that is somehow still here.
  - ReMi1dConsumer-v2 is a RabbitMQ Consumer, which receives some data, does some basic processing, then saves it and triggers
two emails to be sent.
  - FastApiFileDownload is a *very* minimal site which allows us to download data, process it, and then trigger a form
email to be sent with results.
  - There's A LOT wrong here.
    - Credentials are entered by just replacing the ####'s and running. Very bad
    - There's no auth on these endpoints, security through obscurity.
    - The file download & results forms should be part of the primary backend

## Things to Address (in no particular order)

- Security
  - HTTPS support
  - How to do user authentication?
    - Is the current OAuth scheme acceptable?
    - Implement refresh tokens (log out after XX minutes of inactivity)
    - Properly store and use secrets (App specific password for the form emails, credentials for RabbitMQ)
  - How to properly prevent unauthenticated users from accessing protected pages
    - `/protected` being an example of how it's currently done - is there a better way?
- How to structure code so that shared utils (`/backend/utils/*`) are available to multiple products, without all of them
living inside `/backend`
- Containerization
  - I'd love to be able to run everything using docker compose
- Backend design
  - How to properly store and provide user data
  - Records: Store path to file in DB?
  - API Design? What order should these tasks be handled in?