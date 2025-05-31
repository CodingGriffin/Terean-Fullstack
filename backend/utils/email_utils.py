import email.utils
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from os import PathLike
from backend.utils.streaming_utils import create_email_attachment_stream

logger = logging.getLogger("backend.utils.email_utils")

def send_email_gmail(
        from_address: str,
        application_password: str,
        subject: str,
        recipients: list[str],
        bcc_recipients: list[str] | None = None,
        body_plain: str | None = None,
        body_html: str | None = None,
        attachments: list[str | PathLike] | None = None,
        from_name: str | None = None,
        use_streaming: bool = True,
) -> None:
    """
    Sends an email with the specified subject, plain text body, HTML body, recipients, and optional attachments.

    :param from_address: Email address to send the email from.
    :param application_password: Application-specific password for authentication.
    :param subject: Subject of the email.
    :param body_plain: Plain text version of the email body.
    :param body_html: HTML version of the email body.
    :param recipients: List of recipient email addresses.
    :param bcc_recipients: List of BCC recipient email addresses (default is None).
    :param attachments: List of file paths to attach to the email (default is None).
    :param from_name: Name to use in the "From" field (default is None).
    :param use_streaming: Whether to use streaming for large attachments (default is True).
    """
    smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtpserver.ehlo()
    smtpserver.login(from_address, application_password)

    msg = MIMEMultipart('mixed')
    if from_name is not None:
        msg['From'] = email.utils.formataddr((from_name, from_address))
    else:
        msg['From'] = from_address
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject

    # Add attachments if provided
    if attachments:
        for file_path in attachments:
            if os.path.exists(file_path):
                # Check file size to decide whether to use streaming
                file_size = os.path.getsize(file_path)
                # Use streaming for files larger than 10MB
                if use_streaming and file_size > 10 * 1024 * 1024:
                    logger.info(f"Using streaming for large attachment: {file_path} ({file_size} bytes)")
                    part = create_email_attachment_stream(file_path)
                else:
                    # Original implementation for smaller files
                    part = MIMEBase('application', 'octet-stream')
                    with open(file_path, 'rb') as attachment:
                        part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
                msg.attach(part)
            else:
                logger.warning(f"Attachment {file_path} not found and will be skipped.")

    # Attach both plain text and HTML versions of the body
    # if body_plain:
    #     msg.attach(MIMEText(body_plain, 'plain'))
    if body_html:
        msg.attach(MIMEText(body_html, 'html'))
    if not body_plain and not body_html:
        logger.warning("No email body provided. Skipping.")
        return

    if bcc_recipients is not None:
        recipients = [recipients] + bcc_recipients

    # Send email
    smtpserver.sendmail(from_address, recipients, msg.as_string())
    smtpserver.close()


def generate_email_signature() -> str:
    """
    Generates an HTML email signature with a separator and an image linked to the website.

    :return: HTML string containing the email signature.
    """
    return """<div>
        <p style="line-height:2;">--</p>
        <p style="line-height:2;"><a href="https://www.terean.com" target="_blank">
            <img src="https://images.squarespace-cdn.com/content/v1/635dd9869747a0469c6db87c/854c476b-99b8-406e-b6b2-a41dce0c9e13/Terean-logo-%C2%AE-2000.png" alt="Terēan Logo" style="height:50px;">
        </a></p>
        <p style="font-size:8pt; font-family:sans-serif; line-height:0.4;">
            AI Processing Tool<br>
        </p>
        <p style="font-size:7pt; font-family:sans-serif; line-height:2;">
            Support: +1 775-258-1991<br>
            <a href="mailto:processing@terean.com">processing@terean.com</a> | 
            <a href="https://www.terean.com" target="_blank">www.terean.com</a>
        </p>
        <p style="font-size:7pt; font-family:sans-serif; color:#CCCCCC; line-height:2;">
            This email and any files transmitted with it are property of Terēan®, are confidential, and are intended solely for the use of the individual or entity to whom this email is addressed. 
            If you are not one of the named recipient(s) or otherwise have reason to believe that you have received this message in error, please notify the sender and delete this message immediately from your computer. 
            Any other use, retention, dissemination, forwarding, printing, or copying of this email is strictly prohibited.
        </p>
    </div>"""


def generate_request_received(name: str) -> tuple[str, str]:
    """
    Generates plain text and HTML email bodies with the given name.

    :param name: The recipient's name to personalize the email.
    :return: A tuple containing the plain text and HTML email bodies.
    """
    plain_text = f"""Hello {name},

Thank you for your request! We've received your data and will return your 1dS model shortly -- including depth, layer thickness, and velocity details.

If you have any questions in the meantime, please feel free to reach out.

Best regards,
Terēan Support Team
"""
    html_text = f"""<html>
<head></head>
<body>
    <p>Hello {name},</p>
    <p>Thank you for your request! We've received your data and will return your 1dS model shortly -- including depth, layer thickness, and velocity details.</p>
    <p>If you have any questions in the meantime, please feel free to reach out.</p>
    <p>Best regards,<br>Terēan Support Team</p>
    {generate_email_signature()}
</body>
</html>
"""
    return plain_text, html_text


def generate_vs_surf_results(name: str) -> tuple[str, str]:
    """
    Generates plain text and HTML email bodies for VsSurf 1dS results with the given name.

    :param name: The recipient's name to personalize the email.
    :return: A tuple containing the plain text and HTML email bodies.
    """
    plain_text = f"""Hello {name},

Your VsSurf 1dS results are attached!

Did you know that this same dataset can be used to generate a 2D shear-wave velocity section, allowing you to visualize changes across your entire site? Visit our On-Demand Processing page to learn more.

If you have any questions or need further assistance, feel free to reach out.

Best regards,
Terēan Support Team
"""
    html_text = f"""<html>
<head></head>
<body>
    <p>Hello {name},</p>
    <p>Your VsSurf 1dS results are attached!</p>
    <p>Did you know that this same dataset can be used to generate a 2D shear-wave velocity section, allowing you to visualize changes across your entire site? Visit our <a href="https://www.terean.com/processing" target="_blank">On-Demand Processing page</a> to learn more.</p>
    <p>If you have any questions or need further assistance, feel free to reach out.</p>
    <p>Best regards,<br>Terēan Support Team</p>
    {generate_email_signature()}
</body>
</html>
"""
    return plain_text, html_text


def generate_data_received_email(user_name, user_email, zip_uuid, base_url):
    # Generate links
    processor_download_link = f"{base_url}/projects/{zip_uuid}/processor_zip"
    raw_data_download_link = f"{base_url}/projects/{zip_uuid}/raw_data"
    email_form_link = f"{base_url}/projects/{zip_uuid}/results_email_form"

    plain_text = f"""
    Data has been received from {user_name} at {user_email}.

    Links:
    Processor zip: {processor_download_link}
    Raw data: {raw_data_download_link}
    Email form: {email_form_link}
    """
    html_text = f"""<html>
    <head></head>
    <body>
        <p>Data has been received from {user_name} at {user_email}.</p>
        <p>Links:</p>
        <p>(zip links may need to be copy-pasted in your browser)</p>
        <p>Processor zip: <a href="{processor_download_link}" target="_blank">{processor_download_link}</a></p>
        <p>Raw data zip: <a href="{raw_data_download_link}" target="_blank">{raw_data_download_link}</a></p>
        <p>Email form: <a href="{email_form_link}" target="_blank">{email_form_link}</a></p>
    </body>
    </html>
    """
    return plain_text, html_text
