from .StatusTable import StatusTable

import os
import re
import json
import zlib  # adler32 hashing
import hashlib  # file_digest sha256 hashing
import shutil  # for copy

import comtypes.client

from pdf2docx import Converter as pdf2docx_Converter
import mammoth

import base64
from PIL import Image, ImageTk
import pytesseract
from io import BytesIO

import tkinter as tk
from tkinter import simpledialog

# TODO: keep track of all the files that have been created and optionally delete them if the program exits prematurely
# TODO: make this consistent, log errors instead of breaking
# TODO: more advanced OCR: https://huggingface.co/spaces/gokaygokay/Florence-2/blob/main/app.py
# TODO: https://github.com/aditeyabaral/convert2pdf/tree/master
# TODO: Fix base64 image OCR text appendation
# TODO: Add flag to produce imagesless HTML
# TODO: store hashes of all the processed files to prevent reprocessing of files at a global level
# TODO: move imageless html functionality into Converter, move flag
# TODO: multithreading:
#   given the batch of files
#   run each conversion on a thread
#       live update the line in the terminal, print to queue above when done
# TODO: combine all the code for the start and end of each conversion function into 2 functions
# TODO: add _ to the start of all conversion files to indicate that the proper procedure is not being followed if they are used standalone
# alternatively, just add proper prodedure to the start and end functions that is mentioned in the above todo
# TODO: there exists an issue where the file is skipped because it has already been processed, but the output from the previous process doesn't exist in the current folder. The reprocessing is skipped but the file is not added to the final output
# in this case we need to keep track of and manually inject the preprocessed output file(s) into the final HTML merging file


class Converter:
    def __init__(self, config):
        self.config = config
        self.created_files = []
        self.supported_input_types = ["pdf", "html", "pptx", "docx"]
        self.supported_output_types = ["html"]
        self.status_table = StatusTable(print_output=self.config.print_status_table)

        self.ocr_map = {}
        self.file_path_map = {}
        self.processed_file_hashes = {}

        with open(self.config.cache_file_path, "r") as f:
            try:
                cache_data = json.load(f)

                self.ocr_map = cache_data["ocr_map"]
                self.file_path_map = cache_data["file_path_map"]
                self.processed_file_hashes = cache_data["processed_file_hashes"]

            except json.decoder.JSONDecodeError:
                # exited halfway through writing to the file, so just reset it to {}
                if len(f.read()) == 0:
                    with open(self.config.cache_file_path, "w") as f:
                        f.write("{}")
                    print(f"JSON decode error on cache JSON, file has been reset")
                else:
                    print(
                        f"JSON decode error on cache JSON, path {self.config.cache_file_path}"
                    )
                    exit()

        if self.config.show_image:
            self.tk_root = tk.Tk()
            self.tk_root.withdraw()
        pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_path

    def convert(
        self,
        input_file_path,
        output_file_path,
        output_type=None,
        ocr=True,
        make_output_dirs=False,
    ):
        # convert input and output to absolute paths if not already
        input_file_path = self.prepare_path(input_file_path)
        output_file_path = self.prepare_path(
            output_file_path, new_extension=output_type, make_dirs=True
        )

        input_type = input_file_path.split(".")[-1]
        output_type = (
            output_file_path.split(".")[-1] if not output_type else output_type
        )

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

        # If file content has been processed in a different folder, return the path to that file
        file_processed_path = self.check_if_file_already_processed(input_file_path)
        if not file_processed_path:
            # if the input and output types are the same, just copy the file into the temp directory
            # notably, we don't run any OCR or internal file processing in this case
            # the OCR may need to be rectified specifically for html to html
            if input_type == output_type:
                shutil.copy2(input_file_path, output_file_path)
            elif input_type == "pdf" and output_type == "html":
                self.PDF_to_HTML(
                    input_file_path, output_file_path, ocr, make_output_dirs
                )
            elif input_type == "pdf" and output_type == "docx":
                self.PDF_to_DOCX(input_file_path, output_file_path, make_output_dirs)
            elif input_type == "docx" and output_type == "html":
                self.DOCX_to_HTML(input_file_path, output_file_path, make_output_dirs)
            elif input_type == "pptx" and output_type == "html":
                self.PPTX_to_HTML(input_file_path, output_file_path, make_output_dirs)
            else:
                print(f"Invalid conversion type pair {input_type} and {output_type}")
                output_file_path = None
        else:
            self.status_table.update_statuses(
                {
                    "AP?": "✅",
                    "File Name": input_file_path.split("\\")[-1],
                },
                reset_to={"AP?": "❌", "File Name": ""},
            )
            output_file_path = file_processed_path

        return output_file_path

    def PDF_to_DOCX(self, input_file_path, output_file_path, make_output_dirs=False):
        self.status_table.update_statuses(
            {
                "File Name": input_file_path.split("\\")[-1],
                "Input": "pdf",
                "Output": "docx",
                "Status": "Converting",
            },
        )

        input_file_path = self.prepare_path(input_file_path, "pdf")
        output_file_path = self.prepare_path(
            output_file_path, "docx", make_dirs=make_output_dirs
        )

        cv = pdf2docx_Converter(input_file_path)
        cv.convert(output_file_path)
        cv.close()

        self.map_processed_file(input_file_path, output_file_path)

        self.status_table.update_status("Status", "Done")

        return True

    def DOCX_to_HTML(self, input_file_path, output_file_path, make_output_dirs=False):
        self.status_table.update_statuses(
            {
                "File Name": input_file_path.split("\\")[-1],
                "Input": "docx",
                "Output": "html",
                "Status": "Converting",
            },
            reset_to={},
        )
        input_file_path = self.prepare_path(input_file_path, "docx")
        output_file_path = self.prepare_path(
            output_file_path, "html", make_dirs=make_output_dirs
        )

        with open(output_file_path, "w", encoding="utf-8") as o_f:
            with open(input_file_path, "rb") as f:
                o_f.write(mammoth.convert_to_html(f).value)
        self.created_files.append(output_file_path)

        self.map_processed_file(input_file_path, output_file_path)

        self.status_table.update_status("Status", "Done")

        return True

    def PPTX_to_PDF(
        self, input_file_path, output_file_path, make_output_dirs=False, formatType=32
    ):
        self.status_table.update_statuses(
            {
                "File Name": input_file_path.split("\\")[-1],
                "Input": "pptx",
                "Out": "pdf",
                "Status": "Converting",
            },
        )

        input_file_path = self.prepare_path(input_file_path, "pptx")
        output_file_path = self.prepare_path(
            output_file_path, "pdf", make_dirs=make_output_dirs
        )

        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        deck = powerpoint.Presentations.Open(input_file_path, WithWindow=False)
        deck.SaveAs(output_file_path, formatType)
        deck.Close()
        powerpoint.Quit()

        self.map_processed_file(input_file_path, output_file_path)

        self.status_table.update_status("Status", "Done")

        return True

    # transitive (multiple steps)
    def PDF_to_HTML(
        self, input_file_path, output_file_path, ocr=True, make_output_dirs=False
    ):
        self.status_table.update_statuses(
            {
                "File Name": input_file_path.split("\\")[-1],
                "Input": "pdf",
                "Output": "html",
                "Status": "Converting",
            },
        )

        input_file_path = self.prepare_path(input_file_path, "pdf")
        output_file_path = self.prepare_path(
            output_file_path, "html", make_dirs=make_output_dirs
        )

        docx_intermediatary_path = self.change_ext(output_file_path, "docx")

        self.PDF_to_DOCX(input_file_path, docx_intermediatary_path)
        self.DOCX_to_HTML(docx_intermediatary_path, output_file_path)
        os.remove(docx_intermediatary_path)

        if ocr:
            self.HTML_ocr(output_file_path)

        self.map_processed_file(input_file_path, output_file_path)

        self.status_table.update_status("Status", "Done")

        return True

    # transitive (multiple steps)
    def PPTX_to_HTML(
        self, input_file_path, output_file_path, ocr=True, make_output_dirs=False
    ):
        self.status_table.update_statuses(
            {
                "File Name": input_file_path.split("\\")[-1],
                "Input": "pptx",
                "Output": "html",
                "Status": "Converting",
            },
        )

        input_file_path = self.prepare_path(input_file_path, "pptx")
        output_file_path = self.prepare_path(
            output_file_path, "html", make_dirs=make_output_dirs
        )

        pdf_intermediatary_path = self.change_ext(output_file_path, "pdf")

        self.PPTX_to_PDF(input_file_path, pdf_intermediatary_path)
        self.PDF_to_HTML(pdf_intermediatary_path, output_file_path, ocr=ocr)
        os.remove(pdf_intermediatary_path)

        self.map_processed_file(input_file_path, output_file_path)

        self.status_table.update_status("Status", "Done")

        return True

    def HTML_ocr(self, output_file_path):
        self.status_table.update_status("Status", f"Starting OCR")
        with open(output_file_path, "r", encoding="utf-8") as f:
            html_text = f.read()

        base64_image_regex = r"\".*?base64, ?([^\"]*)\"[^>]*>"

        base64_images = re.findall(base64_image_regex, html_text)

        if len(base64_images) > 0:

            for i, unformatted_b64_img in enumerate(base64_images):

                # determine the indexes in the html to insert the OCR text
                base64_image_end_indexes = list(
                    m.end(0) for m in re.finditer(base64_image_regex, html_text)
                )
                base64_image_end_indexes.reverse()

                # pad end of base64 string with "=" to fill up to length divisible by 4
                b64_img = unformatted_b64_img
                if missing_padding := len(unformatted_b64_img) % 4:
                    b64_img += "=" * (4 - missing_padding)

                # if already parsed, return existing value
                hashed_b64_string = zlib.adler32(bytes(b64_img, encoding="utf8"))

                ocr_text = None

                if hashed_b64_string in self.ocr_map:
                    if not self.ocr_map[hashed_b64_string]["ignore"]:
                        self.status_table.update_statuses(
                            {"IMS?": "✅ Already", "Status": f"OCR ({i + 1})"}
                        )
                        ocr_text = self.ocr_map[hashed_b64_string]["text"]
                    else:
                        self.status_table.update_statuses(
                            {"IMS?": "✅ Ignored", "Status": f"OCR ({i + 1})"}
                        )
                        html_text.replace(unformatted_b64_img, "")
                else:
                    # self.status_table.update_status("Status", f"OCR ({i + 1})")
                    self.status_table.update_statuses(
                        {
                            "IMS?": str(zlib.adler32(bytes(b64_img, encoding="utf8"))),
                            "Status": f"OCR ({i + 1})",
                        },
                        show=False,
                    )
                    # add ocr text of the image after the image tag
                    ocr_text = self.base64_ocr(b64_img)

                if ocr_text:
                    html_text = (
                        html_text[: base64_image_end_indexes[i]]
                        + " OCR text: '"
                        + ocr_text
                        + "'"
                        + html_text[base64_image_end_indexes[i] :]
                    )

        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(html_text)

    def base64_ocr(self, b64_string):
        hashed_b64_string = zlib.adler32(bytes(b64_string, encoding="utf8"))

        # convert base64 to bytes, convert bytes to a PIL image object
        img = Image.open(BytesIO(base64.b64decode(b64_string)))
        w, h = img.size

        ocr_text = ""

        ignore = self.config.determine_ignore_image(w, h)
        self.ocr_map[hashed_b64_string] = {
            "text": "",
            "ignore": ignore,
            "seen": False,
        }
        # save image to file if image_output_path exists
        if self.config.image_output_path:
            if os.path.exists(self.config.image_output_path):
                img.save(
                    os.path.join(
                        self.config.image_output_path, f"{hashed_b64_string}.png"
                    )
                )

        if self.config.show_image and not ignore:
            # create a new Toplevel window
            top = tk.Toplevel(self.tk_root)

            prefill = ""
            if self.config.determine_ignore_image(w, h):
                prefill = "y"
            self.status_table.update_status("Status", f"Showing image ({w}, {h})")

            img.thumbnail((800, 600))
            tk_img = ImageTk.PhotoImage(img)

            label = tk.Label(top, image=tk_img)
            label.pack()

            response = simpledialog.askstring(
                "Ignore Image", "Ignore? (*/N/exit)", parent=top, initialvalue=prefill
            )
            top.destroy()

            # make the static type checker happy
            response = "" if not response else response

            # "" = don't ignore, any char but n = ignore, n = don't ignore
            ignore = response != "" and "n" not in response.lower()

            # exit for this session, value of config.show_image in file stays the same
            if response.lower() == "exit":
                self.write_to_cache_file()
                self.tk_root.quit()
                self.config.show_image = False

            self.ocr_map[hashed_b64_string]["seen"] = True

        elif ignore:
            self.status_table.update_status("IMS?", f"✅ small {w}, {h}")

        if not ignore:
            # actually run OCR
            ocr_text = pytesseract.image_to_string(img)

            self.status_table.update_status(
                "OCR Text", ocr_text.replace("\n", " "), reset_to=" "
            )

            self.status_table.update_status("IMS?", f"❌", show=False)

            self.ocr_map[hashed_b64_string]["text"] = ocr_text

        return ocr_text

    def change_ext(self, file, new_extension):
        return f"{file[0:file.rfind('.')]}.{new_extension.replace('.', '')}"

    def write_to_cache_file(self):
        self.status_table.update_status("Status", "Writing cache")
        with open(self.config.cache_file_path, "w") as cache_file:
            cache_file.write(
                json.dumps(
                    {
                        "ocr_map": self.ocr_map,
                        "file_path_map": self.file_path_map,
                        "processed_file_hashes": self.processed_file_hashes,
                    },
                    indent=4,
                )
            )

    def generate_file_hash(self, file_path):
        with open(file_path, "rb", buffering=0) as f:
            return hashlib.file_digest(f, "sha256").hexdigest()

    def map_processed_file(self, in_file_path, out_file_path):
        if out_file_path.split(".")[-1] == self.config.main_output_type:
            self.file_path_map[in_file_path] = out_file_path

            # key: the hash of the content of the processed file
            # value: the location of the processed file, "look here instead"
            self.processed_file_hashes[self.generate_file_hash(in_file_path)] = (
                out_file_path
            )

    def check_if_file_already_processed(self, file_path):
        # check if file path has been seen before, alternatively check if the (hashed) file content has been seen before
        if file_path in self.file_path_map:
            return self.file_path_map[file_path]
        else:
            file_hash = self.generate_file_hash(file_path)
            if file_hash in self.processed_file_hashes:
                return self.processed_file_hashes[file_hash]
            else:
                return False

    def prepare_path(self, path, new_extension=None, make_dirs=False):
        if make_dirs:
            os.makedirs(os.path.dirname(path), exist_ok=True)

        if new_extension:
            path = self.change_ext(path, new_extension)

        return os.path.abspath(path)
