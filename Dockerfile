FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Create data directory for persistence
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app/data

# Switch to non-root user
USER appuser

# Expose port 5000
EXPOSE 5000

# Run the Flask application
CMD ["python3", "backend/app.py"]

