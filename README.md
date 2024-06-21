# PDF2HTML merger
## Process

For all pdfs in a course directory:
1. Convert pdf to docx
2. Convert docx to HTML
3. Delete docx

Merge all html files

Done

## Prerequisites
Pip install dependencies from all python files.

Set the location of inputs and outputs in [Config.py](Config.py)

analysis_path, ignored_dirs, tesseract_path, temp_file_path, file_path_map_path, ocr_map_path, pdftohtml_path

Download xpdftools from:

https://www.xpdfreader.com/

and set the location of pdftohtml.exe as pdftohtml_path in [Config.py](Config.py)

## TODO
Rename this repository
Fix base64 image OCR text appendation
Fix HTML file overwriting