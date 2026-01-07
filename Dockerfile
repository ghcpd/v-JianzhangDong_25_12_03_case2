FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    zip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY inputs.py .
COPY inputs_backup.py .
COPY report.json .

# Create necessary directories
RUN mkdir -p configs logs

# Set environment variables with secure defaults
ENV PAYMENT_TOKEN=""
ENV MAIL_SERVER_KEY=""
ENV INTERNAL_AUTH=""
ENV ALLOWED_DOMAINS="localhost,127.0.0.1"
ENV ALLOWED_CONFIG_DIR="./configs"
ENV FLASK_DEBUG="False"

# Expose Flask default port
EXPOSE 5000

# Run the application
CMD ["python", "inputs.py"]
