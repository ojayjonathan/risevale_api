import logging
import math
import os
import random
import re
import shutil
from datetime import datetime
from random import randint
from string import ascii_lowercase, digits
from typing import Optional

from fastapi import UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from google.cloud import storage

from app.core.config import get_settings

PHONE_REGEX = re.compile(r"^\+?\d{8,13}$")


google_storage_client = storage.Client.from_service_account_json(
    os.path.join(
        os.getcwd(),
        "service-account.json",
    )
)


def random_string(len=10) -> str:
    s = ascii_lowercase + digits
    return "".join(
        [s[randint(0, s.__len__() - 1)] for _ in range(len)],
    )


def random_phone() -> str:
    return "".join(["+254", *[str(randint(0, 9)) for _ in range(8)]])


def tz_now() -> datetime:
    return datetime.now()


def is_email(s):
    return "@" in s


def sanitize_filename(filename: str) -> str:
    return os.path.basename(filename)


def upload_image(
    file: UploadFile | None,
    path_prefix: str = "test",
    use_gcp: bool = True,
    is_public: bool = False,
) -> Optional[str]:
    settings = get_settings()

    if not file:
        return None

    try:
        # Prepare directories
        media_root = os.path.join(os.getcwd(), settings.MEDIA_BASE)
        os.makedirs(media_root, exist_ok=True)

        # Clean filename
        filename = sanitize_filename(file.filename)

        # Use forward slashes for GCP
        blob_path = f"{path_prefix.strip('/')}/{filename}"

        # Local storage (always stored first)
        local_file_path = os.path.join(media_root, filename)

        # Save locally
        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Google Cloud Upload
        if use_gcp and settings.ENVIRONMENT not in ("local", "test"):
            bucket_name = (
                settings.GCP_PUBLIC_BUCKET if is_public else settings.GCP_PRIVATE_BUCKET
            )

            bucket = google_storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_file_path)

            # Make file public if required
            if is_public:
                blob.make_public()
                url = blob.public_url.rstrip("/")
            else:
                url = f"https://storage.googleapis.com/{bucket_name}/{blob_path}"

            # Remove local copy
            if os.path.exists(local_file_path):
                os.remove(local_file_path)

            return url

        # Local fallback URL
        return f"{settings.BASE_API_URL.strip('/')}/media/{filename}"

    except Exception as e:
        logging.error(f"Error uploading file {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            500, detail={"message": "Internal server error uploading file"}
        )


def get_image_url(
    file: UploadFile | None,
    path_prefix: str = "test",
    use_gcp: bool = True,
    is_public: bool = True,
) -> Optional[str]:
    settings = get_settings()

    if not file:
        return None

    filename = sanitize_filename(file.filename)
    if use_gcp and settings.ENVIRONMENT not in ("local", "test"):

        blob_path = f"{path_prefix.strip('/')}/{filename}"

        bucket_name = (
            settings.GCP_PUBLIC_BUCKET if is_public else settings.GCP_PRIVATE_BUCKET
        )

        return f"https://storage.googleapis.com/{bucket_name}/{blob_path}"
    else:
        return f"{settings.BASE_API_URL.strip('/')}/media/{filename}"


def normalize_phone_number(
    phone_number: str | None, country_code: str = "254"
) -> str | None:
    if not phone_number:
        return None

    clean_number = re.sub(r"[\s\-$]", "", phone_number)

    if clean_number.startswith(f"+{country_code}"):
        return clean_number
    elif clean_number.startswith(country_code):
        return f"+{clean_number}"
    elif clean_number.startswith("0"):
        return f"+{country_code}{clean_number[1:]}"
    else:
        return f"+{country_code}{clean_number}"


templates = Jinja2Templates(directory="app/templates")


def render_template(path, context=None):
    if context is None:
        context = {}
    template = templates.get_template(path)
    return template.render(**context)


def calculate_total_pages(count: int, page_size: int) -> int:
    return math.ceil(count / page_size)


def format_date(date: datetime | str) -> str:
    if isinstance(date, datetime):
        formatted_date = date.strftime("%B %d, %Y %I:%M %p")
        return formatted_date
    else:
        return date


def mask_email_or_phone(value):
    return mask_email(value) if is_email(value) else mask_phone(value)


def mask_email(email: str) -> str:
    try:
        local_part, domain = email.split("@")
        if len(local_part) <= 1:
            masked_local = "*"
        else:
            masked_local = local_part[0] + "*" * (len(local_part) - 1)
        return f"{masked_local}@{domain}"
    except Exception:
        return email  # fallback if format is unexpected


def mask_phone(phone: str) -> str:
    phone_digits = re.sub(r"[^\d+]", "", phone)

    if phone_digits.startswith("+"):
        country_code_match = re.match(r"^\+\d{1,4}", phone_digits)
        if country_code_match:
            cc_len = len(country_code_match.group(0))
            masked = (
                phone_digits[:cc_len]
                + "*" * (len(phone_digits) - cc_len - 2)
                + phone_digits[-2:]
            )
            return masked
    # Default: mask all but last 2 digits
    return "*" * (len(phone_digits) - 2) + phone_digits[-2:]


def slugify(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")

    suffix = random.randint(10, 99)
    return f"{slug}-{suffix}"
