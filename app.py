import os
import PyPDF2
import requests
from flask import Flask
from flask import Response, request
from werkzeug.utils import secure_filename
from flask import send_file
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
import logging
from os import remove
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
                # common_functions.plotkeywords(keyword_list)

                # --------------------------PROCESS REGULATORY DOCUMENT---------------------------- #
                # reg_text = common_functions.getregulatorydoctext('BSI 14971 Application of risk management to medical devices (2012).pdf')
                reg_text = common_functions.getregulatorydoctext(regfilename)
                reg_keyword_list = analyze_functions.identifykeywords(reg_text)
                analyze_functions.calculatescores(reg_keyword_list, reg_text)
                reg_keyword_list.calculateavgscores()

                common_functions.plothighestfreqkeywords(keyword_list, reg_keyword_list, file.filename, regfilename)
                returnhtml = common_functions.getscorepage(keyword_list)


            else:
                logging.info('Invalid File type ' + file.filename[-4:] + '. Responding with error page')
                returnhtml = common_functions.geterrorpage()


    except:
        returnhtml = common_functions.geterrorpage('An unknown error has occured')

    return Response(returnhtml, mimetype='text/html')


@app.route('/keywordfrequencyimage', methods=['GET'])
def getkwfreqimage():
    """
    @summary: returns file at 'downloads/topkeywordfrequency.png"
    @return:
    @rtype:
    """
    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='jpg')
    pilImage = open('downloads/topkeyword.png', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=True, attachment_filename='keyword.png')


if __name__ == '__main__':
    app.run()
