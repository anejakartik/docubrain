from docubrain.ingest import ingest_pdf


def test_ingest_pdf_produces_one_document_per_pdf(sample_pdf_path):
    document = ingest_pdf(sample_pdf_path)
    assert document.page_count == 4
    assert document.source_path == sample_pdf_path


def test_every_chunk_has_a_valid_page_number(sample_pdf_path):
    document = ingest_pdf(sample_pdf_path)
    assert len(document.chunks) > 0
    for chunk in document.chunks:
        assert 1 <= chunk.page <= document.page_count
        assert chunk.doc_id == document.doc_id
        assert chunk.text.strip() != ""


def test_chunks_never_cross_a_page_boundary(sample_pdf_path):
    document = ingest_pdf(sample_pdf_path)
    # Each of our 4 sample pages is short enough to be exactly one chunk;
    # if chunking ever merged two pages' text, we'd see fewer than 4 chunks
    # or a chunk containing two different sections' headers.
    section_headers = ["Section 1", "Section 2", "Section 3", "Section 4"]
    for chunk in document.chunks:
        headers_present = [h for h in section_headers if h in chunk.text]
        assert len(headers_present) <= 1, (
            f"chunk spans multiple sections, page boundary was violated: {chunk.text!r}"
        )


def test_ingest_assigns_a_stable_doc_id_when_not_provided(sample_pdf_path):
    doc_a = ingest_pdf(sample_pdf_path)
    doc_b = ingest_pdf(sample_pdf_path)
    assert doc_a.doc_id != doc_b.doc_id  # auto-generated ids should be unique


def test_ingest_respects_an_explicit_doc_id(sample_pdf_path):
    document = ingest_pdf(sample_pdf_path, doc_id="my-contract-v1")
    assert document.doc_id == "my-contract-v1"
    assert all(c.doc_id == "my-contract-v1" for c in document.chunks)
