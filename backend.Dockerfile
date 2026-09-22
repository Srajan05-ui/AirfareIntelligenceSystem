FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY api/ ./api/
COPY database/ ./database/
COPY ingestion/ ./ingestion/
COPY processing/ ./processing/

# Set Python path so imports work correctly
ENV PYTHONPATH=/app

# Expose FastAPI port
EXPOSE 8000

# Run the secure Uvicorn server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
