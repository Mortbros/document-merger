import os
import json

from Converter import Converter

from Config import Config
import logging

import time

# prerequisites:
# Tesseract at "C:\\Program files\\Tesseract-OCR\\tesseract.exe"
# pip install all modules of file


def get_pdf_paths(directory):
    paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".pdf"):
                paths.append(os.path.join(root, file))
    return paths


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
        # created_files.append(output_dir_path)


def main():
    converter = Converter()
    # iterate over directories
    for dir_name in os.listdir("."):
        if os.path.isdir(dir_name):
            if dir_name not in config.ignored_dirs:
                # get all pdf files in directory
                print(f"Parsing directory: {dir_name}")
                for pdf in get_pdf_paths(dir_name):
                    print(f"\tConverting PDF: {pdf}")
                    converter.PDF_to_HTML(
                        pdf,
                        os.path.join(config.temp_file_path, pdf.split("\\")[-1]),
                    )
                # merge HTML files in the temp directory into a single HTML file in the course directory
                merge_html_files(
                    config.temp_file_path, os.path.join(dir_name, f"{dir_name}.html")
                )


if __name__ == "__main__":
    start_time = time.time()
    logging.getLogger().setLevel(logging.ERROR)

    config = Config()

    # initialise files
    if not os.path.exists(config.ocr_map_path):
        with open(config.ocr_map_path, "w") as f:
            _ = {}
            f.write(json.dumps(_))

    if not os.path.exists(config.temp_file_path):
        os.mkdir(config.temp_file_path)
        # created_files.append(config.temp_file_path)

    # change directory to analysis path
    os.chdir(config.analysis_path)

    main()

    print(f"Finished in {round(time.time() - start_time, 2)} seconds")
