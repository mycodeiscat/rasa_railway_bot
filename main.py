from app import app
import webbrowser
import os

filename = './deploy/index.html'

if __name__ == "__main__":
    webbrowser.open('file://' + os.path.realpath(filename), new=2)
    app.run(debug=True, host='0.0.0.0', port=8080)
