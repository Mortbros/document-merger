import os
import json


class Config:
    """
    A class containing config values to aid in the conversion process.

    Attributes:
        analysis_path (str): The directory that the main script will run. Analysis will take place on each (not ignored)
            subdirectory individually. i.e a seperate combined file will be created for each initial subdirectory in analysis_path.
        ignored_dirs (list[str]): A list of directory names in analysis_path that have contents that should not be parsed.
        merge_file_types (list[str]): List of file types to look for when processing.
        main_output_type (str): Output file extension type.
        temp_file_path (str): Location of where to put temporary output files.
        keep_temp_files (boolean): Flag to keep/remove temporary files during processing. Note that setting this to false will
            force the program to reprocess every file.
        file_path_map_path (str): Location of a JSON file that maps the path of the input file to the output file. This
            prevents re-analysis of files that have already been ran.
        ocr_map_path (str): Location of a JSON that maps hashed base64 image strings to their output text. This prevents
        re-analysis of images that have already been seen.
        show_image (boolean): flag to show to-be-processed OCR image to user, to allow manual image ignoring. The program will
            show a tkinter window and prompt for ignore status: "" = don't ignore, any char but n = ignore, "n" = don't ignore.
        image_output_path (str): Path to output OCR images, primarily for debugging purposes.
        print_status_table (boolean): Flag to print status table
        tesseract_path (str): Location of the tesseract OCR excecutable.
    """

    def __init__(self):
        user_path = os.path.expanduser("~\\")
        self.analysis_path = f"{user_path}OneDrive\\Homework\\2024"
        self.ignored_dirs = ("Textbooks", "temp", "__pycache__")
        self.merge_file_types = ("pdf", "docx", "pptx")
        self.main_output_type = "html"
        self.temp_file_path = f"{user_path}Downloads\\document-merger"
        self.keep_temp_files = True

        self.file_path_map_path = (
            f"{user_path}Downloads\\document-merger\\path_map.json"
        )
        self.ocr_map_path = f"{user_path}Downloads\\document-merger\\ocr_map.json"

        self.show_image = False
        self.image_output_path = f"{self.temp_file_path}\\images"

        self.print_status_table = True

        self.tesseract_path = "C:\\Program files\\Tesseract-OCR\\tesseract.exe"

    def determine_ignore_image(self, w, h):
        ignore = False
        if w <= 20 or h <= 20 or w * h <= 11904:
            ignore = True

        return ignore

    def initialise_json_file(self, filename):
        if not os.path.exists(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                _ = {}
                f.write(json.dumps(_))

    def initialise_directory(self, path):
        if path:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

    def initialise_files(self):
        self.initialise_directory(self.temp_file_path)
        self.initialise_directory(self.image_output_path)

        self.initialise_json_file(self.file_path_map_path)
        self.initialise_json_file(self.ocr_map_path)
