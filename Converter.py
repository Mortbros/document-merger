from Config import Config

import os
import time
import re
import json

import comtypes.client

from pdf2docx import Converter as pdf2docx_Converter
import mammoth

import base64
from PIL import Image
import pytesseract
from io import BytesIO


# TODO: keep track of all the files that have been created and delete them if the program exits prematurely
# TODO: make this consistent, log errors instead of breaking
# TODO: add flag to preview images as the program runs so the user can remove unnecessary images


class Converter:
    def __init__(self):
        self.created_files = []
        self.supported_input_types = ["pdf", "html", "pptx", "docx"]
        self.supported_output_types = ["pdf", "html"]
        self.config = Config()

        with open(self.config.ocr_map_path, "r") as f:
            self.ocr_map = json.load(f)

        pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_path

    def convert(self, input_file_path, output_file_path, ocr=True):
        # convert input and output to absolute paths if not already
        input_file_path, output_file_path = os.path.abspath(
            input_file_path
        ), os.path.abspath(output_file_path)

        input_type = input_file_path.split(".")[-1]
        output_type = output_file_path.split(".")[-1]

        if input_type not in self.supported_input_types:
            print(
                f"Unsupported input file type '{input_type}' (supported types are {', '.join(self.supported_input_types)})"
            )
            return False
        elif output_type not in self.supported_output_types:
            print(
                f"Unsupported output file type '{output_type}' (supported types are {', '.join(self.supported_input_types)})"
            )
            return False

        if not self.check_if_file_already_processed(input_file_path):
            if input_type == "pdf" and output_type == "html":
                self.PDF_to_HTML(input_file_path, output_file_path, ocr)
            elif input_type == "pdf" and output_type == "docx":
                self.PDF_to_DOCX(input_file_path, output_file_path)
            elif input_type == "docx" and output_type == "html":
                self.DOCX_to_HTML(input_file_path, output_file_path)
            elif input_type == "pptx" and output_type == "html":
                self.PPTX_to_PDF(input_file_path, output_file_path)
        else:
            print("\t\tFile already processed, skipping")

        with open(self.config.ocr_map_path, "w") as f:
            f.write(json.dumps(self.ocr_map, indent=4))

    # def PDF_to_HTML(self, input_file_path, output_file_path):
    #     os.system(
    #         f'{self.config.pdftohtml_path} -nofonts "{input_file_path}" "{os.path.join(self.config.temp_file_path, output_file_path)}"'
    #     )
    #     return True

    def PDF_to_DOCX(self, input_file_path, output_file_path):
        input_file_path = self.change_ext(input_file_path, "pdf")
        output_file_path = self.change_ext(output_file_path, "docx")

        cv = pdf2docx_Converter(input_file_path)
        cv.convert(output_file_path)
        cv.close()
        self.created_files.append(output_file_path)
        # os.system(f"pdf2docx convert \"{pdf_in_path}\" \"{docx_out_path}\"")

    def DOCX_to_HTML(self, input_file_path, output_file_path):
        input_file_path = self.change_ext(input_file_path, "pdf")
        output_file_path = self.change_ext(output_file_path, "docx")

        with open(input_file_path, "w", encoding="utf-8") as o_f:
            with open(output_file_path, "rb") as f:
                o_f.write(mammoth.convert_to_html(f).value)
        self.created_files.append(output_file_path)

    def PPTX_to_PDF(self, input_file_path, output_file_path, formatType=32):
        input_file_path = self.change_ext(input_file_path, "pptx")
        output_file_path = self.change_ext(output_file_path, "pdf")

        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        powerpoint.Visible = 1

        deck = powerpoint.Presentations.Open(input_file_path)
        deck.SaveAs(output_file_path, formatType)  # formatType = 32 for ppt to pdf
        deck.Close()
        powerpoint.Quit()
        return True

    def PDF_to_HTML(self, input_file_path, output_file_path, ocr=True):
        input_file_path = self.change_ext(input_file_path, "pdf")
        output_file_path = self.change_ext(output_file_path, "html")

        docx_intermediatary_path = self.change_ext(output_file_path, "docx")

        self.PDF_to_DOCX(input_file_path, docx_intermediatary_path)
        self.DOCX_to_HTML(docx_intermediatary_path, output_file_path)
        os.remove(docx_intermediatary_path)

        with open(output_file_path, "r", encoding="utf-8") as f:
            html_text = f.read()

        base64_image_regex = r"\".*?base64,([^\"]*)\"[^>]*>"

        base64_images = re.findall(base64_image_regex, html_text)

        if len(base64_images) > 0:
            base64_image_end_indexes = list(
                m.end(0) for m in re.finditer(base64_image_regex, html_text)
            )
            base64_image_end_indexes.reverse()

            for i, base64_img in enumerate(base64_images):
                # add ocr text of the image after the image tag
                ocr_text = self.base64_ocr(base64_img)
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

        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(html_text)

        self.map_processed_file(input_file_path, output_file_path)

    def base64_ocr(self, b64_string, filename=None):
        # pad end of base64 string with "=" to fill up to length divisible by 4
        if missing_padding := len(b64_string) % 4:
            b64_string += "=" * (4 - missing_padding)

        # if already parsed, return existing value
        hashed_b64_string = hash(b64_string)
        if hashed_b64_string in self.ocr_map:
            print(f"\t\tText already extracted: '{self.ocr_map[hashed_b64_string]}'")
            return self.ocr_map[hashed_b64_string]

        # convert base64 to bytes
        img_bytes = base64.b64decode(b64_string)

        # convert bytes to a PIL image object
        img = Image.open(BytesIO(img_bytes))

        if filename:
            img.save(filename)
            self.created_files.append(filename)

        w, h = img.size
        if w * h >= 2000 and h > 20 and w > 20:
            ocr_text = pytesseract.image_to_string(img)
            print(
                f"\t\tFound text in image {img.size}: '{ocr_text.replace('\n', ' ')}'"
            )
        else:
            ocr_text = ""
            print(f"\t\tSkipping image: {w}, {h}")

        self.ocr_map[hashed_b64_string] = ocr_text
        return ocr_text

    def change_ext(self, file, new_extension):
        return f"{file[0:file.rfind('.')]}.{new_extension.replace('.', '')}"

    def map_processed_file(self, in_filepath, out_filepath):
        with open(self.config.file_path_map_path, "r+") as f:
            path_map = json.loads(f.read())
            path_map[in_filepath] = out_filepath
            f.seek(0)
            f.write(json.dumps(path_map, indent=4))
            f.truncate()
            f.close()

    def check_if_file_already_processed(self, filepath):
        if os.path.exists(self.config.file_path_map_path):
            with open(self.config.file_path_map_path, "r+") as f:
                path_map = json.loads(f.read())
                return filepath in path_map
        else:
            with open(self.config.file_path_map_path, "w", encoding="utf-8") as f:
                _ = {}
                f.write(json.dumps(_))
