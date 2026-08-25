# Use Python base image (3.12: 3.9 is past end-of-life, and the stlite build
# already runs this same source on a 3.11/3.12-era CPython under Pyodide)
FROM python:3.12-slim

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