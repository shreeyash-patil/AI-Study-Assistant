import fitz
import uuid

def parse_pdf(file_bytes: bytes) -> dict:
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    full_text = ""
    page_boundaries = []  # (start_offset, end_offset, page_num)
    table_chunks = []     # [{"text": ..., "page": ...}]

    for page_num, page in enumerate(doc, start=1):
        text = extract_text_with_columns(page)
        start_offset = len(full_text)
        if text.strip():
            full_text += text + "\n"
        end_offset = len(full_text)
        page_boundaries.append((start_offset, end_offset, page_num))

        tables = page.find_tables()
        for table in tables:
            markdown_table = table_to_markdown(table)
            if markdown_table:
                table_chunks.append({"text": markdown_table, "page": page_num})

    return {
        "full_text": full_text,
        "page_boundaries": page_boundaries,
        "table_chunks": table_chunks
    }


def extract_text_with_columns(page) -> str:
    blocks = page.get_text("blocks")
    text_blocks = [b for b in blocks if b[6] == 0 and b[4].strip()]

    if not text_blocks:
        return ""

    page_width = page.rect.width
    mid = page_width / 2

    left_blocks = [b for b in text_blocks if b[0] < mid - 20]
    right_blocks = [b for b in text_blocks if b[0] >= mid - 20]

    if len(left_blocks) >= 3 and len(right_blocks) >= 3:
        left_blocks.sort(key=lambda b: b[1])
        right_blocks.sort(key=lambda b: b[1])
        ordered = left_blocks + right_blocks
    else:
        ordered = sorted(text_blocks, key=lambda b: b[1])

    return "\n".join(b[4] for b in ordered)


def table_to_markdown(table) -> str:
    try:
        data = table.extract()
        if not data:
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