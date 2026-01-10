FROM python:3.12-slim AS base

WORKDIR /app

# Install deps 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared + both steps 
COPY common ./common
COPY check_ip ./check_ip
COPY check_ip_batch ./check_ip_batch

# ---- Step 1 image ----
FROM base AS check-ip
CMD ["python", "-m", "check_ip.main"]

# ---- Step 2 image ----
FROM base AS check-ip-batch
CMD ["python", "-m", "check_ip_batch.main"]
