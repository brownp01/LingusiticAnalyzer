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

UPLOAD_FOLDER = 'downloads/'

app = Flask(__name__)


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
    localuploadfolder = None
    logging.info('Started in Analyze')
    returnhtml = ""

    if 'datafile' not in request.files:
        logging.warning('cannot find "datafile" in request object')
        print('No file found')
    else:
        # --------------------------PROCESS USER PDF---------------------------- #
        file = request.files['datafile']
        if request.headers.has_key('Test') and request.headers["Test"] == "True":
            localuploadfolder = 'unit_tests/test_pdfs/'

        if file.filename[-3:] == 'pdf' or file.filename[-4:] == 'docx':
            keyword_list = common_functions.interpretfile(file, localuploadfolder)
            common_functions.plotkeywords(keyword_list)

            returnhtml = common_functions.getscorepage(keyword_list)
        else:
            logging.info('Invalid File type ' + file.filename[-4:] + '. Responding with error page')
            returnhtml = common_functions.geterrorpage()
    return Response(returnhtml, mimetype='text/html')


if __name__ == '__main__':
    app.run()
