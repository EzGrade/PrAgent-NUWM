FROM python:3.12-slim AS base

# Set the working directory
WORKDIR /app

# Install system dependencies for OpenCV and other packages
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY pyproject.toml poetry.lock ./

# Install the dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the source code
COPY . .

RUN chmod +x entrypoint.sh

# Run the application
CMD ["/app/entrypoint.sh"]