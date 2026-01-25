FROM python:3.14-slim

# https://docs.cloud.google.com/run/docs/tips/python#use_pythonunbuffered_environment_variable_for_logging
ENV PYTHONUNBUFFERED=True

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

# Install dependencies
#   --system: Install to system python (no venv needed in container)
#   --deploy: Fail if Pipfile.lock is out of date
RUN pipenv install --system --deploy

# Copy application code
COPY entrypoint ./
COPY *.py ./
COPY static ./static
COPY templates ./templates

ENTRYPOINT ["./entrypoint"] 

EXPOSE 8080
