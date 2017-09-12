from flask import Flask
from flask import Response, request, redirect
import requests

app = Flask(__name__)


@app.route('/')
def default():
    f = open("constants/index.html", "r")  # opens file with name of "index.html"
    return Response(f.read(), mimetype='text/html')


# Project route, with no additions to the URI
@app.route('/project')
def hello_world():
    jsonString = '{"Project":"Linguistic Analyzer", "Author":"Tyler Blanton and Paul Brown", "Client":"Benjamin Pope"}'
    return Response(jsonString, content_type='application/json')


# Route with /Test ('http://127.0.0.1:5000/Test') accepts both posts and puts

@app.route('/Test', methods=['GET', 'POST', 'PUT', 'DELETE'])
def test():
    if request.method == 'POST':
        # This POST parses json data
        jsonData = request.get_json()
        print(jsonData["this"])
        return Response('<p>POST response. </p>', mimetype='text/html')

    elif request.method == 'GET':
        # This GET samples calling to an API
        r = requests.get('https://api.github.com/users/tlblanton')
        return Response(r.text, mimetype='application/json')
    else:
        # in other cases, we return what type of request it was
        retJson = '{"Request.method" : "' + request.method + '"}'
        return Response(retJson, mimetype='application/json')


@app.route('/api/v1/analyze', methods=['POST'])
def analyze():
    return Response('<p>api/v1/analyze placeholder</p>', mimetype='text/html')


if __name__ == '__main__':
    app.run()
