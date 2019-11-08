import os
import pathlib
import re
import shutil

from PIL import Image, ImageFilter
from flask import current_app as app
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename


class UploadStore:
    def __init__(self, indexer):
        self.indexer = indexer
        self.preview_file_name = "preview.png"
        self.attachment_file_name = "attachment"

    @staticmethod
    def _get_file_extension(filename):
        """
        Gets file extension string
        :param filename: full filename to extract extension from
        :return: file extension as string
        """
        return re.findall('\.\w+$', filename)[0]

    @staticmethod
    def _get_preview_directory_path(upload_id):
        """
        Gets static filepath for preview image using upload_id
        :param upload_id: ID of upload to create path for
        :return: string containing path
        """
        return os.path.join('static', 'previews', upload_id)

    @staticmethod
    def _get_attachment_directory_path(upload_id):
        """
        Get non-static filepath for PDF document using upload_id
        :param upload_id: ID of upload to create path for
        :return: string containing path
        """
        return os.path.join('doc_data', upload_id)

    @staticmethod
    def _create_filepath(directory_path, filename):
        """
        Create filepath at directory, return filepath + revised filename.
        :param directory_path: full path to directory to create, and to make final filepath
        :param filename: name of file to add to directory
        :return: string containing new filepath
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return os.path.join(directory_path, filename)

    def _get_pdf_for(self, upload_id):
        """
        Gets path to PDF file associated with provided upload_id
        :param upload_id: ID of uploaded PDF
        :return: string containing full path to PDF
        """
        return os.path.join(self._get_attachment_directory_path(upload_id),
                            "{}.pdf".format(self.attachment_file_name))

    def _create_attachment_filepath(self, directory_path, filename):
        """
        Create filepath for attachment at directory, return filepath + revised filename.
        :param directory_path: full path to directory to create, and to make final filepath
        :param filename: name of file to add to directory
        :return: string containing new filepath
        """
        filename = secure_filename(filename)
        ext = self._get_file_extension(filename)
        new_filename = "{}{}".format(self.attachment_file_name, ext)
        return self._create_filepath(directory_path, new_filename)

    def add_file_to_listing(self, file, upload_id):
        """
        Save PDF file for listing with upload_id.
        :param file: flask file object to add
        :param upload_id: ID of upload
        :return: tuple containing list of filepaths and number of pages in PDF
        """
        filepaths = []
        pdf_path = self._create_attachment_filepath(self._get_attachment_directory_path(upload_id), file.filename)
        app.logger.debug("Saving file: {}".format(pdf_path))
        file.save(pdf_path)
        filepaths += [pdf_path]
        preview_path, numPages = self._add_preview(upload_id, pdf_path)
        if preview_path is not None:
            filepaths += [preview_path]

        # return path to PDF and path to preview
        return filepaths, numPages

    def get_preview_from_listing(self, upload_id):
        """
        Return filepath to preview image for listing with upload_id.
        :param upload_id: ID of upload to look for
        :return:
        """
        raw_path = os.path.join(self._get_preview_directory_path(upload_id),
                                self.preview_file_name)

        # must crop '/static/' from path because jinja needs paths relative to static root foler
        return "/" + str(pathlib.Path(*pathlib.Path(raw_path).parts[1:]))

    def _add_preview(self, upload_id, pdf_path):
        """
        Creates PNG preview of first page of PDF file. Also counts number of pages in PDF.
        :param upload_id: ID of upload to add preview to
        :param pdf_path: path of PDF file
        :return: path to preview file and number of pages in PDF
        """
        imgs = convert_from_path(pdf_path)
        numPages = len(imgs)
        if numPages == 0:
            app.logger.error("No images could be extracted from file")
            return None
        filepath = self._create_filepath(self._get_preview_directory_path(upload_id),
                                         self.preview_file_name)
        app.logger.debug("Saving file: {}".format(filepath))
        imgs[0].save(filepath)
        self._partial_blur_image(filepath)
        return filepath, numPages

    @staticmethod
    def _partial_blur_image(filepath):
        """
        Blurs part of image.
        :param filepath: path to file that will be blurred
        """
        preview_image = Image.open(filepath)
        width, height = preview_image.size
        preview_image = preview_image.crop((0, 0, width, round(height / 2)))
        blurred_image = Image.open(filepath).filter(ImageFilter.GaussianBlur(12))
        blurred_image.paste(preview_image, (0, 0))
        blurred_image.save(filepath)
        app.logger.debug("Blurred image {}".format(filepath))

    def promote_uploads(self, request_upload_id, listing_upload_id):
        """
        Move files from directory associated with old_upload_id (request)
        to directory associated with new_upload_id (listing). This is used when a request
        is approved so a request becomes a listing which is associated with a new ID.

        Indexing also occurs here to facilitate searching PDFs.
        :param request_upload_id: upload ID of request
        :param listing_upload_id: upload ID of listing
        :return:
        """
        # move preview image to new directory
        src_preview_path = self._get_preview_directory_path(request_upload_id)
        dest_preview_path = self._get_preview_directory_path(listing_upload_id)
        shutil.move(src_preview_path, dest_preview_path)

        # move file attachment to new directory
        src_doc_path = self._get_attachment_directory_path(request_upload_id)
        dest_doc_path = self._get_attachment_directory_path(listing_upload_id)
        shutil.move(src_doc_path, dest_doc_path)

        # index file attachment
        self.indexer.index_pdf(self._get_pdf_for(listing_upload_id),
                               listing_upload_id)

        return [dest_preview_path, dest_doc_path]
