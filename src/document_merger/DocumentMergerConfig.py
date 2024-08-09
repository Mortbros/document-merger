import os
import json
from typing import Callable


class DocumentMergerConfig:
    """A class containing config values to aid in the conversion process.

    analysis_path (str): The directory that the main script will run. Analysis will take place on each (not ignored)
        subdirectory individually. i.e a seperate combined file will be created for each initial subdirectory in analysis_path.
    ignored_dirs (tuple[str]): A list of directory names in analysis_path that have contents that should not be parsed.
    ignored_files (list[str]): A list of a mix of absolute or relative file paths to ignore when converting.
    merge_file_types (list[str]): List of file types to look for when processing.
    main_output_type (str): Output file extension type.
    temp_file_path (str): Location of where to put temporary output files.
    keep_temp_files (bool): Flag to keep/remove temporary files during processing. Note that setting this to false will
        force the program to reprocess every file.
    process_subdirectories_individually (bool): A flag that enables/disables a single HTML file for each subdirectory, or one for the
        root directory
    file_path_map_path (str): Location of a JSON file that maps the path of the input file to the output file. This
        prevents re-analysis of files that have already been ran.
    ocr_map_path (str): Location of a JSON that maps hashed base64 image strings to their output text. This prevents
        re-analysis of images that have already been seen.
    create_imageless_version (bool): Flag to produce an additional HTML file that has all the images removed (for quicker fuzzy finding)
    show_image (bool): flag to show to-be-processed OCR image to user, to allow manual image ignoring. The program will
        show a tkinter window and prompt for ignore status: "" = don't ignore, any char but n = ignore, "n" = don't ignore.
    image_output_path (str | None): Path to output OCR images, primarily for debugging purposes.
    print_status_table (bool): Flag to print status table
    tesseract_path (str): Location of the tesseract OCR excecutable.
    determine_ignore_image (Callable | None): A function that takes ints width and height and returns a boolean whether the image should
        be exempt from being processed by the OC
    """

    def __init__(
        self,
        analysis_path: str,
        temp_file_path: str,
        file_path_map_path: str,
        ocr_map_path: str,
        tesseract_path: str,
        ignored_dirs: tuple[str] = ("__pycache__",),
        ignored_files: list[str] = [],
        main_output_type: str = "html",
        process_subdirectories_individually: bool = True,
        keep_temp_files: bool = True,
        create_imageless_version: bool = False,
        show_image: bool = False,
        image_output_path: str | None = None,
        print_status_table: bool = True,
        determine_ignore_image: Callable | None = None,
    ):
        self.analysis_path = analysis_path
        self.ignored_dirs = ignored_dirs
        # ignored_files can be a mix of absolute and relative paths.
        self.ignored_files = ignored_files
        self.merge_file_types = ("pdf", "docx", "pptx")
        self.main_output_type = main_output_type
        self.temp_file_path = temp_file_path
        self.keep_temp_files = keep_temp_files
        self.process_subdirectories_individually = process_subdirectories_individually

        self.file_path_map_path = file_path_map_path
        self.ocr_map_path = ocr_map_path

        self.create_imageless_version = create_imageless_version
        self.show_image = show_image
        self.image_output_path = image_output_path

        self.print_status_table = print_status_table
        if os.path.exists(tesseract_path):
            self.tesseract_path = tesseract_path
        else:
            raise FileNotFoundError(f"Tesseract path '{tesseract_path}' is invalid")

        if determine_ignore_image is None:
            self.determine_ignore_image = self.default_determine_ignore_image
        else:
            if callable(determine_ignore_image):
                self.determine_ignore_image = self.default_determine_ignore_image
            else:
                raise TypeError("determine_ignore_image input must be a function")

    def default_determine_ignore_image(self, w, h):
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
