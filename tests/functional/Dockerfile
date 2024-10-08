FROM python:3.12.4-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/opt/tests'


WORKDIR /opt

RUN apt-get update && apt-get install postgresql sudo -y && \
addgroup --gid 1000 nonroot && \
adduser --uid 1000 --gid 1000 --disabled-password --gecos "" nonroot && \
echo 'nonroot ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

COPY --chown=nonroot:nonroot  tests/functional/requirements.txt /opt/requirements.txt
RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r /opt/requirements.txt

COPY --chown=nonroot:nonroot tests/functional/ /opt/tests/functional
COPY --chown=nonroot:nonroot app/models/* /opt/tests/models/
COPY --chown=nonroot:nonroot app/core/config.py /opt/tests/core/
COPY --chown=nonroot:nonroot app/alembic/* /opt/alembic/
COPY --chown=nonroot:nonroot app/alembic.ini /opt/

RUN mv /opt/tests/functional/conftest.py /opt/tests/conftest.py && \
    mv /opt/tests/functional/fixtures /opt/tests/ && \
    chmod -R 755 /opt/tests


USER nonroot


ENTRYPOINT find /opt/tests && python3 -m pytest tests -vvv --disable-warnings
