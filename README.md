# Document Merger
## Process
For every file of the input type(s) in each directory in the main directory
Then convert from input type(s) to output type, deleting any intermediary files
Merge all output files into a single file for each directory in the main directory

## Supported types
| Type | Output | Merge |
|--|--|--|
| html | ✅ | ✅ |
| pdf  | ❌ | ❌ |
| docx | ✅ | ❌ |
| pptx | ❌ | ❌ |

| ➡️ to ⬇️ | html | pdf | docx | pptx |
|-----------|------|-----|------|------|
| html      | ➖  | ✅  |  ✅  | ✅  |
| pdf       | ❌  | ➖  |  ❌  | ❌  |
| docx      | ❌  | ✅  |  ➖  | ❌  |
| pptx      | ❌  | ❌  |  ❌  | ➖  |


## Prerequisites
Pip install dependencies from all python files.

Set the location of inputs and outputs in [Config.py](Config.py)

analysis_path, ignored_dirs, tesseract_path, temp_file_path, file_path_map_path, ocr_map_path, pdftohtml_path

Download xpdftools from:

https://www.xpdfreader.com/

and set the location of pdftohtml.exe as pdftohtml_path in [Config.py](Config.py)

## TODO
Fix base64 image OCR text appendation