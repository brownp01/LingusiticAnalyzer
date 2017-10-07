import os
import PyPDF2
import requests
from flask import Flask
from flask import Response, request
from werkzeug.utils import secure_filename

from functionsv1 import analyze_functions

app = Flask(__name__)

# TODO: Look into logging/implement

UPLOAD_FOLDER = '/downloads'

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


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    @summary: Receives uploaded document and compares it to an existing document.
    @return: Information regarding uploaded document's similarity to regulatory document
    @rtype: html
    """
    file_text = []
    if 'datafile' not in request.files:
        print('No file found')
    else:
        file = request.files['datafile']
        if file.filename[-3:] == 'pdf':
            filename = secure_filename(file.filename)
            f = open('downloads/' + filename, 'w+')    # Creates file with given filename
            f.close()
            file.save(os.path.join('', filename))   # saves uploaded file

            pdfFileObj = open(filename, 'rb')       # Opens uploaded file
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            for i in range(0, pdfReader.numPages):
                pageObject = pdfReader.getPage(i)

                # saves text of uploaded pdf into a list of strings
                file_text.append(pageObject.extractText().strip('\n'))

            os.remove(filename)     # Removes created file from directory.

            # Returns static HTML to user
            f = open("views/processing.html", "r")
            return Response(f.read(), mimetype='text/html')

        # Returns error page
    f = open("views/invalid_upload.html", "r")
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

    try:
        # ---------
        # Opening and reading the pdf file
        # ---------
        pdfFileObj = open('downloads/ipsum.pdf', 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

        for i in range(0, pdfReader.numPages):
            pageObject = pdfReader.getPage(i)
            pdfText = pageObject.extractText()
            analyze_functions.printText(pageObject.extractText())


    except Exception as ex:
        # ---------
        # In the event that something goes wrong, we return an error page.
        # ---------
        print(ex)
        f = open("views/invalid_upload.html", "r")  # opens file with name of "index.html"
        return Response(f.read(), mimetype='text/html')

    # ---------
    # Redirecting the user back to the home page
    # ---------
    f = open("views/index.html", "r")  # opens file with name of "index.html"
    return Response(f.read(), mimetype='text/html')


if __name__ == '__main__':
    app.run()
