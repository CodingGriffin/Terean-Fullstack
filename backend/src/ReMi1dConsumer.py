import logging
import os
import sys
import traceback

import pika

from config import settings
from utils.consumer_utils import write_zip_bytes, extract_zip_data, make_for_processor_file, \
    make_for_processor_zip, get_user_info
from utils.email_utils import generate_request_received, send_email_gmail, generate_data_received_email

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s::%(lineno)d - %(levelname)s - %(message)s',
    level=logging.INFO,
)

def main():
    download_base_url = settings.DOWNLOAD_BASE_URL
    mq_host_name = settings.MQ_HOST_NAME
    mq_port = settings.MQ_PORT
    mq_virtual_host = settings.MQ_VIRTUAL_HOST
    mq_user_name = settings.MQ_USER_NAME
    mq_password = settings.MQ_PASSWORD
    queue_name = settings.MQ_QUEUE_NAME

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
                    save_dir: str = MQ_SAVE_DIR
            ):
                logger.info(f"Received a Message!")
                logger.info(f"Channel is {ch} of type {type(ch)}")
                logger.info(f"Method is {method} of type {type(method)}")
                logger.info(f"Properties is {properties} of type {type(properties)}")
                zip_path, zip_uuid = write_zip_bytes(body, os.path.join(save_dir, "Zips"))
                extracted_dir = extract_zip_data(zip_path, os.path.join(save_dir, "Extracted"))
                make_for_processor_file(extracted_dir)
                processor_zip_path = make_for_processor_zip(extracted_dir, os.path.join(save_dir, "ProcessorReady"))
                user_name, user_phone, user_email = get_user_info(extracted_dir)

                plain_text, html_text = generate_request_received(user_name)
                send_email_gmail(
                    from_address=settings.GOOGLE_EMAIL,
                    application_password=settings.GOOGLE_EMAIL_APP_PASSWORD,
                    subject="Request Received - 1dS Model Processing",
                    body_plain=plain_text,
                    body_html=html_text,
                    recipients=[user_email, ],  # ["dbarnes@terean.com", "astarr@terean.com"],
                )

                # Send data to processors (AKA Alison)
                plain_text, html_text = generate_data_received_email(
                    user_name=user_name,
                    user_email=user_email,
                    zip_uuid=zip_uuid,
                    base_url=download_base_url,
                )
                send_email_gmail(
                    from_address=settings.GOOGLE_EMAIL,
                    application_password=settings.GOOGLE_EMAIL_APP_PASSWORD,
                    subject="Data Received for user " + user_name,
                    body_plain=None,
                    body_html=html_text,
                    recipients=["dbarnes@terean.com", "astarr@terean.com", "apancha@terean.com",
                                "arosenbergmain@terean.com", "jlouie@terean.com", "dscofield@terean.com"],
                )

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
        logger.info('Interrupted')
        sys.exit(0)
