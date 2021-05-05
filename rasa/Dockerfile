# syntax=docker/dockerfile:1
FROM rasa/rasa:latest

USER root

WORKDIR /model

COPY . .

RUN pip3 install -r requirements.txt
RUN python3 -m spacy download xx_ent_wiki_sm

USER 1001

EXPOSE 5005

ENTRYPOINT ["rasa"]

CMD ["--help"]