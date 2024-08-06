import os
import shutil

from .Converter import Converter
from .StatusTable import StatusTable

import logging

import time


class DocumentMerger:
    def __init__(self, config):
        self.config = config

    def merge_html_files(self, input_dir_path, output_file_path):
        # get all HTML files in the output directory
        html_files = [
            os.path.join(input_dir_path, f)
            for f in os.listdir(input_dir_path)
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
            # created_files.append(input_dir_path)

    def start(self):
        start_time = time.time()
        logging.getLogger().setLevel(logging.ERROR)

        self.config.initialise_files()

        # change directory to analysis path
        os.chdir(self.config.analysis_path)

        converter = Converter(self.config)
        status_table = StatusTable(self.config.print_status_table)

        # iterate over directories
        for dir_name in os.listdir("."):
            if (
                os.path.isdir(dir_name)
                and os.path.exists(dir_name)
                and len(os.listdir(dir_name)) != 0
            ):
                if dir_name not in self.config.ignored_dirs:
                    # get all pdf files in directory
                    status_table.update_status("Directory", dir_name)

                    paths = []
                    for root, dirs, files in os.walk(dir_name):
                        for file in files:
                            # each time we encounter a new file:
                            # if it matches any relative file name it will be ignored, then its absolute path will be checked against all provided absolute apaths
                            if (
                                file.endswith(self.config.merge_file_types)
                                and file not in self.config.ignored_files
                                and os.path.abspath(file)
                                not in self.config.ignored_files
                            ):
                                paths.append(os.path.join(root, file))

                    for file in paths:
                        convert_path = os.path.join(
                            self.config.temp_file_path,
                            dir_name,
                            file.split("\\")[-1],
                        )

                        if self.config.absolute_temp_directory_names:
                            # Make temporary directory with name that is unique to the input directory
                            # We do this by removing all invalid letters in the input, then replacing \ with !
                            # This modified path is then used as the directory name inside the temp file directory
                            convert_path = os.path.join(
                                self.config.temp_file_path,
                                dir_name,
                                "".join(
                                    c
                                    for c in "!".join(
                                        os.path.abspath(file).split("\\")[0:-1]
                                    )
                                    if c.isalnum() or c in " !"
                                ),
                            )

                        converter.convert(
                            file,
                            convert_path,
                            output_type=self.config.main_output_type,
                            make_output_dirs=True,
                        )
                    # if no conversion files are found in the directory, don't merge html files
                    if len(paths) > 0:
                        # merge HTML files in the temp directory into a single HTML file in the course directory
                        self.merge_html_files(
                            os.path.join(self.config.temp_file_path, dir_name),
                            os.path.join(dir_name, f"{dir_name}.html"),
                        )

        if not self.config.keep_temp_files:
            shutil.rmtree(self.config.temp_file_path)

        print(f"Finished in {round(time.time() - start_time, 2)} seconds")
