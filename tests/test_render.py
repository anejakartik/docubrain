import fitz
import pytest

from docubrain import ingest_pdf, render_page_png

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def test_every_chunk_on_a_text_pdf_gets_a_bbox(sample_pdf_path):
    document = ingest_pdf(sample_pdf_path)
    assert all(chunk.bbox is not None for chunk in document.chunks)


def test_chunk_bbox_lies_within_its_page(sample_pdf_path):
    document = ingest_pdf(sample_pdf_path)
    pdf = fitz.open(sample_pdf_path)
    for chunk in document.chunks:
        page_rect = pdf.load_page(chunk.page - 1).rect
        x0, y0, x1, y1 = chunk.bbox
        assert 0 <= x0 < x1 <= page_rect.width
        assert 0 <= y0 < y1 <= page_rect.height
    pdf.close()


def test_render_page_png_returns_a_png(sample_pdf_path):
    assert render_page_png(sample_pdf_path, 1).startswith(PNG_MAGIC)


def test_render_with_bbox_differs_from_plain_render(sample_pdf_path):
    chunk = ingest_pdf(sample_pdf_path).chunks[0]
    plain = render_page_png(sample_pdf_path, chunk.page)
    boxed = render_page_png(sample_pdf_path, chunk.page, chunk.bbox)
    assert plain != boxed


@pytest.mark.parametrize("page_number", [0, -1, 5])
def test_render_rejects_out_of_range_pages(sample_pdf_path, page_number):
    # page 0 / -1 matter: PyMuPDF would otherwise wrap them to the last page.
    with pytest.raises(ValueError):
        render_page_png(sample_pdf_path, page_number)
