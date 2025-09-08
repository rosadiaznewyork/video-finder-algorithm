# Use official Python image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*


# Install Python dependencies globally
RUN pip install --upgrade pip \
    && pip install requests pandas scikit-learn numpy python-dotenv flask flask-cors

# Expose dashboard port
EXPOSE 5001

# Default command: run dashboard API
CMD ["python", "dashboard_api.py"]
