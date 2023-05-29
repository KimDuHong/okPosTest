FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install vim \
    && apt-get -y install python3 \
    && rm -rf /var/lib/apt/lists/*

# RUN mkdir /srv/docker-server
# ADD . /srv/docker-server
# WORKDIR /srv/docker-server
# RUN curl -sSL https://install.python-poetry.org | python3 -
# ENV PATH="/root/.local/bin:$PATH"


COPY poetry.lock pyproject.toml /srv/docker-server/
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

CMD ["python", "manage.py", "runserver","127.0.0.1:8000"]
