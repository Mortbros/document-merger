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

    def merge_html_files(self, input_dir_paths, output_file_path):
        self.status_table.update_statuses(
            {
                "File Name": f"{output_file_path.split('\\')[-1]}",
                "Status": "Merging HTML",
                "Input": "html",
                "Output": "html",
            },
        )
        # get all HTML files in the output directory
        html_files = []

        # put input_dir_paths into a list with one item if it is not a list
        if not isinstance(input_dir_paths, list):
            input_dir_paths = [input_dir_paths]

        # for path in input_dir_paths:
        #     html_files.extend(
        #         os.path.join(path, f) for f in os.listdir(path) if f.endswith(".html")
        #     )
        html_files = input_dir_paths

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

    def generate_absolute_dir_name(self, file):
        # takes a directory or a file and returns a formatted absolute version of it
        return str(
            "".join(
                c
                for c in "!".join(os.path.abspath(file).split("\\")[0:-1])
                if c.isalnum() or c in " !"
            ),
        )

    def process_subdirectory(self, dir_name):
        # takes a directory and performs the conversion and merging process for that directory
        converter = Converter(self.config)

        self.status_table.update_status("Directory", dir_name.split("\\")[-1])

        input_paths = []
        output_paths = []

        for root, dirs, files in os.walk(dir_name):
            for file in files:
                # each time we encounter a new file:
                # if it matches any relative file name it will be ignored, then its absolute path will be checked against all provided absolute paths
                # get all valid input files in that directory
                # we also check for ignored directories here:
                # if the absolute file path of the file starts with any of the input strings, ignore the file.
                # (yes i am aware that this introduces a bug with ignoring directories called C or C:, but if that ends up being an actual problem then i'll fix it)
                # if any of the directories in the absolute path of the file is present in ignored_dirs, ignore that file

                abs_file_path = os.path.join(os.getcwd(), root, file)
                if (
                    file.endswith(self.config.merge_file_types)
                    and file not in self.config.ignored_files
                    and abs_file_path not in self.config.ignored_files
                    and not abs_file_path.startswith(self.config.ignored_dirs)
                    and not any(
                        f in self.config.ignored_dirs for f in abs_file_path.split("\\")
                    )
                ):
                    input_paths.append(abs_file_path)

        for file in input_paths:
            output_path = os.path.join(
                self.config.temp_file_path,
                dir_name.split("\\")[-1],
                converter.change_ext(
                    file.split("\\")[-1], self.config.main_output_type
                ),
            )

            if self.config.absolute_temp_directory_names:
                # Make temporary directory with name that is unique to the input directory
                # We do this by removing all invalid letters in the input, then replacing \ with !
                # This modified path is then used as the directory name inside the temp file directory
                output_path = os.path.join(
                    self.config.temp_file_path,
                    self.generate_absolute_dir_name(file),
                    converter.change_ext(
                        file.split("\\")[-1], self.config.main_output_type
                    ),
                )
            output_paths.append(output_path)
            converter.convert(
                file,
                output_path,
                output_type=self.config.main_output_type,
                make_output_dirs=True,
            )

        # if no valid conversion files are found in the directory, don't merge html files
        # TODO fix the type of output_paths
        if len(output_paths) > 0 and self.config.main_output_type == "html":
            # merge HTML files in the temp directory into a single HTML file in the course directory
            output_file_path = os.path.join(
                dir_name, f"{dir_name.split('\\')[-1]}.html"
            )
            # TODO: feed the paths variable straight into merge_html_files. From there, grab all html files in all those folders and merge into 1
            # this means a rework to merge_html_files to accept a list of paths.
            self.merge_html_files(
                output_paths,
                output_file_path,
            )

    def start(self):
        start_time = time.time()
        logging.getLogger().setLevel(logging.ERROR)

        self.config.initialise_files()

        # change directory to analysis path
        os.chdir(self.config.analysis_path)

        # iterate over subdirectories in analysis path
        if self.config.process_subdirectories_individually:
            for dir_name in os.listdir("."):
                if (
                    os.path.isdir(dir_name)
                    and len(os.listdir(dir_name)) != 0
                    and os.path.exists(dir_name)
                ):
                    # this is a bit of an agressive way of doing directory ignoring, but it should work for now
                    if (
                        dir_name not in self.config.ignored_dirs
                        and os.path.abspath(dir_name) not in self.config.ignored_dirs
                        and not os.path.abspath(dir_name).startswith(
                            self.config.ignored_dirs
                        )
                        and not any(
                            f in self.config.ignored_dirs
                            for f in os.path.abspath(dir_name).split("\\")
                        )
                    ):
                        # run function for each directory in the root directory: one output per subdirectory
                        self.process_subdirectory(dir_name)
        else:
            # run function on root directory: one output overall, for the root directory
            self.process_subdirectory(self.config.analysis_path)

        if not self.config.keep_temp_files:
            shutil.rmtree(self.config.temp_file_path)

        print(f"Finished in {round(time.time() - start_time, 2)} seconds")
