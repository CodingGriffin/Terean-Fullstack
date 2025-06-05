import configparser
import logging
import os
import uuid
import zipfile
from datetime import datetime
from os import PathLike

logger = logging.getLogger("utils.consumer_utils")


def generate_zip_uuid():
    # Mix date with uuid4 (random)
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f") + "-" + uuid.uuid4().__str__()


def generate_zip_name():
    # Mix date with uuid4 (random)
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f") + "-" + uuid.uuid4().__str__() + ".zip"


def write_zip_bytes(
        zip_bytes: bytes,
        zip_dir: str | PathLike,
):
    zip_uuid = generate_zip_uuid()
    zip_name = zip_uuid + ".zip"
    zip_path = os.path.join(zip_dir, zip_name)
    logger.info(f"Writing zip file to {zip_path}")
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)
    logger.info(f"Zip file written to {zip_path}")
    return zip_path, zip_uuid


def extract_zip_data(
        zip_path: str | PathLike,
        extract_dir: str | PathLike,
):
    extracted_folder = os.path.join(extract_dir, os.path.splitext(os.path.basename(zip_path))[0])
    os.makedirs(extracted_folder, exist_ok=True)
    logger.info(f"Extracting {zip_path} to {extracted_folder}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_folder)
    logger.info(f"Extraction completed to {extracted_folder}")
    return extracted_folder


def get_user_info(
        unzipped_dir: str | PathLike,
):
    user_info_file = os.path.join(unzipped_dir, "user.cfg")
    config_parser = configparser.ConfigParser(allow_unnamed_section=True, strict=False)
    config_parser.read(user_info_file)
    user_name = config_parser.get(configparser.UNNAMED_SECTION, "name")
    user_phone = config_parser.get(configparser.UNNAMED_SECTION, "phone")
    user_email = config_parser.get(configparser.UNNAMED_SECTION, "email")
    logger.info(f"Parsed user name: {user_name}, phone: {user_phone}, email: {user_email}")
    return user_name, user_phone, user_email

def extract_project_name(
    unzipped_dir: str | PathLike,
):
    run_config_path = os.path.join(unzipped_dir, "QaData", "run_config.ini")
    config_parser = configparser.ConfigParser(allow_unnamed_section=True, strict=False)
    config_parser.read(run_config_path)
    
    # Read the record output dir from run_config.ini
    record_output_dir = config_parser.get(configparser.UNNAMED_SECTION, "record_output_dir", fallback=None)
    if record_output_dir is None:
        raise ValueError("record_output_dir not found in run_config.ini")
    
    # Extract the project name from record_output_dir
    project_name = os.path.split(os.path.split(record_output_dir)[0])[-1]
    
    return project_name

def make_for_processor_file(
        unzipped_dir: str | PathLike,
        return_limits=False,
):
    try:
        limits_path = os.path.join(unzipped_dir, "QaData", "limits.txt")
        config_parser = configparser.ConfigParser(allow_unnamed_section=True, strict=False)
        config_parser.read(limits_path)
        max_frequency = config_parser.get(configparser.UNNAMED_SECTION, "max_frequency",
                                          fallback="No max frequency detected.")
        min_velocity = config_parser.get(configparser.UNNAMED_SECTION, "min_velocity",
                                         fallback="No min velocity detected.")
    except Exception:
        max_frequency = "No max frequency detected."
        min_velocity = "No min velocity detected."
    try:
        run_config_path = os.path.join(unzipped_dir, "QaData", "run_config.ini")
        config_parser = configparser.ConfigParser(allow_unnamed_section=True, strict=False)
        config_parser.read(run_config_path)
        spacing = config_parser.get(configparser.UNNAMED_SECTION, "geophone_spacing", fallback="No spacing detected.")
    except Exception:
        spacing = "No spacing detected."
    for_processor_path = os.path.join(unzipped_dir, "for_processor.txt")
    with open(for_processor_path, "w") as f:
        f.write(f"Max frequency={max_frequency}\n")
        f.write(f"Min velocity={min_velocity}\n")
        f.write(f"Spacing={spacing}\n")
    return max_frequency, min_velocity, spacing 


def make_for_processor_zip(
        unzipped_dir: str | PathLike,
        processor_zip_dir: str | PathLike,
):
    # Get uuid from dir
    zip_uuid = os.path.basename(unzipped_dir)

    # Find all sgy files
    sgy_dir = os.path.join(unzipped_dir, "Save")
    sgy_files = [x for x in os.listdir(sgy_dir) if x.endswith(".sgy")]
    sgy_paths = [os.path.join(sgy_dir, x) for x in sgy_files]

    # Ensure processor_zip_dir exists
    os.makedirs(processor_zip_dir, exist_ok=True)

    # Create the zip file
    zip_path = os.path.join(processor_zip_dir, f"{zip_uuid}.zip")
    try:
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            for sgy_file_path in sgy_paths:
                zip_file.write(
                    sgy_file_path,
                    os.path.join("Save", os.path.basename(sgy_file_path))
                )
            # Add user.cfg and for_processor.txt
            user_cfg_path = os.path.join(unzipped_dir, "user.cfg")
            zip_file.write(
                user_cfg_path,
                os.path.basename(user_cfg_path)
            )
            for_processor_path = os.path.join(unzipped_dir, "for_processor.txt")
            zip_file.write(
                for_processor_path,
                os.path.basename(for_processor_path)
            )
        logger.info(f"SGY files zipped successfully at {zip_path}")
    except Exception as e:
        logger.error(f"Failed to create zip file {zip_path}: {e}")
    return zip_path
