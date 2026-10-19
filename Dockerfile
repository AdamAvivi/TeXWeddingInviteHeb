# The hosting server gets Python, XeLaTeX, and PDF-to-image tools together.
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    git texlive-xetex texlive-lang-other texlive-pictures poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 'gunicorn>=23,<24'

# Copy only the files the website uses.
COPY app.py invitation.tex ./
COPY templates/ templates/
COPY static/ static/

RUN useradd --create-home website
USER website

# Render provides PORT. Gunicorn serves Flask to the internet.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 120 app:app"]
