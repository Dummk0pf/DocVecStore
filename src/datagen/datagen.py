from tqdm import tqdm

from datagen.parse_pdf import PDF
from utils.logger import LogManager
from database.milvus_client import Field
from utils.normalize_token import normalize_all
from database.milvus_client import MilvusDBClient
from embeddings.unigram_embeddings import vectorize

CHUNK_SIZE = 1000

def chunkify(iterable, chunk_size=CHUNK_SIZE):
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i:i + chunk_size]

def run(files: list[tuple]):
    db_client = MilvusDBClient()
    logger = LogManager().get_logger()
    logger.info(f"running datagen for {len(files)} files")

    for _tuple in files:
        input_file_path, output_file_path, page_start, page_end = _tuple

        pdf_instance = PDF(input_file_path, output_file_path, page_start, page_end)
        pdf_instance.convert_pdf_to_text()
        pdf_instance.store_page_offset()
        vectorized_lines = list()

        for page_nm, page in tqdm(enumerate(pdf_instance.paginate()), desc=f"Iterating file: {pdf_instance.output_file_path.name}"):
            for line in page:
                normalized_tokens = normalize_all(line).split("_")
                for token in normalized_tokens:
                    vector = vectorize(token)
                    if vector is None:
                        continue
                    vectorized_lines.append({
                        Field.TOKEN: token,
                        Field.PAGE_NM: page_nm,
                        Field.BOOK_NM: pdf_instance.file_name,
                        Field.EMBEDDINGS: vector,
                    })

        for lines_chunk in tqdm(chunkify(vectorized_lines), desc="Storing documents in MilvusDB"):
            db_client.insert(lines_chunk)
