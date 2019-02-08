FROM python:3.7

COPY pyproject.* /app/
WORKDIR /app
RUN python3 -m pip install poetry && poetry config settings.virtualenvs.create false
RUN poetry install --no-dev

COPY . /app/

CMD ["python3", "-u", "-OO", "/app/run.py"]
