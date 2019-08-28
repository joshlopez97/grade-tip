import pathlib
import re
import os
import shutil

from PIL import Image, ImageFilter
from flask import current_app as app
from pdf2image import convert_from_bytes, convert_from_path
from werkzeug.utils import secure_filename


def get_file_extension(filename):
    return re.findall('\.\w+$', filename)[0]


def get_static_filepath_for_preview(upload_id):
    return os.path.join('static', 'previews', upload_id)


def get_filepath_for_document(upload_id):
    return os.path.join('doc_data', upload_id)


def create_file_path(directory, filename, i=0):
    """ Create filepath at directory, return filepath + revised filename. """
    filename = secure_filename(filename)
    ext = get_file_extension(filename)
    new_filename = "{0:0>2}".format(i) + ext
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(directory, new_filename)


def add_file_to_listing(file, upload_id):
    """ Save PDF file for listing with upload_id. """
    filepaths = []
    pdf_path = create_file_path(get_filepath_for_document(upload_id), file.filename)
    app.logger.debug("Saving file: {}".format(pdf_path))
    file.save(pdf_path)
    filepaths += [pdf_path]
    preview_path = add_preview(upload_id, pdf_path)
    if preview_path is not None:
        filepaths += [preview_path]

    # return path to PDF and path to preview
    return filepaths


def get_preview_from_listing(upload_id):
    """ Return filepath to preview image for listing with upload_id. """
    raw_path = os.path.join(get_static_filepath_for_preview(upload_id), "00.png")

    # must crop '/static/' from path because jinja needs paths relative to static root foler
    return "/" + str(pathlib.Path(*pathlib.Path(raw_path).parts[1:]))


def add_preview(upload_id, pdf_path):
    """ Creates PNG preview of first page of PDF file. """
    imgs = convert_from_path(pdf_path)
    if len(imgs) == 0:
        app.logger.error("No images could be extracted from file")
        return None
    filepath = create_file_path(get_static_filepath_for_preview(upload_id), "preview.png")
    app.logger.debug("Saving file: {}".format(filepath))
    imgs[0].save(filepath)
    partial_blur_image(filepath)
    return filepath


def partial_blur_image(filepath):
    """ Blurs part of image. """
    preview_image = Image.open(filepath)
    width, height = preview_image.size
    preview_image = preview_image.crop((0, round(height / 2), width, height))
    blurred_image = Image.open(filepath).filter(ImageFilter.GaussianBlur(12))
    blurred_image.paste(preview_image, (0, round(height / 2)))
    blurred_image.save(filepath)
    app.logger.debug("Blurred image {}".format(filepath))


def migrate_filepaths(src_upload_id, dest_upload_id):
    move_files_to_listing(src_upload_id, dest_upload_id)


def move_files_to_listing(src_upload_id, dest_upload_id):
    """ Move files from directory associated with old_upload_id
        to directory associated with new_upload_id.
    """
    src_preview_path = get_static_filepath_for_preview(src_upload_id)
    dest_preview_path = get_static_filepath_for_preview(dest_upload_id)
    shutil.move(src_preview_path, dest_preview_path)

    src_doc_path = get_filepath_for_document(src_upload_id)
    dest_doc_path = get_filepath_for_document(dest_upload_id)
    shutil.move(src_doc_path, dest_doc_path)

    return [dest_preview_path, dest_doc_path]
