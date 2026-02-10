FROM python:3.14-alpine
RUN addgroup appgroup && adduser --disabled-password --gecos "" --no-create-home -s /bin/sh appuser -G appgroup
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN rm requirements.txt

ENV PORT=5000
ENV HOST="0.0.0.0"

USER appuser
CMD ["python", "app.py"]
