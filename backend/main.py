import ast
import io
import logging
import os
import tempfile
import time
import zipfile
from datetime import datetime

import aiofiles
# import pycuda.autoinit
from typing import Annotated, List, Union

import numpy as np
from dotenv import load_dotenv
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, UploadFile, File, Form, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import HTTPBearer
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, StreamingResponse
from tereancore.VelocityModel import VelocityModel
from tereancore.plotting_utils import validate_contours, validate_unit_str, build_tick_dicts
from tereancore.twodp_utils import plot_2dp_from_geoct

from tereancore.twods_utils import plot_2ds
from tereancore.sgy_utils import validate_record_is_record, load_segy_segyio, preprocess_streams
from tereancore.utils import lambda0, get_geom_func_from_excel, model_search_pattern
from tereancore.vspect import vspect_stream

from backend.database import engine, Base
from backend.router.authentication import authentication_router
from backend.router.admin import admin_router
from backend.utils.authentication import oauth2_scheme
from backend.utils.consumer_utils import get_user_info
from backend.utils.email_utils import generate_vs_surf_results, send_email_gmail
from backend.utils.utils import CHUNK_SIZE, get_fastapi_file_locally

load_dotenv("/settings/.env", override=True)
logging.basicConfig(
    format='%(asctime)s - %(name)s::%(lineno)d - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Initialize / Update DB
Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBearer()
app.include_router(authentication_router)
app.include_router(admin_router)

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logger.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/checkRecord")
async def checkRecord(
        background_tasks: BackgroundTasks,
        file_data: UploadFile = File(...),
):
    file_name = file_data.filename
    split = file_name.split('.')
    if len(split) <= 1:
        raise HTTPException(400, "No file extension found.")
    extension = "." + file_name.split('.')[-1]
    print(extension)
    try:
        fd, path = tempfile.mkstemp(suffix=extension)
        print(path)
        async with aiofiles.open(path, 'wb') as f:
            while chunk := await file_data.read(CHUNK_SIZE):
                await f.write(chunk)
        validate_record_is_record(path)
        # background_tasks.add_task(fd.close)
    except Exception as e:
        return False
    return True


@app.post("/checkRecord2")
async def checkRecord2(
        background_tasks: BackgroundTasks,
        file_data: UploadFile = File(...),
):
    ret = await get_fastapi_file_locally(background_tasks, file_data)
    if ret is Exception:
        return False
    fp, path, extension = ret
    try:
        validate_record_is_record(path)
    except Exception as e:
        return False
    return True


@app.post("/uploadTest")
async def upload_test(
        int_value: str = Form(...),
        float_value: str = Form(...),
        string_value: str = Form(...),
        file_data: UploadFile = File(...),
):
    print(int_value)
    print(float_value)
    print(string_value)
    print(file_data.filename)
    time.sleep(5)
    return FileResponse("backend/Terean-logo.png")


@app.post("/uploadTestTwo")
async def upload_test_two(
        # int_value: str = Form(...),
        # float_value: str = Form(...),
        # string_value: str = Form(...),
        files: List[UploadFile] = File(...),
):
    # print(int_value)
    # print(float_value)
    # print(string_value)
    print(len(files))
    # print(file_data.filename)
    time.sleep(5)
    return FileResponse("backend/Terean-logo.png")


@app.post("/uploadTestThree")
async def upload_test_three(
        int_value: str = Form(...),
        # float_value: str = Form(...),
        # string_value: str = Form(...),
        files: list[UploadFile] = File(...),
):
    print(int_value)
    print(len(files))
    # print(file_data.filename)
    time.sleep(5)
    return FileResponse("backend/Terean-logo.png")


@app.post("/process2dP")
async def process2dP(
        geoct_model_file: Annotated[UploadFile, File(...)],
        background_tasks: BackgroundTasks,
        travel_time_file: Annotated[UploadFile, File(...)] = None,
        title: Annotated[str, Form(...)] = None,
        x_min: Annotated[float, Form(...)] = None,
        x_max: Annotated[float, Form(...)] = None,
        min_depth: Annotated[float, Form(...)] = None,
        max_depth: Annotated[float, Form(...)] = None,
        vel_min: Annotated[float, Form(...)] = None,
        vel_max: Annotated[float, Form(...)] = None,
        smoothing: Annotated[int, Form(...)] = 20,
        contours: Annotated[str, Form(...)] = None,  # JSON THIS
        unit_override: Annotated[str, Form(...)] = None,
        y_label: Annotated[str, Form(...)] = None,
        x_label: Annotated[str, Form(...)] = None,
        label_pad_size: Annotated[float, Form(...)] = -58,
        cbar_label: Annotated[str, Form(...)] = None,
        cbar_pad_size: Annotated[float, Form(...)] = 0.10,
        invert_colorbar_axis: Annotated[bool, Form(...)] = False,
        cbar_ticks: Annotated[list[float], Form(...)] = None,
        contour_color: Annotated[str, Form(...)] = "k",
        contour_width: Annotated[float, Form(...)] = 0.8,
        aboveground_color: Annotated[str, Form(...)] = "w",
        aboveground_border_color: Annotated[str, Form(...)] = None,
        shift_elevation: Annotated[bool, Form(...)] = False,
        display_as_depth: Annotated[bool, Form(...)] = None,
        elevation_tick_increment: Annotated[float, Form(...)] = 50,
        reverse_elevation: Annotated[bool, Form(...)] = False,
        reverse_data: Annotated[bool, Form(...)] = False,
        peak_elevation: Annotated[float, Form(...)] = None,
        tick_right: Annotated[bool, Form(...)] = False,
        tick_left: Annotated[bool, Form(...)] = True,
        tick_top: Annotated[bool, Form(...)] = True,
        tick_bottom: Annotated[bool, Form(...)] = False,
        ticklabel_right: Annotated[bool, Form(...)] = False,
        ticklabel_left: Annotated[bool, Form(...)] = True,
        ticklabel_top: Annotated[bool, Form(...)] = True,
        ticklabel_bottom: Annotated[bool, Form(...)] = False,
        x_axis_label_pos: Annotated[str, Form(...)] = "top",
        y_axis_label_pos: Annotated[str, Form(...)] = "left",
        test_mode: Annotated[bool, Form(...)] = False,
):
    if test_mode is not None and test_mode:
        return FileResponse("backend/Terean-logo.png")

    # Get GeoCT Model and TT files as local files
    model_ret = await get_fastapi_file_locally(background_tasks, geoct_model_file)
    if model_ret is Exception:
        raise HTTPException(500, "Error loading model file.")
    _, model_local, _ = model_ret

    if travel_time_file is not None:
        tt_ret = await get_fastapi_file_locally(background_tasks, travel_time_file)
        if tt_ret is Exception:
            raise HTTPException(500, "Error loading tt file.")
        _, tt_local, _ = tt_ret
    else:
        tt_local = None

    contours = validate_contours(contours)
    unit_override = validate_unit_str(unit_override)
    tick_param, ticklabel_param = build_tick_dicts(
        tick_right=tick_right, tick_left=tick_left, tick_top=tick_top, tick_bottom=tick_bottom,
        ticklabel_right=ticklabel_right, ticklabel_left=ticklabel_left, ticklabel_top=ticklabel_top,
        ticklabel_bottom=ticklabel_bottom
    )

    if x_label is None:
        x_label = "Array Dist., " + unit_override
    if y_label is None:
        if peak_elevation is not None:
            y_label = "Elevation, " + unit_override
        else:
            y_label = "Depth, " + unit_override
    if cbar_label is None:
        cbar_label = "P-Wave Velocity, " + unit_override + "/sec"

    # Create temp file to write to
    fd, path = tempfile.mkstemp(suffix=".png")
    with os.fdopen(fd, 'w') as f:
        _, img_buff = plot_2dp_from_geoct(
            geoct_model_path=model_local,
            travel_time_path=tt_local,
            x_min=x_min,
            x_max=x_max,
            min_depth=min_depth,
            max_depth=max_depth,
            smoothing_sigma=smoothing,
            contours=contours,
            title=title,
            y_label=y_label,
            x_label=x_label,
            cbar_label=cbar_label,
            cbar_vmin=vel_min,
            cbar_vmax=vel_max,
            annotation_color="k",
            interp_res=0.5,
            label_pad_size=label_pad_size,
            cbar_pad_size=cbar_pad_size,
            contour_width=contour_width,
            limit_tt_to_plot=True,
            poly_color="w",
            poly_border_color=None,
            save_path=None,
            show_plot=False,
            reverse_data=reverse_data,
            show_max_survey_depth=False,
            valid_survey_depth_override=None,
            ticks=tick_param,
            ticklabels=ticklabel_param,
            plot_size=(10, 5),
            aspect_ratio=None,
            colorbar=True,
            invert_colorbar_axis=invert_colorbar_axis,
        )
    background_tasks.add_task(img_buff.close)
    headers = {'Content-Disposition': 'inline; filename="out.png"'}
    return Response(img_buff.getvalue(), headers=headers, media_type="image/png")


@app.post("/process2dS")
async def process2dS(
        velocity_models: Annotated[list[UploadFile], File(...)],
        background_tasks: BackgroundTasks,
        title: Annotated[str, Form(...)] = None,
        elevation_data: Annotated[UploadFile, File(...)] = None,
        min_depth: Annotated[float, Form(...)] = None,
        max_depth: Annotated[float, Form(...)] = None,
        vel_min: Annotated[float, Form(...)] = None,
        vel_max: Annotated[float, Form(...)] = None,
        resolution: Annotated[float, Form(...)] = 0.1,
        smoothing: Annotated[int, Form(...)] = 20,
        contours: Annotated[str, Form(...)] = None,  # JSON THIS
        enable_colorbar: Annotated[bool, Form(...)] = True,
        invert_colorbar_axis: Annotated[bool, Form(...)] = False,
        x_min: Annotated[float, Form(...)] = None,
        x_max: Annotated[float, Form(...)] = None,
        unit_override: Annotated[str, Form(...)] = None,
        y_label: Annotated[str, Form(...)] = None,
        x_label: Annotated[str, Form(...)] = None,
        label_pad_size: Annotated[float, Form(...)] = -58,
        cbar_label: Annotated[str, Form(...)] = None,
        cbar_pad_size: Annotated[float, Form(...)] = 0.10,
        cbar_ticks: Annotated[list[float], Form(...)] = None,
        contour_color: Annotated[str, Form(...)] = "k",
        contour_width: Annotated[float, Form(...)] = 0.8,
        elevation_tick_size: Annotated[float, Form(...)] = 50,
        cbar_fraction: Annotated[float, Form(...)] = 0.05,
        cbar_orientation: Annotated[str, Form(...)] = "vertical",
        aspect_ratio: Annotated[str, Form(...)] = None,
        aboveground_color: Annotated[str, Form(...)] = "w",
        aboveground_border_color: Annotated[str, Form(...)] = None,
        shift_elevation: Annotated[bool, Form(...)] = False,
        display_as_depth: Annotated[bool, Form(...)] = None,
        elevation_tick_increment: Annotated[float, Form(...)] = 50,
        reverse_elevation: Annotated[bool, Form(...)] = False,
        reverse_data: Annotated[bool, Form(...)] = False,
        tick_right: Annotated[bool, Form(...)] = False,
        tick_left: Annotated[bool, Form(...)] = True,
        tick_top: Annotated[bool, Form(...)] = True,
        tick_bottom: Annotated[bool, Form(...)] = False,
        ticklabel_right: Annotated[bool, Form(...)] = False,
        ticklabel_left: Annotated[bool, Form(...)] = True,
        ticklabel_top: Annotated[bool, Form(...)] = True,
        ticklabel_bottom: Annotated[bool, Form(...)] = False,
        x_axis_label_pos: Annotated[str, Form(...)] = "top",
        y_axis_label_pos: Annotated[str, Form(...)] = "left",
        test_mode: Annotated[bool, Form(...)] = False,
):
    if test_mode is not None and test_mode:
        print("elevation tick size: ", elevation_tick_size)
        print("colorbar fraction: ", cbar_fraction)
        print("colorbar orientation: ", cbar_orientation)
        print("aspect ratio: ", aspect_ratio)
        return FileResponse("backend/Terean-logo.png")

    contours = validate_contours(contours)
    unit_override = validate_unit_str(unit_override)
    tick_param, ticklabel_param = build_tick_dicts(
        tick_right=tick_right, tick_left=tick_left, tick_top=tick_top, tick_bottom=tick_bottom,
        ticklabel_right=ticklabel_right, ticklabel_left=ticklabel_left, ticklabel_top=ticklabel_top,
        ticklabel_bottom=ticklabel_bottom
    )

    # Process Excel file
    if elevation_data is None:
        geom_interp_func = lambda0
        peak_elevation = None
    else:
        file_name = elevation_data.filename
        split = file_name.split('.')
        if len(split) <= 1:
            raise HTTPException(400, "No file extension found.")
        extension = "." + file_name.split('.')[-1]
        try:
            fd, path = tempfile.mkstemp(suffix=extension)
            async with aiofiles.open(path, 'wb') as f:
                while chunk := await elevation_data.read(CHUNK_SIZE):
                    await f.write(chunk)
            geom_interp_func, peak_elevation = get_geom_func_from_excel(path, reverse_elevation=reverse_elevation)
            if display_as_depth:
                peak_elevation = None
        except Exception as e:
            raise HTTPException(400, "Failed to parse excel file.")

    # Set model elevation using geometry
    ingested_velocity_models = []
    unit_str = None
    prev_units_str = None
    for vel_model in velocity_models:
        matches = model_search_pattern.search(vel_model.filename)
        if matches is not None and len(matches.groups()) == 2:
            position = ast.literal_eval(matches.group(1))
            unit = matches.group(2).lower()
            if unit_override is None:
                if unit == "ft":
                    to_meters_factor = 3.28084
                    unit_str = "ft"
                else:
                    to_meters_factor = 1.0
                    unit_str = "m"
            else:
                if unit_override == "ft":
                    to_meters_factor = 3.28084
                    unit_str = "ft"
                else:
                    to_meters_factor = 1.0
                    unit_str = "m"
            if (unit_str is not None
                    and prev_units_str is not None
                    and prev_units_str != unit):
                print("ERROR: Unit string changed between models!")
            ingested_model = VelocityModel.from_file(
                vel_model.file,
                position=position,
                to_meters_factor=to_meters_factor,
            )
            ingested_velocity_models.append(ingested_model)
        else:
            print("ERROR Reading file ", vel_model.filename)

    if x_label is None:
        x_label = "Array Dist., " + unit_str
    if y_label is None:
        if peak_elevation is not None:
            y_label = "Elevation, " + unit_str
        else:
            y_label = "Depth, " + unit_str
    if cbar_label is None:
        cbar_label = "Shear-Wave Velocity, " + unit_str + "/sec"

    fd, path = tempfile.mkstemp(suffix=".png")
    with os.fdopen(fd, 'w') as f:
        _, img_buff = plot_2ds(
            vel_models=ingested_velocity_models,
            elevation_func=geom_interp_func,
            x_min=x_min,
            x_max=x_max,
            x_min_trim=None,
            x_max_trim=None,
            y_min=min_depth,
            y_max=max_depth,
            res=resolution,
            smoothing_sigma=smoothing,
            contours=contours,
            title=title,
            y_label=y_label,
            x_label=x_label,
            cbar_label=cbar_label,
            cbar_vmin=vel_min,
            cbar_vmax=vel_max,
            contour_color=contour_color,
            contour_width=contour_width,
            label_pad_size=label_pad_size,
            cbar_pad_size=cbar_pad_size,
            colorbar=enable_colorbar,
            invert_colorbar_axis=invert_colorbar_axis,
            save_path=path,
            aboveground_color=aboveground_color,
            aboveground_border_color=aboveground_border_color,
            shift_elevation=shift_elevation,
            peak_elevation=peak_elevation,
            cbar_ticks=cbar_ticks,
            reverse=reverse_data,
            elevation_tick_increment=elevation_tick_increment,
            show_plot=False,
            ticks=tick_param,
            ticklabels=ticklabel_param,
            x_label_position=x_axis_label_pos,
            y_label_position=y_axis_label_pos,
        )
    background_tasks.add_task(img_buff.close)
    headers = {'Content-Disposition': 'inline; filename="out.png"'}
    return Response(img_buff.getvalue(), headers=headers, media_type="image/png")


# region Processor / File Download Endpoints
@app.get("/projects/{file_id}/sgy")
async def download_file(file_id: str):
    data_dir = os.getenv("MQ_SAVE_DIR")
    sgy_dir = os.path.join(data_dir, "Extracted", file_id, "Save")
    sgy_files = [x for x in os.listdir(sgy_dir) if x.endswith(".sgy")]
    # Get sgy files
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as temp_zip:
        for sgy_file in sgy_files:
            sgy_path = os.path.join(sgy_dir, sgy_file)
            # archive_path = os.path.join("Save", sgy_file)
            archive_path = sgy_file
            temp_zip.write(
                filename=sgy_path,
                arcname=archive_path,
            )
    return StreamingResponse(
        iter([zip_io.getvalue()]),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={file_id}_sgy.zip"}
    )


@app.get("/projects/{file_id}/raw_data")
async def download_raw_data(file_id: str):
    data_dir = os.getenv("MQ_SAVE_DIR")
    file_path = f"{data_dir}/Zips/{file_id}.zip"
    return FileResponse(
        path=f"{file_path}",
        filename=f"{file_id}_raw.zip",
        media_type="application/zip",
    )


@app.get("/projects/{file_id}/processor_zip")
async def download_processor_zip(file_id: str):
    data_dir = os.getenv("MQ_SAVE_DIR")
    file_path = f"{data_dir}/ProcessorReady/{file_id}.zip"
    return FileResponse(
        path=f"{file_path}",
        filename=f"{file_id}_processor.zip",
        media_type="application/zip",
    )


@app.post("/generateResultsEmail")
async def generate_results_email(
        velocity_model: Annotated[UploadFile, File(...)],
        client_name: Annotated[str, Form(...)],
        client_email: Annotated[str, Form(...)],
        file_id: Annotated[str, Form(...)],
):
    data_dir = os.getenv("MQ_SAVE_DIR")
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
async def results_email_form(file_id: str):
    data_dir = os.getenv("MQ_SAVE_DIR")

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


# region 1dS Endpoints


# In-memory storage (in a real app, use a database)
project_data = {}


# Initialize the project data structure if it doesn't exist
def init_project(project_id: str):
    if project_id not in project_data:
        project_data[project_id] = {
            "geometry": [],
            "records": [],
            "plotLimits": {
                "numFreq": 50,
                "maxFreq": 50,
                "numSlow": 50,
                "maxSlow": 0.015
            },
            "freq": [],
            "slow": [],
            "grids": [],
            "picks": [],
            "disperSettings": {
                "layers": [
                    {"startDepth": 0.0, "endDepth": 30.0, "velocity": 760.0, "density": 2.0, "ignore": 0},
                    {"startDepth": 30.0, "endDepth": 44.0, "velocity": 1061.0, "density": 2.0, "ignore": 0},
                    {"startDepth": 44.0, "endDepth": 144.0, "velocity": 1270.657, "density": 2.0, "ignore": 0},
                ],
                "displayUnits": "m",
                "asceVersion": "ASCE 7-22",
                "curveAxisLimits": {
                    "xmin": 0.001,
                    "xmax": 0.6,
                    "ymin": 30,
                    "ymax": 500
                },
                "modelAxisLimits": {
                    "xmin": 50,
                    "xmax": 1400,
                    "ymin": 0,
                    "ymax": 50
                },
                "numPoints": 10,
                "velocityUnit": "velocity",
                "periodUnit": "period",
                "velocityReversed": False,
                "periodReversed": False,
                "axesSwapped": False
            }
        }
    return project_data[project_id]


# data models
class GeometryItem(BaseModel):
    x: float
    y: float
    z: float
    index: Union[str, int]  # Accept either string or integer


class PlotLimits(BaseModel):
    numFreq: int
    maxFreq: float
    numSlow: int
    maxSlow: float


class Layer(BaseModel):
    startDepth: float
    endDepth: float
    velocity: float
    density: float
    ignore: int


class DisperSettingsModel(BaseModel):
    displayUnits: str
    # model settings
    layers: List[Layer]
    asceVersion: str
    modelAxisLimits: dict = {
        "xmin": float,
        "xmax": float,
        "ymin": float,
        "ymax": float
    }
    # curve settings
    curveAxisLimits: dict = {
        "xmin": float,
        "xmax": float,
        "ymin": float,
        "ymax": float
    }
    numPoints: int
    velocityUnit: str
    periodUnit: str
    velocityReversed: bool
    periodReversed: bool
    axesSwapped: bool


class RecordOption(BaseModel):
    id: str
    enabled: bool
    weight: float
    fileName: str


class PickData(BaseModel):
    d1: float
    d2: float
    frequency: float
    d3: float
    slowness: float
    d4: float
    d5: float


class Grid(BaseModel):
    name: str
    data: list
    shape: list


class OptionsModel(BaseModel):
    geometry: List[GeometryItem]
    records: List[RecordOption]
    plotLimits: PlotLimits


@app.post("/process/grids")
async def process_grids_from_input(
        background_tasks: BackgroundTasks,
        sgy_files: Annotated[list[UploadFile], File(...)],
        geometry_data: Annotated[str, Form(...)],  # Format as json
        max_slowness: Annotated[float, Form(...)],
        max_frequency: Annotated[float, Form(...)],
        num_slow_points: Annotated[int, Form(...)],
        num_freq_points: Annotated[int, Form(...)],
        return_freq_and_slow: Annotated[bool, Form(...)] = True,
):
    # Parse geometry data to get geophone spacing as an average
    geometry_data = ast.literal_eval(geometry_data)
    geom_list = [np.array([x['x'], x['y'], x['z']]) for x in geometry_data]
    distances = []
    for idx in range(len(geom_list) - 1):
        distances.append(np.linalg.norm(geom_list[idx] - geom_list[idx + 1]))

    # TODO: Convert between feet and meters.
    geophone_spacing = float(np.average(distances))
    provided_freq_slow = False
    response_data = {
        "data": {
            "grids": []
        }
    }
    for sgy_file in sgy_files:
        local_result = await get_fastapi_file_locally(
            background_tasks=None,
            file_data=sgy_file,
            extension=".sgy"
        )
        if local_result is Exception:
            raise HTTPException(status_code=500, detail=f"Error processing file {sgy_file.filename}.")
        file_descriptor, file_path, extension = local_result
        logger.debug(f"Temp file is {file_path}")
        stream_data = load_segy_segyio([file_path, ])
        preprocess_streams(stream_data)
        p_values, freq_values, slant_stack_grid, forward_grid, reverse_grid, combined_grid, timing_info = (
            vspect_stream(
                stream=stream_data[0],
                geophone_dist=geophone_spacing,
                f_min=0.0,
                f_max=max_frequency,
                f_points=num_freq_points,
                p_points=num_slow_points,
                p_max=max_slowness,
                reduce_nyquist_to_f_max=True,
                ratio_grids=True,
                normalize_grids=True,
            ))
        logger.debug("LenFreq: ", freq_values.shape)
        logger.debug("LenSlow: ", p_values.shape)
        response_data["data"]["grids"].append({
            "name": sgy_file.filename,
            "data": combined_grid.tolist(),
            "shape": combined_grid.shape,
        })

        # Add frequency and slowness data if requested
        if return_freq_and_slow and not provided_freq_slow:
            response_data["data"]["freq"] = {
                "data": freq_values.tolist(),
            }
            response_data["data"]["slow"] = {
                "data": p_values.tolist(),
            }
            provided_freq_slow = True
    # print(response_data)
    # for item in response_data["data"]["grids"]:
    #     print(item)
    return response_data


# Geometry endpoints
# @app.get("/project/{project_id}/geometry")
# async def get_geometry(project_id: str):
#     project = init_project(project_id)
#     return {"geometry": project["geometry"]}

# @app.post("/project/{project_id}/geometry")
# async def save_geometry(project_id: str, geometry: List[GeometryItem]):
#     project = init_project(project_id)
#     project["geometry"] = [item.dict() for item in geometry]
#     return {"status": "success", "count": len(geometry)}

# # Plot limits endpoints
# @app.get("/project/{project_id}/pickPlotLimits")
# async def get_plot_limits(project_id: str):
#     project = init_project(project_id)
#     return project["plotLimits"]

# @app.post("/project/{project_id}/pickPlotLimits")
# async def save_plot_limits(project_id: str, limits: PlotLimits):
#     project = init_project(project_id)
#     project["plotLimits"] = limits.dict()
#     return {"status": "success"}

# model endpoints
@app.get("/project/{project_id}/disper-settings")
async def get_disper_settings(project_id: str):
    project = init_project(project_id)
    return project["disperSettings"]


# grids endpoint
@app.post("/project/{project_id}/grids")
async def dummy_grids_save(
        project_id: str,
        background_tasks: BackgroundTasks,
        sgy_files: Annotated[list[UploadFile], File(...)],
        geometry_data: Annotated[str | None, Form(...)] = None,  # Format as json
        max_slowness: Annotated[float | None, Form(...)] = None,
        max_frequency: Annotated[float | None, Form(...)] = None,
        num_slow_points: Annotated[int | None, Form(...)] = None,
        num_freq_points: Annotated[int | None, Form(...)] = None,
        return_freq_and_slow: Annotated[bool, Form(...)] = True,
):
    # Grab data from stored project if not provided
    if geometry_data is None:
        geometry_data = project_data[project_id]["geometry"]
    else:
        geometry_data = ast.literal_eval(geometry_data)
    if max_slowness is None or max_frequency is None or num_slow_points is None or num_freq_points is None:
        plot_limits = project_data[project_id]["plotLimits"]
        if max_slowness is None:
            max_slowness = plot_limits["maxSlow"]
        if max_frequency is None:
            max_frequency = plot_limits["maxFreq"]
        if num_freq_points is None:
            num_freq_points = plot_limits["numFreq"]
        if num_slow_points is None:
            num_slow_points = plot_limits["numSlow"]
    geom_list = [np.array([x['x'], x['y'], x['z']]) for x in geometry_data]
    distances = []
    for idx in range(len(geom_list) - 1):
        distances.append(np.linalg.norm(geom_list[idx] - geom_list[idx + 1]))

    # TODO: Convert between feet and meters.
    geophone_spacing = float(np.average(distances))
    provided_freq_slow = False
    response_data = {
        "data": {
            "grids": []
        }
    }
    for sgy_file in sgy_files:
        local_result = await get_fastapi_file_locally(
            background_tasks=None,
            file_data=sgy_file,
            extension=".sgy"
        )
        if local_result is Exception:
            raise HTTPException(status_code=500, detail=f"Error processing file {sgy_file.filename}.")
        file_descriptor, file_path, extension = local_result
        logger.debug(f"Temp file is {file_path}")
        stream_data = load_segy_segyio([file_path, ])
        preprocess_streams(stream_data)
        p_values, freq_values, slant_stack_grid, forward_grid, reverse_grid, combined_grid, timing_info = (
            vspect_stream(
                stream=stream_data[0],
                geophone_dist=geophone_spacing,
                f_min=0.0,
                f_max=max_frequency,
                f_points=num_freq_points,
                p_points=num_slow_points,
                p_max=max_slowness,
                reduce_nyquist_to_f_max=True,
                ratio_grids=True,
                normalize_grids=True,
            ))
        logger.debug("LenFreq: ", freq_values.shape)
        logger.debug("LenSlow: ", p_values.shape)
        response_data["data"]["grids"].append({
            "name": sgy_file.filename,
            "data": combined_grid.tolist(),
            "shape": combined_grid.shape,
        })

        # Add frequency and slowness data if requested
        if return_freq_and_slow and not provided_freq_slow:
            response_data["data"]["freq"] = {
                "data": freq_values.tolist(),
            }
            response_data["data"]["slow"] = {
                "data": p_values.tolist(),
            }
            provided_freq_slow = True
    project_data[project_id]["grids"] = response_data["data"]["grids"]
    return response_data


@app.get("/project/{project_id}/grids")
async def dummy_grids_get(project_id: str, return_freq_and_slow=True):
    project = init_project(project_id)
    response_data = {
        "data": {
            "grids": project["grids"]
        }
    }

    # Add frequency and slowness data if requested
    if return_freq_and_slow:
        response_data["data"]["freq"] = {
            "data": project["freq"],
        }
        response_data["data"]["slow"] = {
            "data": project["slow"],
        }

    return response_data


# Geometry endpoints
# @app.get("/project/{project_id}/geometry")
# async def get_geometry(project_id: str):
#     project = init_project(project_id)
#     return {"geometry": project["geometry"]}

# @app.post("/project/{project_id}/geometry")
# async def save_geometry(project_id: str, geometry: List[GeometryItem]):
#     project = init_project(project_id)
#     project["geometry"] = [item.dict() for item in geometry]
#     return {"status": "success", "count": len(geometry)}

# # Plot limits endpoints
# @app.get("/project/{project_id}/pickPlotLimits")
# async def get_plot_limits(project_id: str):
#     project = init_project(project_id)
#     return project["plotLimits"]

# @app.post("/project/{project_id}/pickPlotLimits")
# async def save_plot_limits(project_id: str, limits: PlotLimits):
#     project = init_project(project_id)
#     project["plotLimits"] = limits.dict()
#     return {"status": "success"}

# model endpoints
@app.get("/project/{project_id}/disper-settings")
async def get_disper_settings(project_id: str):
    project = init_project(project_id)
    return project["disperSettings"]


@app.post("/project/{project_id}/disper-settings")
async def save_disper_settings(project_id: str, model: DisperSettingsModel):
    project = init_project(project_id)
    project["disperSettings"] = model.dict()
    return {"status": "success"}


# pick data endpoints
@app.get("/project/{project_id}/options")
async def get_options(project_id: str):
    project = init_project(project_id)
    response_data = {}
    response_data["geometry"] = project["geometry"]
    response_data["records"] = project["records"]
    response_data["plotLimits"] = project["plotLimits"]

    return response_data


@app.post("/project/{project_id}/options")
async def save_options(project_id: str, options: OptionsModel):
    project = init_project(project_id)
    project["geometry"] = options.geometry
    project["records"] = options.records
    project["plotLimits"] = options.plotLimits
    return {"status": "success"}


# pick data endpoint
@app.post("/project/{project_id}/picks")
async def save_picks(project_id: str, picks: List[PickData]):
    project = init_project(project_id)
    project["picks"] = [item.dict() for item in picks]
    return {"status": "success", "count": len(picks)}


@app.get("/project/{project_id}/picks")
async def get_picks(project_id: str):
    project = init_project(project_id)
    return project["picks"]
# endregion
