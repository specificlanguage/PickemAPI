FROM python:3.10 as requirements-stage
WORKDIR /tmp

# Poetry install
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10
WORKDIR /code
EXPOSE 80

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./pickem /code/pickem

CMD ["uvicorn", "pickem.main:app", "--host", "0.0.0.0", "--port", "80"]