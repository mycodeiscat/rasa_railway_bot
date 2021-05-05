FROM rasa/rasa-sdk:2.5.0

WORKDIR /app

USER root

COPY . /app/actions

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/actions/requirements-actions.txt

USER 1001