FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

USER 10001

EXPOSE 5002

HEALTHCHECK --interval=30s --timeout=5s \
  --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5002/health', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5002", \
     "--workers", "1", "--access-logfile", "-", \
     "--error-logfile", "-", "app:app"]
