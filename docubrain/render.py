"""Render a cited PDF page as an image, with the matching region boxed.

Turns "this answer cites page 4" into something a reader can verify at a
glance instead of having to go open the PDF and hunt for it themselves.
"""

from __future__ import annotations

import fitz

_HIGHLIGHT_COLOR = (0.86, 0.11, 0.11)
_HIGHLIGHT_WIDTH = 2.0
# Breathing room so the box doesn't sit on top of the glyphs it frames.
_HIGHLIGHT_PADDING = 4.0


def render_page_png(
    pdf_path: str,
    page_number: int,
    bbox: tuple[float, float, float, float] | None = None,
    *,
    dpi: int = 150,
) -> bytes:
    """Render `page_number` (1-indexed) of `pdf_path` to PNG bytes.

    Draws a rectangle around `bbox` (in PDF point coordinates, as produced
    by `ingest._locate_bbox`) before rendering, when given. Raises
    ValueError if `page_number` is out of range — callers turn that into
    a 404.
    """
    doc = fitz.open(pdf_path)
    try:
        # Checked explicitly: PyMuPDF treats negative indexes as
        # from-the-end, so page 0 would silently render the last page.
        if not 1 <= page_number <= doc.page_count:
            raise ValueError(
                f"Page {page_number} out of range (document has {doc.page_count} pages)"
            )
        page = doc.load_page(page_number - 1)
        if bbox is not None:
            rect = fitz.Rect(*bbox) + (
                -_HIGHLIGHT_PADDING, -_HIGHLIGHT_PADDING, _HIGHLIGHT_PADDING, _HIGHLIGHT_PADDING
            )
            page.draw_rect(
                rect, color=_HIGHLIGHT_COLOR, width=_HIGHLIGHT_WIDTH, overlay=True
            )
        pixmap = page.get_pixmap(dpi=dpi)
        return pixmap.tobytes("png")
    finally:
        doc.close()
