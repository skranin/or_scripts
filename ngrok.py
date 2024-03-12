from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def hello_world():
    try:
      for i in request.json:
        print(i, ":", request.json[i])
    except:
        print(request.values)


    return "Success", 201

if __name__ == '__main__':
    app.run(debug=True, port=8666)

# Readme:
# 1. Start script
# 2. ngrok http 8666
# 3. All requests sent to the ngrok https endpoint should be logged by script
