from unittest import TestCase
import Keyword
import KeywordList
from unittest import TestCase
from unittest import TestCase
from functionsv1 import common_functions
from werkzeug import datastructures
from functionsv1 import common_functions
import logging
from functionsv1 import analyze_functions
import os


# Right click the 'test_pdfs' folder in the explorer, select 'copy path' and paste that value here
DOWNLOADS_FOLDER = '/Users/tlblanton/Documents/UC_Denver/2017_fall/senior_design/linguistic_analyzer/11_7_17\
/LinguisticAnalyzer/unit_tests/test_pdfs/'

# Right click the 'Keywords.txt' file in the explorer, select 'copy path' and paste that value here
OUTPUT_KW_PATH = '/Users/tlblanton/Documents/UC_Denver/2017_fall/senior_design/linguistic_analyzer/11_7_17\
/LinguisticAnalyzer/Documents/Keywords.txt'


class TestOutputkeywordtotext(TestCase):
    def test_outputkeywordtotext(self):
        file = ''
        testFileName = 'test_dfwpdftext.pdf'        # Name os test file
        try:
            # opening test file
            file = datastructures.FileStorage(filename=testFileName,
                                              content_type="application/pdf", name='datafile')
            if file.filename is None:
                self.fail("File could not be opened")

            # Grabbing text from pdf file
            if file.filename[-3:] == 'pdf':
                file_text = common_functions.extractpdftext(file, DOWNLOADS_FOLDER)
            elif file.filename[-4:] == 'docx':
                file_text = common_functions.extractmicrosoftdocxtext(file)

            # identifying keywords of pdf file
            keyword_list = analyze_functions.identifykeywords(file_text)

            # outputting keyword information to file 'Keywords.txt'
            common_functions.outputkeywordtotext(keyword_list, OUTPUT_KW_PATH)

            word_list = []

            # populating word_list with words from 'Keywords.txt'
            with open(OUTPUT_KW_PATH, 'r') as f:
                for line in f:
                    word_list.append(line.split(',')[0])
            f.close()

            kw_string_list = []
            for word in keyword_list.list:
                kw_string_list.append(word.word)

            # Asserting that the words we epected to be inserted into
            assert set(kw_string_list) == set(word_list)

        except Exception as e:
            logging.info("Test Failed")
            self.fail('unable to output keyword list to file.')
        finally:
            file.close()

