FROM python:3.12.5-slim-bookworm

# Prevent interactive apt dialogs
ENV DEBIAN_FRONTEND=noninteractive

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libcairo2-dev \
    libjpeg-dev \
    libpng-dev \
    libffi-dev \
    libpango1.0-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set workdir and copy files
WORKDIR /app
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt


EXPOSE 8000

# Use a command to merge files if needed
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]