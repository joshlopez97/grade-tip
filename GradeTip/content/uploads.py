import re
import os

from PIL import Image, ImageFilter
from flask import current_app as app
from pdf2image import convert_from_bytes, convert_from_path
from werkzeug.utils import secure_filename


def get_file_extension(filename):
    return re.findall('\.\w+$', filename)[0]


def create_file_path(listing_id, filename, i=0):
    """ Create filepath using listing_id. """
    filename = secure_filename(filename)
    ext = get_file_extension(filename)
    new_filename = "{0:0>2}".format(i) + ext
    directory = os.path.join('static', 'doc_data', listing_id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(directory, new_filename)


def add_file_to_listing(file, listing_id):
    """ Save PDF file for listing with listing_id. """
    filepaths = []
    pdf_path = create_file_path(listing_id, file.filename)
    app.logger.debug("Saving file: {}".format(pdf_path))
    file.save(pdf_path)
    filepaths += [pdf_path]
    preview_path = add_preview(file, listing_id, pdf_path)
    if preview_path is not None:
        filepaths += [preview_path]

    # return path to PDF and path to preview
    return filepaths


def add_preview(file, listing_id, pdf_path):
    """ Creates PNG preview of first page of PDF file. """
    print(file)
    imgs = convert_from_path(pdf_path)
    if len(imgs) == 0:
        app.logger.error("No images could be extracted from file")
        return None
    filepath = create_file_path(listing_id, "preview.png")
    app.logger.debug("Saving file: {}".format(filepath))
    imgs[0].save(filepath)
    partial_blur_image(filepath)
    return filepath


def partial_blur_image(filepath):
    preview_image = Image.open(filepath)
    width, height = preview_image.size
    preview_image = preview_image.crop((0, round(height / 2), width, height))
    print(width, height)
    blurred_image = Image.open(filepath).filter(ImageFilter.GaussianBlur(12))
    blurred_image.paste(preview_image, (0, round(height / 2)))
    blurred_image.save(filepath)
    app.logger.debug("Blurred image {}".format(filepath))


def move_files_to_listing(old_listing_id, new_listing_id):
    """ Move files from directory associated with old_listing_id
        to directory associated with new_listing_id.
    """
    pass
