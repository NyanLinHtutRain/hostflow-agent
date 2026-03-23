FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Cloud Run expects port 8080
ENV PORT=8080
EXPOSE 8080

# Use uvicorn directly for production (better signal handling than python main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
