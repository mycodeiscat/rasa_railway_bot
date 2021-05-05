import json

import requests
from flask import Flask, request, render_template


# App factory
def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)
    return app


app = create_app("config_docker.py")


@app.route('/', methods=['GET'])
def mainPage():
    """
    Endpoint to serve chat webpage
    """
    return render_template('index.html')


@app.route('/railway', methods=['POST'])
def messageBot():
    """
    Proxy endpoint for communicating with bot from frontend. Due to security reasons it'd be better to avoid sending
    requests directly to RASA server.
    """
    text = request.get_json()
    payload = json.dumps({
        "sender": text['sender'],
        "message": text['message']
    })
    bot_response = requests.post(url=app.config["RASA"],
                                 data=payload)
    answer = json.dumps(bot_response.json())
    return answer
