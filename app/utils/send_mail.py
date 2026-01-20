import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, formataddr
from typing import List, Optional, Union

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# def send_email(
#     port: int,
#     smtp_server: str,
#     sender_email: str,
#     sender_password: str,
#     recipient_email: Union[str, List[str]],
#     subject: str,
#     message: str,
#     content_type: str = "html",
#     reply_to: Optional[str] = None,
#     attachments: Optional[List] = None,
# ):
#
# try:
#     EMAIL_USE_SSL = port == 465
#     EMAIL_USE_TLS = port == 587
#
#     if isinstance(recipient_email, str):
#         recipient_email = [recipient_email]
#
#     recipient_email = [e for e in recipient_email if "deleted" not in e]
#     if len(recipient_email) == 0:
#         return
#
#     logger.info("Preparing email message")
#     mimemsg = MIMEMultipart()
#     sender_name = "Koo Movers Solutions"
#     mimemsg["From"] = formataddr((sender_name, sender_email))
#     mimemsg["To"] = ", ".join(recipient_email)
#     mimemsg["Subject"] = subject
#     mimemsg["Date"] = formatdate(localtime=True)
#     if reply_to:
#         mimemsg["Reply-To"] = reply_to
#
#     mimemsg.attach(MIMEText(message, content_type))
#
#     if attachments:
#         for attachment in attachments:
#             mimemsg.attach(attachment)
#
#     if EMAIL_USE_SSL:
#         logger.info("Connecting via SSL...")
#         context = create_default_context()
#         with smtplib.SMTP_SSL(
#             smtp_server, port, context=context, timeout=30
#         ) as server:
#             server.login(sender_email, sender_password)
#             server.sendmail(sender_email, recipient_email, mimemsg.as_string())
#     else:
#         logger.info("Connecting via TLS...")
#         with smtplib.SMTP(smtp_server, port, timeout=30) as server:
#             server.ehlo()
#             if EMAIL_USE_TLS:
#                 server.starttls()
#                 server.ehlo()
#             server.login(sender_email, sender_password)
#             server.sendmail(sender_email, recipient_email, mimemsg.as_string())
#
#     logger.info(f"Email successfully sent to: {recipient_email}")
#
# except Exception as e:
#     logger.error(
#         f"Failed to send email '{subject}' to {recipient_email}: {e}", exc_info=e
#     )


def send_email(
    port: int,
    smtp_server: str,
    sender_email: str,
    recipient_email: Union[str, List[str]],
    subject: str,
    message: str,
    content_type: str = "html",
    attachments: Optional[List[str]] = None,
    *args,
    **kwargs,
):
    """
    Send email via SMTP Relay (Google Workspace compatible).
    """
    if isinstance(recipient_email, str):
        recipient_email = [recipient_email]

    # filter invalid or deleted addresses
    recipient_email = [e for e in recipient_email if e and "deleted" not in e]
    if len(recipient_email) == 0:
        logger.warning("No valid recipients, skipping email.")
        return

    try:
        logger.info(f"Preparing email message for {recipient_email}")
        mimemsg = MIMEMultipart()
        sender_name = "KooMovers System"
        mimemsg["From"] = formataddr((sender_name, sender_email))
        mimemsg["To"] = ", ".join(recipient_email)
        mimemsg["Subject"] = subject
        mimemsg["Date"] = formatdate(localtime=True)

        mimemsg.attach(MIMEText(message, content_type))

        if attachments:
            for filepath in attachments:
                try:
                    with open(filepath, "rb") as f:
                        part = MIMEApplication(f.read(), Name=filepath.split("/")[-1])
                    part["Content-Disposition"] = (
                        f'attachment; filename="{filepath.split("/")[-1]}"'
                    )
                    mimemsg.attach(part)
                except Exception as e:
                    logger.warning(f"Could not attach file {filepath}: {e}")

        # Connect via Google Workspace SMTP relay
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.send_message(mimemsg)

        logger.info(f"Email successfully sent to: {recipient_email}")

    except Exception as e:
        logger.error(
            f" Failed to send email '{subject}' to {recipient_email}: {e}",
            exc_info=True,
        )
