import pickle
import pathlib
import subprocess

from settings.config import Config
from utils.logger import LogManager

class PDF:

    PAGE_BREAK = "#$<>PAGE_BREAK<>$#"

    def __init__(self, input_file_name, output_file_name, page_start = 0, page_end = 0) -> None:
        input_dir = Config().get_instance()["INPUT_DIR"]
        output_dir = Config().get_instance()["OUTPUT_DIR"]
        input_file_path = pathlib.Path.joinpath(pathlib.Path(input_dir), pathlib.Path(input_file_name))
        output_file_path = pathlib.Path.joinpath(pathlib.Path(output_dir), pathlib.Path(output_file_name))

        if not input_file_path.exists():
            raise FileNotFoundError(f"the file specified in the path {input_file_path} does not exist")
        if not output_file_path.parent.exists():
            raise FileNotFoundError(f"the file specified in the path {output_file_path} does not exist")
        if page_start < 0:
            raise ValueError(f"invalid `page_start` value: {page_start}")
        if page_end < 0:
            raise ValueError(f"invalid `page_end` value: {page_end}")
        
        self.page_start = page_start
        self.page_end = page_end
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.file_name = input_file_path.stem

    def convert_pdf_to_text(self):
        logger = LogManager().get_logger()
        
        logger.info(f"file: {self.input_file_path.name} to text conversion started")
        if self.page_start == 0 and self.page_end == 0:
            subprocess.call(["pdftotext", f"{self.input_file_path}", f"{self.output_file_path}", "-layout"])
        else:
            subprocess.call(["pdftotext", f"{self.input_file_path}", f"{self.output_file_path}", "-f", f"{self.page_start}", "-l", f"{self.page_end}", "-layout"])

        logger.info(f"replacing form-feed characters to page break characters")
        subprocess.call(["sed", "-i", "s/\\xC/\\n#$<>PAGE_BREAK<>$#\\n/g", f"{self.output_file_path}"])

    def paginate(self):
        lines = list()
        file = open(self.output_file_path, "r")

        for line in file:
            line = line.strip()
            if line == PDF.PAGE_BREAK:
                yield lines
                lines.clear()
                continue
            lines.append(line)

        file.close()

    def store_page_offset(self):
        pdf_details = (self.input_file_path.stem, self.page_start, self.page_end)
        pickle.dump(pdf_details, open(pathlib.Path.joinpath(pathlib.Path(Config().get_instance()["OUTPUT_DIR"]), pathlib.Path(f"./pickle_files/{self.input_file_path.stem}.pkl")), "wb"))