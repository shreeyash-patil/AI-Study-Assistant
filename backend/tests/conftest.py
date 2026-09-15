import fitz
import pytest


@pytest.fixture
def sample_pdf_bytes():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a test document about Binary Search Trees.")
    page.insert_text((50, 80), "A BST is a tree where left children are smaller than the root.")

    page2 = doc.new_page()
    page2.insert_text((50, 50), "This is page two, continuing the discussion on traversals.")

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes