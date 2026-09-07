import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from scripts.make_sample_pdf import make_sample_pdf


@pytest.fixture(scope="session")
def sample_pdf_path(tmp_path_factory) -> str:
    out_dir = tmp_path_factory.mktemp("sample_data")
    return make_sample_pdf(str(out_dir / "sample_contract.pdf"))
