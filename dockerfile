# Use a lightweight Python base image
FROM python:3.10-slim

# Set a working directory
WORKDIR /app

# Copy requirements first, so Docker can cache the pip install steps
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . /app

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Use Gunicorn to serve your Dash app on port 8080
# Note: We reference "app:server" because inside app.py we have "server = app.server"
CMD exec gunicorn app:server \
    --bind 0.0.0.0:8080 \
    --workers 2 \
    --threads 8
