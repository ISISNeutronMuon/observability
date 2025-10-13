FROM python:3.12-slim
RUN pip install boto3 prometheus_client
COPY s3_metrics_exporter.py /app/s3_metrics_exporter.py
WORKDIR /app
CMD ["python", "s3_metrics_exporter.py"]