FROM python:3.11-alpine
WORKDIR /app
COPY . .  
RUN pip install --no-cache-dir redis websockets watchdog pandas
CMD ["python", "main.py" ]
