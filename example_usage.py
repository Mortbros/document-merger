from document_merger import DocumentMerger, DocumentMergerConfig

# from src.document_merger import DocumentMerger, DocumentMergerConfig

import os

user_path = os.path.expanduser("~\\")


document_merger_config = DocumentMergerConfig(
    analysis_path=f"{user_path}OneDrive\\Homework\\2024",
    temp_file_path=f"{user_path}Downloads\\document-merger",
    file_path_map_path=f"{user_path}Downloads\\document-merger\\path_map.json",
    ocr_map_path=f"{user_path}Downloads\\document-merger\\ocr_map.json",
    # image_output_path=f"{user_path}Downloads\\document-merger\\images",
    tesseract_path="C:\\Program files\\Tesseract-OCR\\tesseract.exe",
    ignored_dirs=(
        "Textbooks",
        "temp",
        "__pycache__",
        "Assignment 1",
        "Assessment 1",
        "Assignment 2",
        "Assessment 2",
        "Algorithms and Analysis",
        "Full stack development",
        "Introduction to Cybersecurity",
        "Software engineering fundamentals",
    ),
    main_output_type="html",
    keep_temp_files=True,
    show_image=False,
    print_status_table=True,
    create_imageless_version=True,
    process_subdirectories_individually=True,
    absolute_temp_directory_names=True,
)

DocumentMerger(document_merger_config).start()
