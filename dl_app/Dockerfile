FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /dl_app

COPY requirements.txt .

# Install Poetry
RUN pip install -r requirements.txt


COPY . /dl_app

EXPOSE ${PORT}