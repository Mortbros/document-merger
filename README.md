# Document Merger
## Process

For all pdfs in each directory in the main directory:
1. Convert pdf to docx
2. Convert docx to HTML
3. Delete docx

Merge all html files into a single file for each directory in the main directory

## Prerequisites
Pip install dependencies from all python files.

Set the location of inputs and outputs in [Config.py](Config.py)

analysis_path, ignored_dirs, tesseract_path, temp_file_path, file_path_map_path, ocr_map_path, pdftohtml_path

Download xpdftools from:

https://www.xpdfreader.com/

and set the location of pdftohtml.exe as pdftohtml_path in [Config.py](Config.py)

## TODO
Fix base64 image OCR text appendation