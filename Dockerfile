# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run sends PORT env var (e.g., 8080)
ENV PORT=8080 PYTHONUNBUFFERED=1

# (EXPOSE is optional for Cloud Run, but keep it aligned)
EXPOSE 8080

# Run Streamlit bound to $PORT and 0.0.0.0
CMD ["bash","-lc","streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"]