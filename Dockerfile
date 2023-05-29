FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install vim \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /okpos
COPY . /okpos/
WORKDIR /okpos

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

COPY poetry.lock pyproject.toml /okpos/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip install -r requirements.txt

# RUN poetry config virtualenvs.create false
# RUN poetry install --no-interaction --no-ansi

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
