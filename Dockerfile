FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render (and most hosts) inject $PORT at runtime — fall back to 5000 locally.
ENV PORT=5000
EXPOSE 5000

# gunicorn is a production-grade server (Flask's built-in app.run() is dev-only).
# api.app:app means: look inside api/app.py for the variable named "app".
CMD ["sh", "-c", "gunicorn --chdir api --bind 0.0.0.0:${PORT} app:app"]
