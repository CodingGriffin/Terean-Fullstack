import ast
import glob
import io
import json
import logging
import os
import tempfile
from typing import Annotated, List

import aiofiles
import numpy as np
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Response, UploadFile
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException

from tereancore.VelocityModel import VelocityModel
from tereancore.plotting_utils import validate_contours, validate_unit_str, build_tick_dicts
from tereancore.sgy_utils import load_segy_segyio, preprocess_streams
from tereancore.twodp_utils import plot_2dp_from_geoct
from tereancore.twods_utils import plot_2ds
from tereancore.utils import lambda0, get_geom_func_from_excel, model_search_pattern
from tereancore.vspect import vspect_stream

from schemas.user_schema import User as UserSchema
from utils.authentication import check_permissions, get_current_user, require_auth_level
from utils.utils import CHUNK_SIZE, get_fastapi_file_locally, validate_id

logger = logging.getLogger(__name__)

process_router = APIRouter(
    prefix="/process",
    tags=["process"],
    dependencies=[Depends(get_current_user)],
)

# Create a global directory for storing SGY files
GLOBAL_DATA_DIR = os.getenv("MQ_SAVE_DIR", "data")
GLOBAL_SGY_FILES_DIR = os.path.join(GLOBAL_DATA_DIR, "SGYFiles")
os.makedirs(GLOBAL_SGY_FILES_DIR, exist_ok=True)


@process_router.post("/2d-p")
async def process_2dp(
    geoct_model_file: Annotated[UploadFile, File(...)],
    background_tasks: BackgroundTasks,
    current_user: UserSchema = Depends(require_auth_level(2)),
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
    """Process 2D P-wave velocity model visualization."""
    if test_mode is not None and test_mode:
        return FileResponse("backend/Terean-logo.png")

    # Get GeoCT Model and TT files as local files
    model_ret = await get_fastapi_file_locally(background_tasks=None, file_data=geoct_model_file)
    if model_ret is Exception:
        raise HTTPException(500, "Error loading model file.")
    _, model_local, _ = model_ret

    if travel_time_file is not None:
        tt_ret = await get_fastapi_file_locally(background_tasks=None, file_data=travel_time_file)
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


@process_router.post("/2d-s")
async def process_2ds(
    velocity_models: Annotated[list[UploadFile], File(...)],
    background_tasks: BackgroundTasks,
    current_user: UserSchema = Depends(require_auth_level(1)),
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
    """Process 2D S-wave velocity model visualization."""
    if test_mode is not None and test_mode:
        logger.info(f"elevation tick size: {elevation_tick_size}")
        logger.info(f"colorbar fraction: {cbar_fraction}")
        logger.info(f"colorbar orientation: {cbar_orientation}")
        logger.info(f"aspect ratio: {aspect_ratio}")
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
            logger.error(f"Failed to parse excel file: {e}")
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
                logger.error("ERROR: Unit string changed between models!")
            ingested_model = VelocityModel.from_file(
                vel_model.file,
                position=position,
                to_meters_factor=to_meters_factor,
            )
            ingested_velocity_models.append(ingested_model)
        else:
            logger.error(f"ERROR Reading file {vel_model.filename}")

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


@process_router.post("/grids")
async def process_grids_from_input(
    record_options: Annotated[str, Form(...)],
    geometry_data: Annotated[str, Form(...)],  # Format as json
    max_slowness: Annotated[float, Form(...)],
    max_frequency: Annotated[float, Form(...)],
    num_slow_points: Annotated[int, Form(...)],
    num_freq_points: Annotated[int, Form(...)],
    return_freq_and_slow: Annotated[bool, Form(...)] = True,
    project_id: Annotated[str, Form(...)] = None,  # Add project_id parameter
    current_user: UserSchema = Depends(get_current_user)
):
    """Process SGY files to generate dispersion grids."""
    check_permissions(current_user, 1)
    logger.info("=== Process Grids START ===")
    logger.info(f"Project ID: {project_id}")
    logger.info(f"Record options: {record_options}")
    logger.info(f"Max slowness: {max_slowness}, Max frequency: {max_frequency}")
    logger.info(f"Num slow points: {num_slow_points}, Num freq points: {num_freq_points}")
    
    # Set default response data
    response_data = {}
    response_data["grids"] = []
    response_data["freq"] = None
    response_data["slow"] = None

    # Parse JSON
    try:
        logger.info("Parsing record options JSON...")
        record_options_list = json.loads(record_options)
        logger.info(f"Parsed record options: {record_options_list}")
        
        logger.info("Parsing geometry data JSON...")
        geometry_list = json.loads(geometry_data)
        logger.info(f"Parsed geometry data: {geometry_list}")
    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")

    geom_list = [np.array([x['x'], x['y'], x['z']]) for x in geometry_list]
    if len(record_options_list) <= 0 or len(geom_list) <= 0:
        logger.warning("No record options or geometry data provided")
        return response_data
    distances = []
    for idx in range(len(geom_list) - 1):
        distances.append(np.linalg.norm(geom_list[idx] - geom_list[idx + 1]))

    # TODO: Convert between feet and meters.
    geophone_spacing = float(np.average(distances))
    logger.info(f"Calculated geophone spacing: {geophone_spacing}")
    
    provided_freq_slow = False
    for i, option in enumerate(record_options_list):
        file_id = option["id"]
        logger.info(f"Processing file {i + 1}/{len(record_options_list)}, ID: {file_id}")
        
        # Validate file_id to prevent path traversal
        if not validate_id(file_id):
            logger.error(f"Invalid file ID: {file_id}")
            continue
        
        # Look for files in both project-specific directory and global directory
        if project_id:
            # First try project-specific directory
            project_dir = os.path.join(GLOBAL_SGY_FILES_DIR, project_id)
            file_path_pattern = os.path.join(project_dir, f"{file_id}.*")
            matching_files = glob.glob(file_path_pattern)
            logger.info(f"Searching in project directory: {file_path_pattern}")
        else:
            matching_files = []
        
        # If not found in project directory, try global directory (for backward compatibility)
        if not matching_files:
            file_path_pattern = os.path.join(GLOBAL_SGY_FILES_DIR, f"{file_id}.*")
            matching_files = glob.glob(file_path_pattern)
            logger.info(f"Searching in global directory: {file_path_pattern}")

        if not matching_files:
            logger.error(f"File with ID {file_id} not found in project {project_id}")
            continue

        file_path = matching_files[0]
        # file_name = os.path.basename(file_path)
        file_name = option["fileName"]
        logger.info(f"Found file: {file_path}, using name: {file_name}")

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
        logger.info(f"Processing complete for {file_name}")
        logger.debug(f"LenFreq: {freq_values.shape}")
        logger.debug(f"LenSlow: {p_values.shape}")
        response_data["grids"].append({
            "name": file_name,
            "data": combined_grid.tolist(),
            "shape": combined_grid.shape,
        })

        # Add frequency and slowness data if requested
        if return_freq_and_slow and not provided_freq_slow:
            response_data["freq"] = {
                "data": freq_values.tolist(),
            }
            response_data["slow"] = {
                "data": p_values.tolist(),
            }
            provided_freq_slow = True
            logger.info("Added frequency and slowness data to response")
            
    logger.info(f"=== Process Grids Complete ===")
    logger.info(f"Processed {len(response_data['grids'])} grids successfully")
    return response_data 