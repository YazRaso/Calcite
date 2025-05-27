# Dockerfile
FROM rasa/rasa:3.6.10

WORKDIR /app

COPY .. /app

# Optional: Install extra Python packages for custom actions
COPY ../requirements.txt .
USER root
RUN pip install --no-cache-dir -r requirements.txt

# Train model during build (optional, or do it at runtime)
# RUN rasa train

CMD ["run", "--enable-api", "--cors", "*"]
