import os
import re
import shutil

from .Converter import Converter
from .StatusTable import StatusTable

import logging

import time


class DocumentMerger:
    def __init__(self, config):
        self.config = config
        self.status_table = StatusTable(self.config.print_status_table)

    def merge_html_files(self, input_dir_path, output_file_path):
        self.status_table.update_statuses(
            {
                "File Name": f"{output_file_path.split('\\')[-1]}",
                "Status": "Merging HTML",
                "Input": "html",
                "Output": "html",
            },
        )
        # get all HTML files in the output directory
        html_files = [
            os.path.join(input_dir_path, f)
            for f in os.listdir(input_dir_path)
            if f.endswith(".html")
        ]

        # empty out HTML file before writing to prevent a single file from storing multiple outputs
        with open(output_file_path, "w", encoding="utf8") as out_f:
            out_f.write("")

        # iterate over all html files and append to merged html file
        with open(output_file_path, "a+", encoding="utf8") as out_f:
            for html_file in html_files:
                with open(html_file, "r", encoding="utf8") as f:
                    out_f.write(f.read())
            # created_files.append(input_dir_path)

        self.status_table.update_status("Status", "Done")

        if self.config.create_imageless_version:
            imageless_file_path = output_file_path.replace(".html", " (Imageless).html")
            self.status_table.update_statuses(
                {
                    "File Name": imageless_file_path.split("\\")[-1],
                    "Status": "Creating imageless HTML",
                    "Input": "html",
                    "Output": "html",
                },
            )

            with open(imageless_file_path, "w", encoding="utf8") as f:
                with open(
                    output_file_path,
                    "r",
                    encoding="utf8",
                    errors="ignore",
                ) as existing_html:
                    f.write(
                        re.sub(
                            r'<img src=".*?base64, ?[^"]*"[^>]*>',
                            "",
                            existing_html.read(),
                        )
                    )

    # function that takes a directory and performs the conversion and merging process for that directory
    def process_subdirectory(self, dir_name):
        converter = Converter(self.config)

        self.status_table.update_status("Directory", dir_name.split("\\")[-1])

        processed_a_file = False
        for root, dirs, files in os.walk(dir_name):
            for file in files:
                # each time we encounter a new file:
                # if it matches any relative file name it will be ignored, then its absolute path will be checked against all provided absolute apaths
                # get all valid input files in that directory
                if (
                    file.endswith(self.config.merge_file_types)
                    and file not in self.config.ignored_files
                    and os.path.abspath(file) not in self.config.ignored_files
                ):
                    input_file = os.path.join(root, file)

                    convert_path = os.path.join(
                        self.config.temp_file_path,
                        dir_name.split("\\")[-1],
                        input_file.split("\\")[-1],
                    )

                    converter.convert(
                        input_file,
                        convert_path,
                        output_type=self.config.main_output_type,
                        make_output_dirs=True,
                    )
                    processed_a_file = True

        # if no conversion files are found in the directory, don't merge html files
        if processed_a_file:
            # merge HTML files in the temp directory into a single HTML file in the course directory
            output_file_path = os.path.join(
                dir_name, f"{dir_name.split('\\')[-1]}.html"
            )
            self.merge_html_files(
                os.path.join(self.config.temp_file_path, dir_name.split("\\")[-1]),
                output_file_path,
            )

    def start(self):
        start_time = time.time()
        logging.getLogger().setLevel(logging.ERROR)

        self.config.initialise_files()

        # change directory to analysis path
        os.chdir(self.config.analysis_path)

        # iterate over directories
        if self.config.process_subdirectories_individually:
            for dir_name in os.listdir("."):
                if (
                    os.path.isdir(dir_name)
                    and os.path.exists(dir_name)
                    and len(os.listdir(dir_name)) != 0
                ):
                    if dir_name not in self.config.ignored_dirs:
                        # run function for each directory in the root directory: one output per subdirectory
                        self.process_subdirectory(dir_name)
        else:
            # run function on root directory: one output overall, for the root directory
            self.process_subdirectory(self.config.analysis_path)

        if not self.config.keep_temp_files:
            shutil.rmtree(self.config.temp_file_path)

        print(f"Finished in {round(time.time() - start_time, 2)} seconds")
