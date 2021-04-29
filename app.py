from flask import Flask, request, jsonify, make_response
import requests
import json


# App factory
def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)
    return app


app = create_app("config.py")


# Proxy endpoint for communicating with bot from frontend. Due to security reasons it'd be better to avoid sending
# requests directly to RASA server.
@app.route('/railway', methods=['POST'])
def messageBot():
    text = request.get_json()
    payload = json.dumps({
        "sender": text['sender'],
        "message": text['message']
    })
    headers = {
        'Content-type': 'applications/json'
    }
    bot_response = requests.request("POST", url="http://localhost:5005/webhooks/rest/webhook", headers=headers,
                                    data=payload)
    answer = json.dumps(bot_response.json())
    return answer


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
