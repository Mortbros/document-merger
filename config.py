import os


class Config:
    def __init__(self):
        user_path = os.path.expanduser("~\\")
        self.analysis_path = f"{user_path}OneDrive\\Homework\\2024"
        self.ignored_dirs = ["Textbooks", "temp", "__pycache__"]
        self.tesseract_path = "C:\\Program files\\Tesseract-OCR\\tesseract.exe"
        self.temp_file_path = f"{user_path}Downloads\\PDF2HTML"
        self.file_path_map_path = f"{user_path}Downloads\\PDF2HTML\\path_map.json"
        self.ocr_map_path = f"{user_path}Downloads\\PDF2HTML\\ocr_map.json"
