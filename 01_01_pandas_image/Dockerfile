FROM python:3.12.8

RUN pip install pandas

# Create a directory and copy the pipeline.py file
WORKDIR /app
COPY pipeline.py pipeline.py

ENTRYPOINT ["python", "pipeline.py"]