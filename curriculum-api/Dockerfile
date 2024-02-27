FROM python:3.10
RUN mkdir /app
COPY requirements.txt /app
WORKDIR /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY . /app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]