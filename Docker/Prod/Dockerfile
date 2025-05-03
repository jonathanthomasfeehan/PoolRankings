# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

# ARG PYTHON_VERSION=3
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/

# The cloud service provider that I am using (Render) seems to not allow secrets to be accessed
# by non-privileged users. So I am going to run the app as root for now.

# ARG UID=10001
# RUN adduser \
#     --disabled-password \
#     --gecos "" \
#     --home "/nonexistent" \
#     --shell "/sbin/nologin" \
#     --no-create-home \
#     --uid "${UID}" \
#     appuser



# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
# RUN --mount=type=cache,target=/root/.cache/pip \
#     --mount=type=bind,source=requirements.txt,target=requirements.txt \
#     python -m pip install -r requirements.txt

COPY requirements.txt requirements.txt

RUN python -m pip install -r requirements.txt




# Switch to the non-privileged user to run the application.
# This is getting moved to the entrypoint script so that seccret files can be updated
# and the app can be run as a non-privileged user.
# USER appuser

# Copy the source code into the container.
COPY ../../. .


# Expose the port that the application listens on.
EXPOSE 5000

# Set flask env variable
ENV FLASK_ENV=Production

# Include env variables for the application.
# Look into render secrets for storing sensitive information.

RUN pip install gunicorn




# Run the application.

# CMD ["/app/Docker/Prod/start.sh"] Used for running a shell script to start the app.
CMD ["gunicorn" , "-w" , "4", "-b", "0.0.0.0:5000" , "app:app"]

