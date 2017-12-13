from unittest import TestCase
from werkzeug import datastructures
import requests


# DOWNLOADS_FOLDER = '/Users/tlblanton/Documents/UC_Denver/2017_fall/senior_design/linguistic_analyzer/11_7_17\
  #      /LinguisticAnalyzer/unit_tests/test_pdfs/'

DOWNLOADS_FOLDER = '/test_pdfs'

LOCAL_HOST = 'http://127.0.0.1:5000/'


# TODO: Move this to an integration test area and get it to work there. This is NOT a unit test.
class TestAnalyze(TestCase):
    def test_analyze(self):
        """
        Summary: Tests the Analyze() function
        
        """
        testFileName = 'test_extractpdftext.pdf'

        # opening test file
        file = datastructures.FileStorage(filename=testFileName,
                                          content_type="application/pdf", name=testFileName)
        if file.filename is None:
            self.fail("File could not be opened")

        reqFile = {'datafile': file}
        data = ''
        headers = {'Host': '127.0.0.1:5000', 'Content-Type': 'Multipart/form-data', 'Connection': 'keep-alive', "Test": "True"}
        response = requests.post(LOCAL_HOST + 'analyze', data=None, files=reqFile, cookies=None, auth=None)



        self.fail()
