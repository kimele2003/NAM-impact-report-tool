# Use a slim Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install system dependencies and run setup.sh
RUN apt-get update -q && apt-get install -y -q wget curl unzip gnupg2 && \
    chmod +x setup.sh && ./setup.sh && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 (used by Google Cloud Run)
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]
