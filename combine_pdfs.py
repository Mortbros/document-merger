import os
import shutil
import subprocess
import re
import sys

from pdf2docx import Converter
import mammoth

import base64
from PIL import Image
import pytesseract
from io import BytesIO

import json

from config import Config
import logging

import time

# prerequisites:
# Tesseract at "C:\\Program files\\Tesseract-OCR\\tesseract.exe"
# pip install all modules of file

# TODO: keep track of all the files that have been created and delete them if the program exits prematurely
# TODO: make this consistent, log errors instead of breaking
# TODO: add flag to preview images as the program runs so the user can remove unneccecary images
# TODO: hash image base64 strings

start_time = time.time()

global created_files
created_files = []


def pdf_to_docx(pdf_in_path, docx_out_path):
    cv = Converter(pdf_in_path)
    cv.convert(docx_out_path)
    cv.close()
    created_files.append(docx_out_path)
    # os.system(f"pdf2docx convert \"{pdf_in_path}\" \"{docx_out_path}\"")


def docx_to_html(docx_in_path, html_out_path):
    with open(html_out_path, "w", encoding="utf-8") as o_f:
        with open(docx_in_path, "rb") as f:
            o_f.write(mammoth.convert_to_html(f).value)
    created_files.append(html_out_path)


# maybe turn this into an object instead of passing around
def base64_ocr(b64_string, ocr_map, filename=None):
    if b64_string in ocr_map:
        print(f"\t\tText already extracted: '{ocr_map[b64_string]}'")
        return ocr_map[b64_string], ocr_map
    # pad end of base64 string with "=" to fill up to length divisible by 4
    missing_padding = len(b64_string) % 4
    if missing_padding:
        b64_string += "=" * (4 - missing_padding)

    # convert base64 to bytes
    img_bytes = base64.b64decode(b64_string)

    # convert bytes to a PIL image object
    img = Image.open(BytesIO(img_bytes))

    if filename:
        img.save(filename)
        created_files.append(filename)

    w, h = img.size
    if w * h >= 2000 and h > 20 and w > 20:
        ocr_text = pytesseract.image_to_string(img)
        print(f"\t\tFound text in image {img.size}: '{ocr_text.replace('\n', ' ')}'")
    else:
        ocr_text = ""
        print(f"\t\tSkipping image: {w}, {h}")

    ocr_map[b64_string] = ocr_text
    return ocr_text, ocr_map


def pdf_to_html_ocr(pdf_in_path, html_out_path, ocr_map):
    print("\tTo HTML: ", html_out_path)
    if not check_if_file_already_processed(pdf_in_path):
        docx_in_out_path = change_ext(html_out_path, "docx")

        pdf_to_docx(pdf_in_path, docx_in_out_path)
        docx_to_html(docx_in_out_path, html_out_path)
        os.remove(docx_in_out_path)

        base64_image_regex = r"\".*?base64,([^\"]*)\"[^>]*>"

        with open(html_out_path, "r", encoding="utf-8") as f:
            html_text = f.read()

        base64_images = re.findall(base64_image_regex, html_text)
        # if duplicate images, set the end index of the b64 to be the end index of the nth match
        # base64_image_end_indexes = [html_text.find(b64img) + len(b64img) - 1 for bg64img in base64_images]

        # base64_image_end_indexes = [[m.end(0) for m in re.finditer(b64, html_text)][list(base64_images).index(b64, list(base64_images).index(b64))] for b64 in base64_images]

        # base64_image_end_indexes = [html_text.find(b64img) + len(b64img) - 1 for b64img in base64_images]

        # base64_image_end_indexes = [
        #     m.end(0) for m in re.finditer(base64_image_regex, html_text)
        # ]

        if len(base64_images) > 0:
            base64_image_end_indexes = list(
                m.end(0) for m in re.finditer(base64_image_regex, html_text)
            )
            base64_image_end_indexes.reverse()

            for i, base64_img in enumerate(base64_images):
                # add ocr text of the image after the image tag
                ocr_text, ocr_map = base64_ocr(base64_img, ocr_map)
                if ocr_text:
                    start_ocr = html_text[
                        max(
                            base64_image_end_indexes[i] - 10, 0
                        ) : base64_image_end_indexes[i]
                    ]
                    end_ocr = html_text[
                        base64_image_end_indexes[i] : min(
                            base64_image_end_indexes[i] + 10, len(html_text) - 1
                        )
                    ]
                    print(
                        f"\t\tInserting OCR text in position: ...{start_ocr}(OCR TEXT HERE){end_ocr}..."
                    )
                    html_text = (
                        html_text[: base64_image_end_indexes[i]]
                        + " OCR text: '"
                        + ocr_text
                        + "'"
                        + html_text[base64_image_end_indexes[i] :]
                    )

        with open(html_out_path, "w", encoding="utf-8") as f:
            f.write(html_text)
    else:
        print("\t\tFile already processed, skipping")

    map_processed_file(pdf_in_path, html_out_path)
    return ocr_map
    # cleaned_up = False
    # while not cleaned_up:
    #     try:
    #         if os.path.exists(docx_in_out_path):
    #             os.remove(docx_in_out_path)
    #         cleaned_up = True
    #     except PermissionError:
    #         print(f"PermissionError on file {docx_in_out_path}")
    #         pass


def merge_html_files(output_dir_path, output_file_path):
    # get all HTML files in the output directory
    html_files = [
        os.path.join(output_dir_path, f)
        for f in os.listdir(output_dir_path)
        if f.endswith(".html")
    ]

    # empty out HTML file before writing to prevent it storing multiple outputs
    with open(output_file_path, "w", encoding="utf-8") as out_f:
        out_f.write("")

    # iterate over all html files and append to merged html file
    with open(output_file_path, "a+", encoding="utf-8") as out_f:
        for html_file in html_files:
            with open(html_file, "r", encoding="utf-8") as f:
                out_f.write(f.read())
        created_files.append(output_dir_path)
        # os.remove(html_file)
    # # Create a new HTML file to merge all HTML files
    # with open(output_file, 'w', encoding='utf-8') as merged_file:
    #     for html_file in html_files:
    #         with open(os.path.join(output_dir, html_file), 'r', encoding='utf-8') as f:
    #             merged_file.write(f.read())


def get_pdf_paths(directory):
    paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".pdf"):
                paths.append(os.path.join(root, file))
                # output_dir = "TEMPCOMBINE" + os.path.splitext(pdf_file)[0] + "_html"
    return paths


def change_ext(file, new_extension):
    return f"{file[0:file.rfind('.')]}.{new_extension.replace('.', '')}"


def map_processed_file(in_filepath, out_filepath):
    with open(config.file_path_map_path, "r+") as f:
        path_map = json.loads(f.read())
        path_map[in_filepath] = out_filepath
        f.seek(0)
        f.write(json.dumps(path_map))
        f.truncate()
        f.close()


def check_if_file_already_processed(filepath):
    if os.path.exists(config.file_path_map_path):
        f = open(config.file_path_map_path, "r+")
        path_map = json.loads(f.read())
        return filepath in path_map
    else:
        with open(config.file_path_map_path, "w", encoding="utf-8") as f:
            _ = {}
            f.write(json.dumps(_))


def main():
    if not os.path.exists(config.ocr_map_path):
        with open(config.ocr_map_path, "w") as f:
            _ = {}
            f.write(json.dumps(_))

    with open(config.ocr_map_path, "r") as f:
        ocr_map = json.load(f)

    # iterate over directories
    for dir_name in os.listdir("."):
        if os.path.isdir(dir_name):
            if dir_name not in config.ignored_dirs:
                # get all pdf files in directory
                print(f"Parsing directory: {dir_name}")
                for pdf in get_pdf_paths(dir_name):
                    print(f"\tConverting PDF: {pdf}")
                    ocr_map = pdf_to_html_ocr(
                        pdf,
                        os.path.join(
                            config.temp_file_path,
                            change_ext(pdf, "html").split("\\")[-1],
                        ),
                        ocr_map,
                    )
                # merge HTML files in the temp directory into a single HTML file in the course directory
                merge_html_files(
                    config.temp_file_path, os.path.join(dir_name, f"{dir_name}.html")
                )

    with open(config.ocr_map_path, "w") as f:
        f.write(json.dumps(ocr_map))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.ERROR)

    config = Config()
    pytesseract.pytesseract.tesseract_cmd = config.tesseract_path

    # change directory to directory of python file instead of where it is ran from
    os.chdir(config.analysis_path)

    if not os.path.exists(config.temp_file_path):
        os.mkdir(config.temp_file_path)
        created_files.append(config.temp_file_path)

    main()
    # try:
    # except:
    #     shutil.rmtree(config.temp_file_path)

    # temp_img_path = os.path.join(os.getcwd(), config.temp_file_path, "temp.png")
    # base64_ocr(b64_string, temp_img_path)
    # print(pytesseract.image_to_string(temp_img_path))

    print(f"Finished in {round(time.time() - start_time, 2)} seconds")
