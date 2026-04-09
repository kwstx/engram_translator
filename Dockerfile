FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Force 1 thread for libraries like OpenBLAS/MKL to save memory
ENV OMP_NUM_THREADS 1
ENV MKL_NUM_THREADS 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    swi-prolog \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
