from flask import Flask
from flask import Response, request, redirect

app = Flask(__name__)


# Default route, with no additions to the URI
@app.route('/')
def hello_world():
    jsonString = '{"Project":"Linguistic Analyzer", "Author":"Tyler Blanton and Paul Brown", "Client":"Benjamin Pope"}'
    return Response(jsonString, content_type='application/json')


# Route with /Test ('http://127.0.0.1:5000/Test') accepts both posts and puts
@app.route('/Test', methods=['GET', 'POST', 'PUT', 'DELETE'])
def test():
    if request.method == 'POST':
        # redirecting the user to the same page in the case of a POST
        return redirect(request.url)

    elif request.method == 'GET':
        # returning hard-coded html in the case of a GET
        htmlInputString = """
            <form action="http://127.0.0.1:5000/Test"
            enctype="multipart/form-data" method="post">
            <p>
            Type some text (if you like):<br>
            <input type="text" name="textline" size="30">
            </p>
            <p>
            Please specify a file, or a set of files:<br>
            <input type="file" name="datafile" size="40">
            </p>
            <div>
            <input type="submit" value="Send">
            </div>
            </form>
            """
        # mimetype is the response type
        return Response(htmlInputString, mimetype='text/html')
    else:
        # in other cases, we return what type of request it was
        retJson = '{"Request.method" : "' + request.method + '"}'
        return Response(retJson, mimetype='application/json')


if __name__ == '__main__':
    app.run()
