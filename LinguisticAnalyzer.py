from flask import Flask
from flask import Response, request, redirect

app = Flask(__name__)


@app.route('/')
def hello_world():
    jsonString = '{"Project" : "Linguistic Analyzer", "Author" : "Tyler Blanton and Paul Brown", "Client" : "Benjamin Pope"  }'
    return Response(jsonString, content_type='application/json')


@app.route('/Test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        return redirect(request.url)

    elif request.method == 'GET':
        htmlInputString = """
            <form action="http://127.0.0.1:5000/TylerTest"
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
        return Response(htmlInputString)
    else:
        retJson = '{"Request.method" : "' + request.method + '"}'
        return Response(retJson)


if __name__ == '__main__':
    app.run()
