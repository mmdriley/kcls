FROM python:3.14-slim

# https://docs.cloud.google.com/run/docs/tips/python#use_pythonunbuffered_environment_variable_for_logging
ENV PYTHONUNBUFFERED True

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

# Install dependencies
#   --system: Install to system python (no venv needed in container)
#   --deploy: Fail if Pipfile.lock is out of date
RUN pipenv install --system --deploy

# Copy the content of the local src directory to the working directory
COPY . .

# Default environment variables (can be overridden at runtime)
# Secrets should ideally be injected via secret manager or env vars at deploy time,
# not baked into the image, but we declare them here for clarity.
ENV KCLS_CREDS=""
ENV APP_TOKEN=""
ENV PORT=8080

# Run the web service on container startup using gunicorn
# --workers 1: Single worker is usually sufficient for this lightweight app
# --threads 8: Handle concurrent requests (useful for blocking I/O like scraping)
# --timeout 0: Let Cloud Run handle timeouts
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
