import os


class Config:
    """
    A class containing config values to aid in the conversion process.

    Attributes:
        analysis_path (str): The directory that the main script will run. Analysis will take place on each (not ignored)
        subdirectory individually. i.e a seperate combined file will be created for each initial subdirectory in analysis_path.
        ignored_dirs (list[str]): A list of directory names in analysis_path that have contents that should not be parsed.
        tesseract_path (str): Location of the tesseract OCR excecutable.
        temp_file_path (str): Location of where to put temporary output files.
        file_path_map_path (str): Location of a JSON file that maps the path of the input file to the output file. This
        prevents re-analysis of files that have already been ran.
        ocr_map_path (str): Location of a JSON that maps hashed base64 image strings to their output text. This prevents
        re-analysis of images that have already been seen.
        pdftohtml_path (str): Location of the xpdf pdftohtml excecutable.
    """

    def __init__(self):
        user_path = os.path.expanduser("~\\")
        self.analysis_path = f"{user_path}OneDrive\\Homework\\2024"
        self.ignored_dirs = ["Textbooks", "temp", "__pycache__"]
        self.tesseract_path = "C:\\Program files\\Tesseract-OCR\\tesseract.exe"
        self.temp_file_path = f"{user_path}Downloads\\PDF2HTML"
        self.file_path_map_path = f"{user_path}Downloads\\PDF2HTML\\path_map.json"
        self.ocr_map_path = f"{user_path}Downloads\\PDF2HTML\\ocr_map.json"
        self.pdftohtml_path = f"{os.path.dirname(os.path.realpath(__file__))}\\xpdf-tools-win-4.05\\bin64\\pdftohtml.exe"
