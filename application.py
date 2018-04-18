from flask import Flask, Response, request, send_file, redirect

from shutil import copyfileobj
from tempfile import NamedTemporaryFile
import logging
from functionsv1 import common_functions
from functionsv1 import analyze_functions
import sys
import os
import time
import json
#import progressbar
#from multiprocessing import Pool, Process


UPLOAD_FOLDER = 'downloads/'

application = Flask(__name__)
loggerStart = 0  #log file counter.



def resource_path(relative_path):
    """
    Summary: Function to determine correct file path of directories for use within an IDE or executable.


    :param str relative_path: the path of a directory relative to a local environment
    :return: *base_path* in relation to executable environment and *relative_path* of local environment
    :rtype: str

    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)


VIEWS = resource_path("views/")


@application.route('/')
def main():
    """
    Summary: Home page of the Linguistic Analyzer API.

    A *loggerStart* variable is used here to keep track of home page instances in relation to logging.
    :func:`analyze_functions.declarelogger` is used to start a new instance of the log.

    :return: Home page
    :rtype: html

    """

    #flash('temp', category='message')
    #get_flashed_messages()

    #sets the NEW_DOC_FLAG to false as a default setting. NEW_DOC_FLAG indicates whether a regulatory document was dynamically
    #added to the app.

    common_functions.writeToConfig('NEW_DOC_FLAG', 'false')

    global loggerStart

    # Creating new log file every time the program starts.
    if loggerStart == 0:
        analyze_functions.declarelogger()
    if loggerStart > 10:
        analyze_functions.declarelogger()
        loggerStart = 0

    f = open(VIEWS + "index.html", "r")  # opens file with name of "index.html"
    loggerStart += 1

    return Response(f.read(), mimetype='text/html')


@application.route('/bubbletest')
def bubbletest():
    """
    Summary: Page for bubble chart testing.


    :return: Test page
    :rtype: html

     """

    # Creating new log file every time the program starts.
    if common_functions.homeCount() == 0:
        analyze_functions.declarelogger()

    f = open(VIEWS + "test.html", "r")  # opens file with name of "index.html"

    return Response(f.read(), mimetype='text/html')


@application.route('/reusablebubble')
def reusablebubble():
    """
    Summary: Page for bubble chart testing.


    :return: Test page
    :rtype: html

     """

    f = open(VIEWS + "reusable_bubble.html", "r")  # opens file with name of "reusable_bubble.html"

    return Response(f.read(), mimetype='text/html')


@application.route('/keywordbubblechart')
def keywordbubblechart():
    """
    Summary: Returns bubble chart html page.

    :return: bubble chart html page
    :rtype: html

    """

    f = open(VIEWS + "bubble_chart.html", "r")  # opens file with name of "reusable_bubble.html"

    return Response(f.read(), mimetype='text/html')


@application.route('/reusablebubble.js')
def reusablebubblejs():
    """
    Summary: Page for bubble chart testing.

    :return: Test page
    :rtype: html

    """

    f = open(VIEWS + "js/reusable_bubble.js", "r")  # opens file with name of "index.html"

    return Response(f.read(), mimetype='text/html')


@application.route('/index.js')
def indexjs():
    """
    Summary: Page for testing

    :return: Test page
    :rtype: html

    """

    # Creating new log file every time the program starts.
    if common_functions.homeCount() == 0:
        analyze_functions.declarelogger()

    f = open(VIEWS + "js/index.js", "r")  # opens file with name of "index.html"

    return Response(f.read(), mimetype='text/javascript')


@application.route('/project')
def project():
    """
    Summary: Returns an html page containing details about the Linguistic Analyzer project.


    :return: App summary
    :rtype: html

    """

    common_functions.writeToConfig('NEW_DOC_FLAG', 'false')

    f = open(VIEWS + "info.html", "r")  # opens file with name of "index.html"

    return Response(f.read().replace('#--DESCRIPTION_TITLE--#', 'Project Information').replace('#--DESCRIPTION--#',
                    "This Linguistic Analyzer lets the user upload a description document and compares that document \
                    against a regulatory document using Yule's k and Yule's i Algorithms, as well as a keyword scores algorithm.\
                    The results of the calculations are then displayed graphically to the user."), mimetype='text/html')


@application.route('/analyze', methods=['POST'])
def analyze():
    """
    Summary: Receives uploaded document and comparison document choice and executes various functions to compare them.

    - This functions starts by verifying that a valid file has been uploaded. Error handling also occurs here if no
      file has been selected.
    - Process User Document

        - All functions relating to the analysis of a user doc is handled by :func:`common_functions.interpretfile`.

    - Process Regulatory Document

        - All functions relating to the analysis of a reg doc is handled by :func:`common_functions.interpretexistingfile`.

    - Process Various Graph Displays

        - All functions related to processing graphical displays of the analyzed data is handled here.

            - :func:`common_functions.plotkeywordsalience`.
            - :func:`common_functions.plotkeywordscores`.
            - :func:`common_functions.plotkeywordfrequency`.
            - :func:`common_functions.generatebubblecsv`.

    An **Exception** will be raised if there is an error in the analysis process. An *"Unknown Error Has Occurred"* web
    page will be displayed.

    :return: Information regarding the uploaded document's similarity to regulatory document
    :rtype: html
    :raises: Exception

    """

    #bar = progressbar.Bar()

    # resetting document flag in case it was previously set when adding a new regulatory document to the list.
    common_functions.writeToConfig('NEW_DOC_FLAG', 'false')

    userdocwordcount = 0
    regdocwordcount = 0

    start_time = time.clock()
    regfilename = ''
    filename = ''
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
            filename = file.filename
            if request.headers.has_key('Test') and request.headers["Test"] == "True":
                localuploadfolder = 'unit_tests/test_pdfs/'

            if file.filename[-3:] == 'pdf' or file.filename[-4:] == 'docx':

                # The 'with' portion below is an example of concurrency in Python.
                # with Pool(5) as p:
                #     p = Process(target=common_functions.interpretfile, args=(file, localuploadfolder))
                #     p.start()
                #     p.join()

                [keyword_list, userdocwordcount] = common_functions.interpretfile(file, localuploadfolder)

                data = json.load((open('applicationconfig.json')))
                data['NUM_KWS'] = len(keyword_list.list)

                # --------------------------PROCESS REGULATORY DOCUMENT---------------------------- #
                reg_keyword_list = common_functions.interpretexistingfile(regfilename)

                data['NUM_REG_KWS'] = len(reg_keyword_list.list)
                with open('applicationconfig.json', 'w') as outfile:
                    json.dump(data, outfile)



                # ---------------------------KEYWORD PLOT FUNCTIONS------------------------------- #
                common_functions.plotkeywordsalience(keyword_list, reg_keyword_list, file.filename, regfilename)
                common_functions.plotkeywordscores(keyword_list, reg_keyword_list, file.filename, regfilename)
                common_functions.plotkeywordfrequency(keyword_list, reg_keyword_list, file.filename, regfilename)
                common_functions.generatebubblecsv(keyword_list, reg_keyword_list)

            else:
                logging.info('Invalid File type ' + file.filename[-4:] + '. Responding with error page')
                returnhtml = common_functions.geterrorpage('Invalid file type ' +file.filename[-4:] + '. Please only use .pdf')
                return Response(returnhtml, mimetype='text/html')

            end_time = time.clock()

            common_functions.printanalytics(filename, regfilename, keyword_list, reg_keyword_list, end_time-start_time)
            returnhtml = common_functions.getscorepage(keyword_list, reg_keyword_list, userdocwordcount, filename, regfilename)

    except Exception as e:
        returnhtml = common_functions.geterrorpage('An unknown error has occurred')

    try:
        return Response(returnhtml, mimetype='text/html')
    except Exception as e:
        SystemError(e)


@application.route('/backgroundimg', methods=['GET'])
def getbackgroundimg():
    """
    Summary: Returns *png* image of file.

    :return: graph
    :rtype: png

    """

    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='jpg')
    pilImage = open('views/img/background.png', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=False, attachment_filename='keyword.png')


@application.route('/keywordsalienceimage', methods=['GET'])
def getkwsalienceimage():
    """
    Summary: Returns *png* image of a graph of top salience keywords.

    :return: graph
    :rtype: png

    """

    return_html = ''

    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='jpg')
    pilImage = open('downloads/topsalience.png', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=False, attachment_filename='keyword.png')


@application.route('/backgroundwordsimg', methods=['GET'])
def getbackgroundwordsimg():
    """
    Summary: Returns *png* image of a graph of words background.

    :return: graph
    :rtype: png

    """

    return_html = ''

    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='jpg')
    pilImage = open('views/img/words_background_1.jpg', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=False, attachment_filename='keyword.png')


@application.route('/keywordscoresimage', methods=['GET'])
def getkwscoresimage():
    """
    Summary: Returns *png* image of a graph of keyword scores.

    :return: graph
    :rtype: png

    """

    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='jpg')
    pilImage = open('downloads/topkeywordscores.png', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=False, attachment_filename='keyword.png')


@application.route('/keywordfrequencyimage', methods=['GET'])
def getkwfreeqimage():
    """
    Summary: Returns *png* image of a keyword frequency graph.

    :return: graph
    :rtype: png

    """

    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='jpg')
    pilImage = open('downloads/topkeywordfrequency.png', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=False, attachment_filename='keyword.png')

@application.route('/linguistic_analyzer_log', methods=['GET'])
def getlinguisticanalyzerlog():
    """
    Summary: Returns "LinguisticAnalyzer.log".

    :return: log file
    :rtype: log

    """

    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='log')
    pilImage = open('logging/Linguistic_Analyzer.log', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=False, attachment_filename='Linguistic_Analyzer.log')


@application.route('/user_doc_kws', methods=['GET'])
def getuserdockws():
    """
    Summary: Returns "Keywords.txt" which contains information regarding a user's document keywords.

    :return: keyword file
    :rtype: txt

    """

    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='log')
    pilImage = open('Documents/Keywords.txt', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=False, attachment_filename='UserDocKeywords.txt')


@application.route('/reg_doc_kws', methods=['GET'])
def getregdockws():
    """
    Summary: Returns "Reg_Keywords.txt" which contains information regarding a regulatory document's keywords.

    :return: regulatory doc keyword file
    :rtype: txt

    """

    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='log')
    pilImage = open('Documents/Reg_Keywords.txt', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=False, attachment_filename='RegDocKeywords.txt')


@application.route('/testkeywords', methods=['GET'])
def gettestkeywords():
    """
    Summary: Returns "test_keywords.csv" which contains keywords for bubble chart information.

    :return: test_keywords doc keyword file
    :rtype: csv

    """

    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='log')
    pilImage = open('Documents/test_keywords.csv', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=False, attachment_filename='test_keywords.csv')


@application.route('/csvkeywords', methods=['GET'])
def getcsvkeywords():
    """
    Summary: Returns "csvkeywords.csv" which contains keywords for bubble chart information.

    :return: csvkeywords keyword file
    :rtype: csv

    """

    tempFileObj = NamedTemporaryFile(mode='w+b', suffix='log')
    pilImage = open('Documents/csvkeywords.csv', 'rb')
    copyfileobj(pilImage, tempFileObj)
    pilImage.close()
    tempFileObj.seek(0, 0)

    return send_file(tempFileObj, as_attachment=False, attachment_filename='csvkeywords.csv')


@application.route('/yulesinfo', methods=['GET'])
def yulesinfo():
    """
    Summary: Returns an html page regarding Yule's Info.

    :return: Page that describes Yule's K and Yule's I algorithms
    :rtype: html

    """

    f = open("views/info.html", "r")  # opens file with name of "index.html"

    return Response(f.read().replace('#--DESCRIPTION_TITLE--#', "Yule's k and Yule's i algorithms")\
        .replace('#--DESCRIPTION--#', "\"Yule's k\" and \"Yule's i\" are calculated values that represent the \
        semantic richness of a given text. We utilize this algorithm because semantic richness is one benchmark by \
        which technical writers can measure the effectiveness of what they have written. The score is largely useful as\
        a way to compare an uploaded document's significance against the significance of a regulatory text."),
                    mimetype='text/html')


@application.route('/comparisoninfo', methods=['GET'])
def comparisoninfo():
    """
    Summary: Returns an html page regarding comparison score information.

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


@application.route('/applicationconfig', methods=['GET'])
def getapplicationconfig():
    """
    Summary: Returns a json application config file.

    :return: */applicationconfig.json*
    :rtype: json

    """

    f = open('applicationconfig.json')
    returntext = f.read()
    f.close()

    return Response(returntext, mimetype='application/json')


@application.route('/newregdoc', methods=['POST'])
def newregdoc():
    """
    Summary: Dynamically adds a new regulatory document to the app.

    - A new regulatory document is saved into the app via :func:`common_functions.savefile`.
    - */views/index.html* is edited to include a reference to the new regulatory document so it can be selected by user.
    - Home page is reloaded with newly added document reference.

    :return: updated */views/index.html* page
    :rtype: html

    """

    common_functions.writeToConfig('NEW_DOC_FLAG', 'true')

    if 'datafile' not in request.files or request.files['datafile'].filename == "":
        logging.warning('Cannot find "datafile" in request object')
        returnhtml = common_functions.geterrorpage('No new file selected')
        return Response(returnhtml, mimetype='text/html')

    file = request.files['datafile']

    regfilename = file.filename

    # ----------- saving new regulatory file -------------#
    f = open('RegulatoryDocuments/' + regfilename, 'w')
    common_functions.savefile(file, 'RegulatoryDocuments/')

    f.close()

    # ----------- putting new regulatory file in list on home page -------------#
    fhtml = open('views/index.html')
    text = fhtml.read()
    newhtml = text.replace('<option class="reg doc options" value="Select">Select</option>',
                           '<option class="reg doc options" value="Select">Select</option>\n\t\t\t\t\t\t<option value=' + '"' + regfilename + '"' + '>' + regfilename[:-4] + '</option>')
    fhtml.close()
    newindexhtml = open('views/index.html', 'w')
    newindexhtml.write(newhtml)
    newindexhtml.close()

    return Response(newhtml, mimetype='text/html')


@application.route('/documentationredirect', methods=['GET'])
def getdocumentationhome():
    """
    Summary: Returns redirect page where app documentation is referenced.

    :return: html text
    :rtype: str

    """
    # f = open('file:///', 'r')
    # # f = open('Documentation/_build/html/index.html', 'r')
    # html = f.read()
    # f.close()

    #return Response(html, mimetype='text/html')
    return redirect('https://tlblanton.github.io/LinguisticAnalyzer/', code=302)



if __name__ == '__main__':
    application.run()
