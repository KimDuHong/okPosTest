# okPos Coding Test

![example workflow](https://github.com/KimDuHong/okPosTest/actions/workflows/docker-image.yml/badge.svg)

[![codecov](https://codecov.io/gh/KimDuHong/okPosTest/branch/main/graph/badge.svg?token=VTKIOR9MIT)](https://codecov.io/gh/KimDuHong/okPosTest)
> ### INSTALLATION

```bash
$ git clone https://github.com/KimDuHong/okPosTest
$ cd okPosTest

# Install Poetry
# curl -sSL https://install.python-poetry.org | python3 -

$ poetry install
$ poetry shell
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver

# visit 127.0.0.1:8000
# API document 127.0.0.1:8000/doc
```

> ### Docker Build

```bash
$ docker-compose up --build

# visit 0.0.0.0:8000
```

> ### Test

```bash
$ pytest --cov --cov-report term

> ### APIs

---

| url                  | methods                 | descriptions                     |
| -------------------- | :---------------------- | :------------------------------- |
| `/shop/product`      | GET, POST               | Product 조회 및 추가             |
| `/shop/product/<pk>` | GET, PATCH, PUT, DELETE | Product Detail 조회 및 옵션 수정 |
```
