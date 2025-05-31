import ast
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s::%(lineno)d - %(levelname)s - %(message)s',
    level=logging.INFO,
)

import os
from contextlib import asynccontextmanager
from datetime import datetime
# import pycuda.autoinit
from typing import Annotated

import aiofiles
import json_fix
from fastapi import FastAPI, Depends, UploadFile, File, Form, Response
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from tereancore.VelocityModel import VelocityModel

from config import settings
from crud.user_crud import get_user_by_username, create_user
from database import engine, Base, get_db, SessionLocal
from router.admin import admin_router
from router.authentication import authentication_router
from router.process_router import process_router
from router.project_router import project_router
from router.sgy_file_router import sgy_file_router
from schemas.user_schema import UserCreate, User
from utils.authentication import check_permissions, get_current_user
from utils.consumer_utils import get_user_info
from utils.email_utils import generate_vs_surf_results, send_email_gmail
from utils.utils import validate_id

# Allows json to serialize objects using __json__
json_fix.fix_it()

# Initialize routers
logger = logging.getLogger(__name__)
app = FastAPI()

# Initialize / Update DB - Skip during testing
# Check if we're running tests by looking for pytest in sys.modules
import sys

if "pytest" not in sys.modules:
    Base.metadata.create_all(bind=engine)


def init_users_from_env():
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("before")

    # Initialize / Update DB tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    raw_users = settings.INITIAL_USERS
    if raw_users:
        initial_users = ast.literal_eval(raw_users)
        for initial_user in initial_users:
            # Ensure user has username and password
            if not "username" in initial_user or not "password" in initial_user:
                logger.warning(f"user missing username or password: {initial_user}")
                continue

            # Check db
            query_res = get_user_by_username(db=db, username=initial_user['username'])
            if query_res is None:
                # Register a user with that info
                new_user = UserCreate(
                    username=initial_user.get('username'),
                    password=initial_user.get('password'),
                    disabled=initial_user.get('disabled', False),
                    auth_level=initial_user.get('auth_level', 1),
                    email=initial_user.get('email', None),
                    full_name=initial_user.get('full_name', None),
                    expiration=initial_user.get('expiration', None)
                )
                res = create_user(db=db, user=new_user)
                logger.info(f"created user {new_user.username}: {res}")
            else:
                logger.info(f"user {initial_user['username']} already exists")
    db.close()
    yield
    logger.info("after")


app.include_router(authentication_router)
app.include_router(admin_router)
app.include_router(sgy_file_router)
app.include_router(project_router)
app.include_router(process_router)

origins = [
    "http://localhost:3000",
    "http://localhost:35197",
    "http://47.48.84.166:35197",
    "http://47.48.84.166:35198",
    # Adjust the port if your frontend runs on a different one
    # "https://yourfrontenddomain.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # origins, # Allows all origins from the list
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

db_dependency = Depends(get_db)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logger.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/generateResultsEmail")
async def generate_results_email(
        velocity_model: Annotated[UploadFile, File(...)],
        client_name: Annotated[str, Form(...)],
        client_email: Annotated[str, Form(...)],
        file_id: Annotated[str, Form(...)],
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user, 1)

    # Validate file_id to prevent path traversal
    if not validate_id(file_id):
        raise HTTPException(status_code=400, detail="Invalid file ID")

    data_dir = settings.MQ_SAVE_DIR
    sent_results_dir = os.path.join(data_dir, "SentResults")
    final_results_dir = os.path.join(sent_results_dir, file_id, datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    # Make folder in results dir
    os.makedirs(final_results_dir, exist_ok=True)

    # Write upload file to disk
    model_file_path = os.path.join(final_results_dir, "model.txt")
    async with aiofiles.open(model_file_path, 'wb') as out_file:
        while content := await velocity_model.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    # Ingest velocity model
    ingested_model_meters = VelocityModel.from_file(model_file_path, to_meters_factor=1.0)
    ingested_model_feet = VelocityModel.from_file(model_file_path, to_meters_factor=3.28084)
    ingested_model_meters.plot_vel_model(savefig=os.path.join(final_results_dir, "VsSurf1dS_Model_Meters.png"),
                                         show_fig=False, units="m")
    ingested_model_feet.plot_vel_model(savefig=os.path.join(final_results_dir, "VsSurf1dS_Model_Feet.png"),
                                       show_fig=False, units="ft")
    ingested_model_meters.generate_pretty_model_file(os.path.join(final_results_dir, "VsSurf1dS_Model_Meters.txt"))
    ingested_model_feet.generate_pretty_model_file(os.path.join(final_results_dir, "VsSurf1dS_Model_Feet.txt"))

    plain_text, html_text = generate_vs_surf_results(client_name)
    send_email_gmail(
        from_address=settings.GOOGLE_EMAIL,
        application_password=settings.GOOGLE_EMAIL_APP_PASSWORD,
        subject="Your VsSurf 1dS® Results Are Ready!",
        body_plain=plain_text,
        body_html=html_text,
        recipients=[client_email, ],
        bcc_recipients=["dbarnes@terean.com", "astarr@terean.com"],
        attachments=[
            os.path.join(final_results_dir, "VsSurf1dS_Model_Meters.png"),
            os.path.join(final_results_dir, "VsSurf1dS_Model_Feet.png"),
            os.path.join(final_results_dir, "VsSurf1dS_Model_Meters.txt"),
            os.path.join(final_results_dir, "VsSurf1dS_Model_Feet.txt"),
        ],
    )

    return "Email generated successfully."


@app.get("/projects/{file_id}/results_email_form", response_class=Response)
async def results_email_form(
        file_id: str,
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user, 1)

    # Validate file_id to prevent path traversal
    if not validate_id(file_id):
        raise HTTPException(status_code=400, detail="Invalid file ID")

    data_dir = settings.MQ_SAVE_DIR

    # Get user info
    extracted_dir = os.path.join(data_dir, "Extracted", file_id)
    user_name, user_phone, user_email = get_user_info(extracted_dir)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Results Email Form</title>
    </head>
    <body>
        <h1>Upload Model File and Verify Data</h1>
        <form action="/generateResultsEmail" method="post" enctype="multipart/form-data">
            <label for="velocity_model">Upload Model File:</label>
            <input type="file" id="velocity_model" name="velocity_model" accept=".txt" required><br><br>

            <label for="client_name">Verify Client Name:</label>
            <input type="text" id="client_name" name="client_name" value="{user_name}"><br><br>

            <label for="client_email">Verify Client Email:</label>
            <input type="text" id="client_email" name="client_email" value="{user_email}"><br><br>

            <label for="file_id">File ID (Probably don't change this):</label>
            <input type="text" id="file_id" name="file_id" value="{file_id}"><br><br>

            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    return Response(content=html_content, media_type="text/html")

# endregion
