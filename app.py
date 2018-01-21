from flask import Flask
from flask import Response, request
from flask import send_file
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
import logging
from functionsv1 import common_functions
from functionsv1 import analyze_functions
import sys
import os
import ctypes


UPLOAD_FOLDER = 'downloads/'

app = Flask(__name__)
loggerStart = 0

def resource_path(relative_path):
    """
    Summary: Function to determine correct file path of directories for use within an IDE or executable.

    :param str relative_path: the path of a directory relative to a local environment
    :return: base_path in relation to executable environment and relative_path of local environment
    :rtype: string

    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

VIEWS = resource_path("views/")


@app.route('/')
def main():
    """
    Home page of the Linguistic Analyzer API

    :return: Home page
    :rtype: html
    """
    # Creating new log file every time the program starts.
    if common_functions.homeCount() == 0:
        analyze_functions.declarelogger()
    f = open(VIEWS + "index.html", "r")  # opens file with name of "index.html"
    return Response(f.read(), mimetype='text/html')


@app.route('/project')
def project():
    """
    Returns an html page containing details about the Linguistic Analyzer project.

    :return: Home page
    :rtype: html
    """

    f = open(VIEWS + "info.html", "r")  # opens file with name of "index.html"
    return Response(f.read().replace('#--DESCRIPTION_TITLE--#', 'Project Information').replace('#--DESCRIPTION--#',
                    "This Linguistic Analyzer lets the user upload a description document and compares that document \
                    against a regulatory document using Yule's k and Yule's i Algorithms, as well as a keyword scores algorithm.\
                    The results of the calculations are then displayed graphically to the user."), mimetype='text/html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Receives uploaded document and comparison document choice and executes logic to compare them.

    :return: Information regarding the uploaded document's similarity to regulatory document
    :rtype: html
    """

    try:

        regfilename = request.form.get('regdocname')
        localuploadfolder = None
        logging.info('Started in Analyze')
        returnhtml = ""
        # regfilename = 'small_sample.pdf'

        if 'datafile' not in request.files or request.files['datafile'].filename == "":
            logging.warning('Cannot find "datafile" in request object')
            returnhtml = common_functions.geterrorpage('No user file selected')
            return Response(returnhtml, mimetype='text/html')
        elif regfilename is None or regfilename == 'Select':
            logging.warning('No regulatory document specified')
            returnhtml = common_functions.geterrorpage('No regulatory document specified')
            return Response(returnhtml, mimetype='text/html')
        else:
            # --------------------------PROCESS USER DOCUMENT---------------------------- #
            file = request.files['datafile']
            if request.headers.has_key('Test') and request.headers["Test"] == "True":
                localuploadfolder = 'unit_tests/test_pdfs/'

            if file.filename[-3:] == 'pdf' or file.filename[-4:] == 'docx':
                keyword_list = common_functions.interpretfile(file, localuploadfolder)

                # --------------------------PROCESS REGULATORY DOCUMENT---------------------------- #
                reg_keyword_list = common_functions.interpretexistingfile(regfilename)

                # ---------------------------KEYWORD PLOT FUNCTIONS------------------------------- #
                common_functions.plotkeywordsalience(keyword_list, reg_keyword_list, file.filename, regfilename)
                common_functions.plotkeywordscores(keyword_list, reg_keyword_list, file.filename, regfilename)
                common_functions.plotkeywordfrequency(keyword_list, reg_keyword_list, file.filename, regfilename)
                returnhtml = common_functions.getscorepage(keyword_list, reg_keyword_list)


            else:
                logging.info('Invalid File type ' + file.filename[-4:] + '. Responding with error page')
                returnhtml = common_functions.geterrorpage()

    except Exception as e:
        returnhtml = common_functions.geterrorpage('An unknown error has occured')

    return Response(returnhtml, mimetype='text/html')


@app.route('/keywordsalienceimage', methods=['GET'])
def getkwsalienceimage():
    """
    Returns png image of a graph of top salience keywords

    :return: graph
    :rtype: png
    """
    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='jpg')
    pilImage = open('downloads/topsalience.png', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=True, attachment_filename='keyword.png')


@app.route('/keywordscoresimage', methods=['GET'])
def getkwscoresimage():
    """
    Returns png image of a graph of keyword scores

    :return: graph
    :rtype: png
    """
    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='jpg')
    pilImage = open('downloads/topkeywordscores.png', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=True, attachment_filename='keyword.png')


@app.route('/keywordfrequencyimage', methods=['GET'])
def getkwfreeqimage():
    """
    Returns Keyword frequency graph

    :return: graph
    :rtype: png
    """
    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='jpg')
    pilImage = open('downloads/topkeywordfrequency.png', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=True, attachment_filename='keyword.png')


@app.route('/yulesinfo', methods=['GET'])
def yulesinfo():
    """
    Yule's Info

    :return: Page that describes Yule's k and Yule's i algorithms
    :rtype: html
    """
    f = open("views/info.html", "r")  # opens file with name of "index.html"
    return Response(f.read().replace('#--DESCRIPTION_TITLE--#', "Yule's k and Yule's i algorithms")\
        .replace('#--DESCRIPTION--#', "\'Yule's k\' and \'Yule's i\' are calculated values that represent the \
        semantic richness of a given text. We utilize this algorithm because semantic richness is one benchmark by \
        which technical writers can measure the effectiveness of what they have written. The score is largely useful as\
        a way to compare an uploaded document's significance against the significance of a regulatory text."),mimetype='text/html')


@app.route('/comparisoninfo', methods=['GET'])
def comparisoninfo():
    """
    Comparison Information

    :return: graph html page that describes the Linguistic Analyzer's Comparison Score
    :rtype: html
    """
    f = open("views/info.html", "r")  # opens file with name of "index.html"
    return Response(f.read().replace('#--DESCRIPTION_TITLE--#', "Yule's k and Yule's i algorithms") \
                    .replace('#--DESCRIPTION--#', "This score takes into account the calculated score, \
                    frequency, and adjacent words for each keyword in both documents. If the given documents are \
                    identical then the score will be 100. This score is useful for seeing how well the semantic \
                    choices made in the user's document match up with the semantics present in the regulatory \
                    document."), mimetype='text/html')


if __name__ == '__main__':
    app.run()
