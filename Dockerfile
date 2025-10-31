# ================================
#   Base Image
# ================================
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# ================================
#   Install Dependencies
# ================================
# Copy dependency list first (for better caching)
COPY requirements.txt .

# Install system and Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ================================
#   Application Files
# ================================
# Copy the rest of the app
COPY . .

# ================================
#   Gunicorn Setup
# ================================
RUN pip install --no-cache-dir gunicorn

# Expose Django’s default port
EXPOSE 8000

# ================================
#   Start Command
# ================================
# Use Gunicorn to run Django in production mode
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers=3", "config.wsgi:application"]