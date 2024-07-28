# Document Merger
## Process
1. For every file of the input type(s) in each directory in the main directory:

    1. Convert from input type(s) to output type, deleting any intermediary files

2. Merge all output files into a single file for each directory in the main directory

## Supported types
| Type | Output | Merge |
|------|--------|-------|
| html |   ✅   |  ✅  |
| pdf  |   ❌   |  ❌  |
| docx |   ✅   |  ❌  |
| pptx |   ❌   |  ❌  |

| ➡️ to ⬇️ | html | pdf | docx | pptx |
|-----------|------|-----|------|------|
| html      | ➖  | ✅  |  ✅  | ✅  |
| pdf       | ❌  | ➖  |  ❌  | ❌  |
| docx      | ❌  | ✅  |  ➖  | ❌  |
| pptx      | ❌  | ❌  |  ❌  | ➖  |


## Prerequisites
Python >=3.12 (probably works on older versions, but untested)

Windows 11/Windows 10
    - Most of the functionality should work on other operating systems
    - The `comtypes` module only works on windows (to my knowledge)

Set the location of inputs and outputs in [Config.py](Config.py)

Download xpdftools from:

https://www.xpdfreader.com/

and set the location of pdftohtml.exe as pdftohtml_path in [Config.py](Config.py)

## TODO
Fix base64 image OCR text appendation
User defined Config class