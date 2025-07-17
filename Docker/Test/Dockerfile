# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

# ARG PYTHON_VERSION=3
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=1001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser


# For testing purposes
RUN apt-get update && apt-get install -y iputils-ping
RUN apt-get update && apt-get install -y build-essential libffi-dev

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
# RUN --mount=type=cache,target=/root/.cache/pip \
#     --mount=type=bind,source=../../requirements.txt,target=requirements.txt \
#     python -m pip install -r requirements.txt

# Can optionally include dev specific dependencies in the requirements.txt file.
# RUN --mount=type=bind,source=../../requirements.txt,target=requirements.txt \
#     python -m pip install -r requirements.txt

RUN curk -sL https://firebase.tools | bash

COPY requirements.txt ./requirements.txt

RUN python -m pip install -r requirements.txt
RUN pip install pytest python-dotenv
# TODO: check if needed

# Modify dir access for github actions
RUN mkdir -p /app/htmlcov && chown -R appuser /app/htmlcov

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY ../../. .

# Expose the port that the application listens on.
EXPOSE 8080

# Set flask env variable
ENV FLASK_ENV=Development

# Not needed for development
# RUN pip install gunicorn


# Run the application.
# Change to ./app.py when deploying



CMD ["pytest", "--cov=app", "--cov-report=term-missing", "--cov-report=html"]
