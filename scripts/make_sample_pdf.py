"""Generate a small synthetic multi-page PDF for the demo and test suite.

Uses PyMuPDF directly (no extra dependency like reportlab) — each page
gets distinct, identifiable content so tests can assert a specific
question maps to a specific page.
"""

from __future__ import annotations

import os

import fitz

PAGES = [
    (
        "Section 1 - Termination Clause\n\n"
        "Either party may terminate this agreement with 30 days written "
        "notice. Termination for cause requires immediate written notice "
        "and forfeits any prepaid fees for the remaining term."
    ),
    (
        "Section 2 - Payment Terms\n\n"
        "Invoices are due net 45 from the invoice date. Late payments "
        "accrue interest at 1.5% per month. All fees are quoted in USD "
        "and are non-refundable once services have been rendered."
    ),
    (
        "Section 3 - Confidentiality\n\n"
        "Each party agrees to hold the other party's confidential "
        "information in strict confidence for a period of five years "
        "following disclosure, and not to use it for any purpose outside "
        "the scope of this agreement."
    ),
    (
        "Section 4 - Liability Cap\n\n"
        "Total liability under this agreement is capped at the fees paid "
        "in the twelve months preceding the claim. Neither party is "
        "liable for indirect, incidental, or consequential damages."
    ),
]


def make_sample_pdf(output_path: str) -> str:
    doc = fitz.open()
    for page_text in PAGES:
        page = doc.new_page()
        page.insert_text((72, 72), page_text, fontsize=11)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    doc.close()
    return output_path


if __name__ == "__main__":
    path = make_sample_pdf("sample_data/sample_contract.pdf")
    print(f"wrote {path}")
