from pdf_processor import parse_pdf, generate_session_id


def test_parse_pdf_extracts_text(sample_pdf_bytes):
    result = parse_pdf(sample_pdf_bytes)

    assert "full_text" in result
    assert "page_boundaries" in result
    assert "table_chunks" in result
    assert "Binary Search Trees" in result["full_text"]


def test_parse_pdf_tracks_correct_page_count(sample_pdf_bytes):
    result = parse_pdf(sample_pdf_bytes)

    assert len(result["page_boundaries"]) == 2


def test_parse_pdf_page_boundaries_are_sequential(sample_pdf_bytes):
    result = parse_pdf(sample_pdf_bytes)
    boundaries = result["page_boundaries"]

    for i in range(len(boundaries) - 1):
        current_end = boundaries[i][1]
        next_start = boundaries[i + 1][0]
        assert next_start >= current_end


def test_parse_pdf_second_page_content_present(sample_pdf_bytes):
    result = parse_pdf(sample_pdf_bytes)

    assert "page two" in result["full_text"]
    assert "traversals" in result["full_text"]


def test_generate_session_id_returns_string():
    session_id = generate_session_id()
    assert isinstance(session_id, str)
    assert len(session_id) > 0


def test_generate_session_id_is_unique():
    id1 = generate_session_id()
    id2 = generate_session_id()
    assert id1 != id2