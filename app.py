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
    file_text = []  # List of strings containing document's text
    keyword_list = []
    keywords = []   # List of Keyword object

    returnhtml = ""

    if 'datafile' not in request.files:
        logging.warning('cannot find "datafile" in request object')
        print('No file found')
    else:
        file = request.files['datafile']
        if request.headers.has_key('Test') and request.headers["Test"] == "True":
            localuploadfolder = '/Users/tlblanton/Documents/UC_Denver/2017_fall/senior_design/linguistic_analyzer/11_7_17\
/LinguisticAnalyzer/unit_tests/test_pdfs/'

        if file.filename[-3:] == 'pdf':
            file_text = common_functions.extractpdftext(file, localuploadfolder)
            common_functions.printStringList(file_text)

            # -----------IDENTIFYING KEYWORDS----------- #
            keyword_list = analyze_functions.identifykeywords(file_text)
            #keyword_list = analyze_functions.identifykeywordswithsentiment(file_text)

            for i in range(0, keyword_list.uniquekeywords):
                # TODO:Fix frequencies, they are not accurate
                print(keyword_list.list[i].word + '-' + str(keyword_list.list[i].frequency))

            common_functions.outputkeywordtotext(keyword_list)

            common_functions.plotmostcommon(file_text, keyword_list)

            f = open("views/score_response.html", "r")
            returnhtml = f.read().replace('#--KEYWORD_SCORE--#', str(keyword_list.getkeywordscore())).\
                replace('#--YULES_SCORE--#', str(keyword_list.getyuleskscore()))
            f.close()

        elif file.filename[-4:] == 'docx':    # No ability to read '.doc' yet

            file_text = common_functions.extractmicrosoftdocxtext(file)
            common_functions.printStringList(file_text)

            # -----------IDENTIFYING KEYWORDS----------- #
            keyword_list = analyze_functions.identifykeywords(file_text)

            for i in range(0, keyword_list.uniquekeywords):
                # TODO:Fix frequencies, they are not accurate
                print(keyword_list.list[i].word + '-' + str(keyword_list.list[i].frequency))

            # Returns static HTML to users
            f = open("views/score_response.html", "r")
            returnhtml = f.read().replace('#--KEYWORD_SCORE--#', str(keyword_list.getkeywordscore())). \
                replace('#--YULES_SCORE--#', str(keyword_list.getyuleskscore()))
            f.close()

        else:
            logging.info('Invalid File type ' + file.filename[-3:] + '. Responding with error page')

            # Returns error page
            f = open("views/invalid_upload.html", "r")
            returnhtml = f.read()
            f.close()
    return Response(returnhtml, mimetype='text/html')


if __name__ == '__main__':
    app.run()
