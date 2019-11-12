import json
import re
from collections import defaultdict

from GradeTip.content.identifier import IDGenerator
from GradeTip.indexer.frequency import FrequencyStore
from GradeTip.indexer.pdf_reader import PDFReader
from nltk import PorterStemmer


class Indexer:
    def __init__(self, redis_manager):
        self.pdf_reader = PDFReader()
        self.ps = PorterStemmer()
        self.id_generator = IDGenerator()
        self.freq_store = FrequencyStore(redis_manager)

    def index_pdf(self, pdf_path, upload_id):
        content_list = self.pdf_reader.read(pdf_path)
        self.freq_store.increment_doc_count()
        for page_num, page_content in enumerate(content_list):
            self.index_content(page_content, upload_id, page_num)

    def index_content(self, text_content, upload_id, page=None):
        term_freqs = defaultdict(dict)
        parsed = re.findall(r'[A-Za-z0-9]+', text_content)
        term_count = 0
        for word in parsed:
            # stem each term and convert to lowercase
            term = self.ps.stem(word.lower())

            # set term frequency to 0, if not set yet
            term_freqs[term].setdefault('freq', 0)

            # increment term frequency
            term_freqs[term]['freq'] += 1

            # store position of current term in document
            term_freqs[term].setdefault('pos', []).append(term_count)
            term_count += 1

        for term, term_info in term_freqs.items():
            if page is not None:
                term_info['pg'] = page
            self.freq_store.set_tf(term, upload_id, json.dumps(term_info))
            self.freq_store.increment_df(term)
