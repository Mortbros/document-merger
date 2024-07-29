# Document Merger
## Process
1. For every file of the input type(s) in each directory in the main directory:

    1. Convert from input type(s) to output type, deleting any intermediary files

    2. Merge all output files into a single file

## Supported types
| Type | Output | Merge |
|------|--------|-------|
| html |   ✅   |  ✅  |
| pdf  |   ❌   |  ❌  |
| docx |   ❌   |  ❌  |
| pptx |   ❌   |  ❌  |

| ➡️ to ⬇️ | html | pdf | docx | pptx |
|-----------|------|-----|------|------|
| html      | ➖  | ✅  |  ✅  | ✅  |
| pdf       | ❌  | ➖  |  ❌  | ❌  |
| docx      | ❌  | ✅  |  ➖  | ❌  |
| pptx      | ❌  | ❌  |  ❌  | ➖  |


## Prerequisites
Python >=3.12.2 (probably works on older versions, but untested)

Windows 11/Windows 10
- Most of the functionality should work on other operating systems
- The `comtypes` module only works on windows (to my knowledge)

Set the location of inputs and outputs in a DocumentMergerConfig class (see [example_usage.py](example_usage.py) for example usage)

## Example usage
Import DocumentMerger and DocumentMergerConfig, then instantiate DocumentMergerConfig and feed it all required config values. Feed this DocumentMergerConfig into DocumentMerger, then run the `start()` command.
See [example_usage.py](example_usage.py)

## TODO
Fix base64 image OCR text appendation