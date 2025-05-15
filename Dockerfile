# Use a slim Python base image
FROM python:3.10-slim

ENV PYTHONPATH=/NAM-impact-report-tool

# Set the working directory
WORKDIR /NAM-impact-report-tool

RUN apt-get update -q && apt-get install -y -q --no-install-recommends \
    wget curl unzip gnupg2 && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run setup.sh to configure the environment
RUN chmod +x setup.sh && ./setup.sh && rm -rf /var/lib/apt/lists/*

# Expose port 8080 (used by Flask app)
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]