import logging
import os
import shutil
import sys
import tempfile
import traceback

import pika

from backend.Notebooks.Example1DS import max_freq
from config import settings
from utils.consumer_utils import write_zip_bytes, extract_zip_data, make_for_processor_file, \
    make_for_processor_zip, get_user_info, extract_project_name
from utils.email_utils import generate_request_received, send_email_gmail, generate_data_received_email
from utils.token_manager import TokenManager

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
    backend_url = os.environ.get("BACKEND_URL")
    backend_username = os.environ.get("BACKEND_USERNAME")
    backend_password = os.environ.get("BACKEND_PASSWORD")
    token_manager = TokenManager(backend_url, backend_username, backend_password)

    # Get initial tokens
    _, _ = token_manager.get_initial_tokens()

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
                    max_slow = 1 / min_vel
                    processor_zip_path = make_for_processor_zip(extracted_dir, processor_dir)

                    #TODO SEND DATA TO BACKEND HERE
                    # Send it to the create project with data endpoint
                    # Only send the request received and processor emails once the project is confirmed to have been created.
                    # Extracted data is structured as follows:
                    # extracted/
                    # ├── QaData/            # Qa test data from the field. This should be zipped and sent as a separate additional file
                    # ├── Save/              # Contains Sgy files - all files here should be uploaded to project sgy files
                    # ├── user.cfg           # Contains user information + preferred units. Should be uploaded as an additional file.
                    # └── for_processor.txt  # Contains limits and geophone spacing. Should be uploaded as an additional file.
                    # The sgy files should be added as sgy files in the new project.
                    # The Save dir should be zipped and added as an additional file.
                    # The files, user.cfg and for_processor.txt, should be added as additional files.
                    # The processor_zip generated earlier in this script should also be added as an additional file.
                    plain_text, html_text = generate_request_received(user_name)
                    send_email_gmail(
                        from_address=settings.GOOGLE_EMAIL,
                        application_password=settings.GOOGLE_EMAIL_APP_PASSWORD,
                        subject="Request Received - 1dS Model Processing",
                        body_plain=plain_text,
                        body_html=html_text,
                        recipients=[user_email, ],
                    )

                    # Send data to processors
                    plain_text, html_text = generate_data_received_email(
                        user_name=user_name,
                        user_email=user_email,
                        zip_uuid=zip_uuid,
                        base_url=download_base_url,
                    )
                    # 
                    send_email_gmail(
                        subject="Data Received for user " + user_name,
                        body_plain=None,
                        body_html=html_text,
                        recipients=["dbarnes@terean.com", "astarr@terean.com", "apancha@terean.com",
                                    "arosenbergmain@terean.com", "jlouie@terean.com", "dscofield@terean.com"],
                    )
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
