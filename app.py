import os
import PyPDF2
import requests
from flask import Flask
from flask import Response, request
from werkzeug.utils import secure_filename
import logging
from functionsv1 import common_functions
from functionsv1 import analyze_functions
# import textract

app = Flask(__name__)


UPLOAD_FOLDER = 'downloads/'
loggerStart = 0

@app.route('/')
def main():
    """
    @summary: This is the function for the base endpoint, the 'front page' of our web app. It will present the user with
    the option to upload a document and submit it.
    @return: Home page
    @rtype: html
    """
    # Creating new log file every time the program starts.
    if common_functions.homeCount() == 0:
        analyze_functions.declarelogger()
    f = open("views/index.html", "r")  # opens file with name of "index.html"
    return Response(f.read(), mimetype='text/html')


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

    logging.info('Started in Analyze')
    file_text = []  # List of strings containing document's text
    keywords = []   # List of Keyword object

    if 'datafile' not in request.files:
        logging.warning('cannot find "datafile" in request object')
        print('No file found')
    else:
        file = request.files['datafile']

        if file.filename[-3:] == 'pdf':
            file_text = common_functions.extractpdftext(file, UPLOAD_FOLDER)
        elif file.filename[-4:] == 'docx' or file.filename[-3:] == 'doc':
            file_text = common_functions.extractmicrosoftdoctext(file, UPLOAD_FOLDER)

            # Returns static HTML to user
            f = open("views/processing.html", "r")
            returntext = f.read()
            f.close()
            return Response(returntext, mimetype='text/html')
        else:
            logging.info('Invalid File type ' + file.filename[-3:] + '. Responding with error page')
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
            analyze_functions.printtext(pageObject.extractText())


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