import logging
import os
import shutil
import sys
import tempfile
import traceback
import json
import zipfile
from datetime import datetime

import pika
import requests
from tereancore.ObspyMimics import CustomStream
from tereancore.geometry_utils import get_json_geometry_from_custom_stream, \
    get_json_geometry_from_spacing_and_num_channels

from config import settings
from utils.consumer_utils import write_zip_bytes, extract_zip_data, make_for_processor_file, \
    make_for_processor_zip, get_user_info, extract_project_name
from utils.email_utils import generate_request_received, send_email_gmail, generate_data_received_email
from utils.token_manager import TokenManager
from utils.custom_types.ProjectStatus import ProjectStatus
from utils.custom_types.Priority import Priority

logger = logging.getLogger("consumer_dev_test")
logging.basicConfig(
    format='%(asctime)s - %(name)s::%(lineno)d - %(levelname)s - %(message)s',
    level=logging.INFO,
)

MQ_SAVE_DIR = settings.MQ_SAVE_DIR
logger.info(f"SAVE DIRECTORY = {MQ_SAVE_DIR}")


def main():
    download_base_url = settings.DOWNLOAD_BASE_URL
    mq_host_name = settings.MQ_HOST_NAME
    mq_port = settings.MQ_PORT
    mq_virtual_host = settings.MQ_VIRTUAL_HOST
    mq_user_name = settings.MQ_USER_NAME
    mq_password = settings.MQ_PASSWORD
    queue_name = settings.MQ_QUEUE_NAME

    # Initialize Token Manager
    backend_url = settings.BACKEND_URL
    backend_username = settings.BACKEND_USERNAME
    backend_password = settings.BACKEND_PASSWORD

    # Validate required environment variables
    if not all([backend_url, backend_username, backend_password]):
        logger.error("Missing required environment variables: BACKEND_URL, BACKEND_USERNAME, or BACKEND_PASSWORD")
        raise ValueError("Backend authentication environment variables are required")

    token_manager = TokenManager(backend_url, backend_username, backend_password)

    # Get initial tokens
    try:
        _, _ = token_manager.get_initial_tokens()
        logger.info("Successfully authenticated with backend")
    except Exception as e:
        logger.error(f"Failed to authenticate with backend: {e}")
        raise

    channel = None
    connection = None
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=mq_host_name,
                    port=mq_port,
                    virtual_host=mq_virtual_host,
                    credentials=pika.PlainCredentials(mq_user_name, mq_password)
                )
            )
            channel = connection.channel()
            channel.queue_declare(
                queue=queue_name,
                durable=True,
                exclusive=False,
                auto_delete=False
            )

            def callback(
                ch: pika.adapters.blocking_connection.BlockingChannel,
                method: pika.spec.Basic.Deliver,
                properties: pika.spec.BasicProperties,
                body: bytes,
            ):
                logger.info(f"Received a Message!")
                logger.info(f"Channel is {ch} of type {type(ch)}")
                logger.info(f"Method is {method} of type {type(method)}")
                logger.info(f"Properties is {properties} of type {type(properties)}")

                # Create temporary directory for this message
                temp_dir = tempfile.mkdtemp()
                try:
                    # Create subdirectories in temp directory
                    zip_dir = os.path.join(temp_dir, "Zips")
                    extracted_dir = os.path.join(temp_dir, "Extracted")
                    processor_dir = os.path.join(temp_dir, "ProcessorReady")
                    os.makedirs(zip_dir, exist_ok=True)
                    os.makedirs(extracted_dir, exist_ok=True)

                    # Save and extract zip file to temporary directory
                    zip_path, zip_uuid = write_zip_bytes(body, zip_dir)
                    extracted_dir = extract_zip_data(zip_path, extracted_dir)

                    # Get user info and project name
                    user_name, user_phone, user_email = get_user_info(extracted_dir)
                    project_name = extract_project_name(extracted_dir)
                    max_freq, min_vel, spacing = make_for_processor_file(extracted_dir, return_limits=True)

                    # Get number of channels from one of the sgy files
                    save_dir = os.path.join(extracted_dir, "Save")
                    sgy_paths = [os.path.join(save_dir, x) for x in os.listdir(save_dir) if x.endswith(".sgy")]
                    geometry = "[]"
                    if len(sgy_paths) <= 0:
                        # No sgy files attached
                        logger.warning("No sgy files included in dir.")
                    else:
                        # Attempt to extract info from a test sgy file
                        sgy_test_path = sgy_paths[0]

                        # Load the test sgy
                        sgy_data = CustomStream.from_sgy(sgy_test_path)

                        # Check if loaded spacing matches provided spacing
                        if sgy_data.geophone_spacing == spacing:
                            geometry = get_json_geometry_from_custom_stream(sgy_data)
                        else:
                            geometry = get_json_geometry_from_spacing_and_num_channels(
                                spacing=spacing, num_channels=sgy_data.num_channels,
                            )

                    # Handle numeric conversions with defaults
                    try:
                        max_freq_float = float(max_freq)
                    except (ValueError, TypeError):
                        logger.warning(f"Could not convert max_freq '{max_freq}' to float, using default 50")
                        max_freq_float = 50.0

                    try:
                        min_vel_float = float(min_vel)
                        max_slow = 1 / min_vel_float
                    except (ValueError, TypeError, ZeroDivisionError):
                        logger.warning(
                            f"Could not convert min_vel '{min_vel}' to float or calculate max_slow, using default 0.015")
                        max_slow = 0.015

                    try:
                        spacing_float = float(spacing)
                    except (ValueError, TypeError):
                        logger.warning(f"Could not convert spacing '{spacing}' to float, using default 4.5")
                        spacing_float = 4.5

                    processor_zip_path = make_for_processor_zip(extracted_dir, processor_dir)

                    # Create project in backend
                    try:
                        # Get a valid access token
                        access_token = token_manager.get_valid_access_token()
                        headers = {"Authorization": f"Bearer {access_token}"}

                        # Prepare project data
                        project_data = {
                            "name": project_name,
                            "status": ProjectStatus.not_started.value,
                            "priority": Priority.medium.value,
                            # "received_date": datetime.now().isoformat(),
                            # "plot_limits": json.dumps({
                            #     "numFreq": 50,
                            #     "maxFreq": max_freq_float,
                            #     "numSlow": 50,
                            #     "maxSlow": max_slow
                            # }),
                            # "geometry": geometry,
                        }

                        # Prepare form data for multipart upload
                        form_data = {
                            'project_data': (None, json.dumps(project_data), 'application/json')
                        }

                        # Prepare files to upload
                        files_to_upload = []

                        # Add SGY files from Save directory
                        save_dir = os.path.join(extracted_dir, "Save")
                        if os.path.exists(save_dir):
                            for filename in os.listdir(save_dir):
                                if filename.lower().endswith('.sgy'):
                                    file_path = os.path.join(save_dir, filename)
                                    try:
                                        files_to_upload.append(
                                            ('sgy_files', (filename, open(file_path, 'rb'), 'application/octet-stream'))
                                        )
                                    except Exception as e:
                                        logger.error(f"Failed to open SGY file {file_path}: {e}")
                                        continue

                        # Create a zip of QaData directory
                        qa_data_dir = os.path.join(extracted_dir, "QaData")
                        if os.path.exists(qa_data_dir):
                            qa_zip_path = os.path.join(temp_dir, "QaData.zip")
                            with zipfile.ZipFile(qa_zip_path, 'w', zipfile.ZIP_DEFLATED) as qa_zip:
                                for root, dirs, files in os.walk(qa_data_dir):
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        arcname = os.path.relpath(file_path, extracted_dir)
                                        qa_zip.write(file_path, arcname)
                            files_to_upload.append(
                                ('additional_files', ('QaData.zip', open(qa_zip_path, 'rb'), 'application/zip'))
                            )

                        # Add user.cfg as additional file
                        user_cfg_path = os.path.join(extracted_dir, "user.cfg")
                        if os.path.exists(user_cfg_path):
                            files_to_upload.append(
                                ('additional_files', ('user.cfg', open(user_cfg_path, 'rb'), 'text/plain'))
                            )

                        # Add for_processor.txt as additional file
                        for_processor_path = os.path.join(extracted_dir, "for_processor.txt")
                        if os.path.exists(for_processor_path):
                            files_to_upload.append(
                                ('additional_files',
                                 ('for_processor.txt', open(for_processor_path, 'rb'), 'text/plain'))
                            )

                        # Add the processor zip as additional file
                        if os.path.exists(processor_zip_path):
                            files_to_upload.append(
                                ('additional_files',
                                 (os.path.basename(processor_zip_path), open(processor_zip_path, 'rb'),
                                  'application/zip'))
                            )

                        # Create project with files
                        create_url = f"{backend_url}/project/create"
                        logger.info(f"Using backend url {create_url} to create the project.")
                        logger.info(f"Creating project '{project_name}' with {len(files_to_upload)} files")

                        try:
                            response = requests.post(
                                create_url,
                                headers=headers,
                                data=form_data,
                                files=files_to_upload,
                                timeout=120  # 2 minute timeout for large file uploads
                            )
                            response.raise_for_status()

                            created_project = response.json()
                            logger.info(f"Successfully created project with ID: {created_project['id']}")

                            # Send confirmation emails only after successful project creation
                            plain_text, html_text = generate_request_received(user_name)
                            send_email_gmail(
                                from_address=settings.GOOGLE_EMAIL,
                                application_password=settings.GOOGLE_EMAIL_APP_PASSWORD,
                                subject="Request Received - 1dS Model Processing",
                                body_plain=plain_text,
                                body_html=html_text,
                                recipients=[user_email, ],
                            )
                            # 
                            # # Send data to processors
                            # plain_text, html_text = generate_data_received_email(
                            #     user_name=user_name,
                            #     user_email=user_email,
                            #     zip_uuid=zip_uuid,
                            #     base_url=download_base_url,
                            # )
                            # 
                            # send_email_gmail(
                            #     from_address=settings.GOOGLE_EMAIL,
                            #     application_password=settings.GOOGLE_EMAIL_APP_PASSWORD,
                            #     subject="Data Received for user " + user_name,
                            #     body_plain=None,
                            #     body_html=html_text,
                            #     recipients=["dbarnes@terean.com", "astarr@terean.com", "apancha@terean.com",
                            #                 "arosenbergmain@terean.com", "jlouie@terean.com", "dscofield@terean.com"],
                            # )

                        finally:
                            # Close all opened files
                            for _, file_tuple in files_to_upload:
                                if hasattr(file_tuple[1], 'close'):
                                    file_tuple[1].close()

                    except requests.exceptions.RequestException as e:
                        logger.error(f"Failed to create project in backend: {e}")
                        if hasattr(e, 'response') and e.response is not None:
                            logger.error(f"Response status code: {e.response.status_code}")
                            logger.error(f"Response body: {e.response.text}")
                        raise
                    except Exception as e:
                        logger.error(f"Unexpected error creating project: {e}")
                        raise
                finally:
                    # Clean up temporary directory for this message
                    try:
                        shutil.rmtree(temp_dir)
                        logger.info(f"Cleaned up temporary directory: {temp_dir}")
                    except Exception as e:
                        logger.error(f"Failed to clean up temporary directory: {e}")

            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except Exception as e:
            logger.error(f"Exception occurred:")
            logger.error(f"Exception type:\n {type(e)}")
            logger.error(f"Exception repr:\n {repr(e)}")
            logger.error(f"Exception:\n {e}")
            logger.error(f"Stack Trace:\n {traceback.format_exc()}.")
        finally:
            try:
                if channel is not None:
                    channel.stop_consuming()
                    channel.close()
                if connection is not None:
                    connection.close()
            except Exception as e:
                logger.error(f"Nested exception occurred:")
                logger.error(f"Exception type:\n {type(e)}")
                logger.error(f"Exception repr:\n {repr(e)}")
                logger.error(f"Exception:\n {e}")
                logger.error(f"Stack Trace:\n {traceback.format_exc()}.")
            finally:
                channel = None
                connection = None


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
