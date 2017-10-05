import os
from flask import Flask
from flask import Response, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import requests
import doxypypy
import PyPDF2
import analyze
app = Flask(__name__)


@app.route('/')
def main():
    """
    @summary: This is the function for the base endpoint, the 'front page' of our web app. It will present the user with
    the option to upload a document and submit it.
    @return: Home page
    @rtype: html

    """
    f = open("views/index.html", "r")  # opens file with name of "index.html"
    return Response(f.read(), mimetype='text/html')


# Project route, with no additions to the URI
@app.route('/project')
def project():
    """
    @summary: Returns a simple page that has detailed information about the project.
    @return: Project information
    @rtype: html
    """

    f = open("views/info.html", "r")  # opens file with name of "index.html"
    return Response(f.read(), mimetype='text/html')


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


@app.route('/staticanalyze', methods=['POST'])
def static_analyze():
    """
    @summary: This endpoint is a placeholder. It currently reads an existing pdf (not the uploaded one).
    This is so we can start the bulk of our algorithmic work immediately and focus on connections to UI in the future.
    @return: Basic information about document
    @rtype: html
    """
    # ---------
    # Opening and reading the pdf file
    # ---------
    try:
        pdfFileObj = open('downloads/sample.pdf', 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        print(pdfReader.numPages)
        pageObject = pdfReader.getPage(0)
        pdfText = pageObject.extractText();
        print(pageObject.extractText())
        try:
            print(analyze.analyzeText(pdfText))
        except Exception as ex:
            print(ex)
    except:
        # ---------
        # In the event that something goes wrong, we return an error page.
        # ---------
        f = open("views/invalid_upload.html", "r")  # opens file with name of "index.html"
        return Response(f.read(), mimetype='text/html')

    # ---------
    # Redirecting the user back to the home page
    # ---------
    f = open("views/index.html", "r")  # opens file with name of "index.html"
    return Response(f.read(), mimetype='text/html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    @summary: Receives uploaded document and compares it to an existing document.
    @return: Information regarding uploaded document's similarity to regulatory document
    @rtype: html
    """

    if 'datafile' not in request.files:
        print('No file found')
    else:
        # ---------
        # Reading file and printing contents. This is a testing area at the moment.
        # ---------
        file = request.files['datafile']
        if file:
            fileStuff = file.read()
            print(repr(fileStuff))      # print representation of file bytes
            fileRepr = repr(fileStuff)
            print(fileRepr.replace('//', '/'))

            # confirming that the type of the file is pdf
            if file.filename[-3:] == 'pdf':
                # ---------
                # Experimenting with accessing pdf and converting its {bytes}
                # ---------
                filename = secure_filename(file.filename)
                print(os.getcwd())
                print(type(file))
                print(file.read())
                print(type(file.read()))
                temp = file.read()
                return Response(str(file.read()), mimetype="text/plain")

    # ---------
    # If the file is of an incorrect type, return error page
    # ---------
    f = open("views/invalid_upload.html", "r")  # opens file with name of "index.html"
    return Response(f.read(), mimetype='text/plain')


if __name__ == '__main__':
    app.run()
