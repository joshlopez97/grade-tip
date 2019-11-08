import io

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


class PDFReader:
    @staticmethod
    def read(filepath):
        """
        Reads PDF saved at filepath and returns list of strings containing text from each page of
        the PDF.
        :param filepath:
        :return:
        """
        pages = []
        with open(filepath, 'rb') as fp:
            resource_manager = PDFResourceManager()
            buffer = io.StringIO()
            device = TextConverter(resource_manager, buffer, laparams=LAParams())
            interpreter = PDFPageInterpreter(resource_manager, device)
            for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)
                data = buffer.getvalue()
                pages += [data]
        return pages
