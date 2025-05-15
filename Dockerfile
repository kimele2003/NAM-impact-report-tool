# Use a slim Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 (used by Google Cloud Run)
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]