FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt

# Copy app
COPY . /app

ENV PYTHONPATH=/app
ENV MAAT_DB_PATH=/app/data/maat.db

EXPOSE 8000

# Use RBAC-enabled v2 API
CMD ["uvicorn", "api.main_v2:app", "--host", "0.0.0.0", "--port", "8000"]
