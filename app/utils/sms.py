import json
import logging

import requests

from app.core.config import get_setting


def send_text_message(
    to, body, schedule_time=None, dlt_template_id=None, settings=get_setting()
):
    if not settings.ENABLE_SMS_NOTIFICATIONS:
        return None

    # ignore deleted or invalid phone numbers
    if "00000000" in to:
        return
    url = "https://bulksms.talksasa.com/api/v3/sms/send"
    headers = {
        "Authorization": f"Bearer {settings.TALK_SASA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {
        "recipient": to,
        "sender_id": settings.TALK_SASA_USERNAME,
        "type": "plain",
        "message": body,
    }
    if schedule_time:
        data["schedule_time"] = schedule_time
    if dlt_template_id:
        data["dlt_template_id"] = dlt_template_id

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()

        if response.status_code == 200 and response_data.get("status") == "success":
            logging.info("SMS sent successfully.")
            return response_data.get("data")
        else:
            error_message: str = response_data.get("message", "Unknown error")
            logging.error(f"Failed to send SMS: {response_data}")

            if "403" in error_message or response.status_code == 403:
                ...  # Notify admin  # client.send_mail_(  #     subject="SMS Delivery Error Notification",  #     recipient=settings.ADMIN_EMAIL,  #     content_type="html",  #     message=(  #         f"<p>Dear Admin,</p>"  #         f"<p>An error occurred while attempting to send an SMS to <strong>{to}</strong>.</p>"  #         f"<p style='color:red;'>Error Details: {error_message}</p>"  #         f"<p>Please check and resolve this issue as soon as possible.</p>"  #         f"<p>Best Regards,<br>Your System</p>"  #     ),  # )
            return f"Failed to send SMS: {error_message}"

    except Exception as e:
        logging.error(f"An error occurred while sending SMS: {str(e)}", exc_info=e)
        return f"An error occurred while sending SMS: {str(e)}"
