import fitz
import uuid

def parse_pdf(file_bytes: bytes) -> list[str]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    chunks = []

    for page in doc:
        tables = page.find_tables()
        table_bboxes = [table.bbox for table in tables]

        text = page.get_text()

        if text.strip():
            chunks.append(text)

        for table in tables:
            markdown_table = table_to_markdown(table)
            if markdown_table:
                chunks.append(markdown_table)

    return chunks

def table_to_markdown(table) -> str:
    try:
        data = table.extract()
        if not data or len(data) == 0:
            return ""

        rows = [[cell if cell else "" for cell in row] for row in data]

        header = rows[0]
        markdown = "| " + " | ".join(header) + " |\n"
        markdown += "| " + " | ".join(["---"] * len(header)) + " |\n"

        for row in rows[1:]:
            markdown += "| " + " | ".join(row) + " |\n"

        return markdown
    except Exception:
        return ""

def generate_session_id() -> str:
    return str(uuid.uuid4())