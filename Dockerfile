FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY inputs.py .
COPY inputs_backup.py .

# Create logs directory
RUN mkdir -p logs

# Set environment variables for security
ENV FLASK_DEBUG=False
ENV PAYMENT_TOKEN=test_token
ENV MAIL_SERVER_KEY=test_key
ENV INTERNAL_AUTH=test_auth

# Expose port for Flask
EXPOSE 5000

# Run the application
CMD ["python", "inputs.py"]
