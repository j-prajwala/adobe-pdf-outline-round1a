# Use official Python 3.10 slim base image (amd64 compatible)
FROM python:3.10-slim


# Set working directory inside container
WORKDIR /app

# Copy requirements & source code
COPY requirements.txt .
COPY src/ ./src/

# Create empty input and output directories (these will be mounted at runtime)
RUN mkdir -p input output

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run your script
CMD ["python", "src/extract_headings.py"]
