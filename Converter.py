import comtypes.client
import os
from Config import Config


class Converter:

    def __init__(self, output_file_type):
        self.created_files = []
        self.output_file_type = output_file_type
        self.supported_input_types = ["pdf", "html", "pptx", "docx"]
        self.supported_output_types = ["pdf", "html"]
        self.config = Config()

    def convert(self, input_file_path, output_file_path):
        # convert input and output to absolute paths if not already
        input_file_path, output_file_path = os.path.abspath(
            input_file_path
        ), os.path.abspath(output_file_path)

        if output_file_path[-3:] != self.output_file_type:
            output_file_path = f"{output_file_path}.{self.output_file_type}"

        input_type = input_file_path.split(".")[-1]
        output_type = output_file_path.split(".")[-1]

        if input_type not in self.supported_input_types:
            print(
                f"Unsupported input file type '{input_type}' (supported types are {', '.join(self.supported_input_types)})"
            )
            return False
        elif output_type not in self.supported_output_types:
            print(
                f"Unsupported output file type '{output_type}' (supported types are {', '.join(self.supported_input_types)})"
            )
            return False

        if input_type == "pdf" and output_type == "html":
            self.PDF_to_HTML(input_file_path, output_file_path)
        elif input_type == "pdf" and output_type == "docx":
            self.PDF_to_DOCX(input_file_path, output_file_path)
        elif input_type == "docx" and output_type == "html":
            self.DOCX_to_HTML(input_file_path, output_file_path)
        elif input_type == "pptx" and output_type == "html":
            self.PPTX_to_PDF(input_file_path, output_file_path)

    def PDF_to_HTML(self, input_file_path, output_file_path):
        os.system(
            f'{self.config.pdftohtml_path} -nofonts "{input_file_path}" "{os.path.join(self.config.temp_file_path, output_file_path)}"'
        )
        return True

    def PDF_to_DOCX(self, input_file_path, output_file_path):
        pass

    def DOCX_to_HTML(self, input_file_path, output_file_path):
        pass

    def PPTX_to_PDF(self, input_file_path, output_file_path, formatType=32):
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        powerpoint.Visible = 1

        deck = powerpoint.Presentations.Open(input_file_path)
        deck.SaveAs(output_file_path, formatType)  # formatType = 32 for ppt to pdf
        deck.Close()
        powerpoint.Quit()
        return True
