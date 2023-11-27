FROM python:3.10.12-alpine as builder

MAINTAINER "Sheya Bernstein sheya@sheyabernstein.com"

ARG APP_NAME=npm_influx_exporter

ARG POETRY_HOME=/app/poetry
ARG POETRY_VENV=/app/.venv

ENV PYTHONPATH="${PYTHONPATH}:/app/$APP_NAME"
ENV PATH="$POETRY_HOME/bin:$POETRY_VENV/bin:$PATH"

WORKDIR /app


FROM builder as python

ARG APP_NAME

RUN apk --no-cache add curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.in-project true

COPY poetry.lock pyproject.toml $APP_NAME/__init__.py ./

RUN poetry install --no-interaction --no-ansi --no-root --without dev


FROM builder as app

ARG APP_NAME
ARG POETRY_VENV

COPY --from=python $POETRY_VENV $POETRY_VENV

COPY $APP_NAME $APP_NAME


FROM app as ci-cd

ARG POETRY_HOME

COPY poetry.lock pyproject.toml ./

COPY --from=python $POETRY_HOME $POETRY_HOME

RUN mkdir -p logs \
    && poetry install --no-interaction --no-ansi --no-root --only dev

COPY tests tests


FROM app as production

ARG APP_NAME

USER nobody:nobody

ENV APP_NAME=$APP_NAME

CMD ["sh", "-c", "python $APP_NAME/main.py"]
