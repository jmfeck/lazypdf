import os

import pymupdf
import pytest


@pytest.fixture
def sample_pdf(tmp_path):
    """Create a simple 3-page PDF for testing."""
    path = str(tmp_path / "sample.pdf")
    doc = pymupdf.open()
    for i in range(3):
        page = doc.new_page(width=595, height=842)  # A4
        page.insert_text(pymupdf.Point(72, 72), f"Page {i + 1} content", fontsize=14)
        page.insert_text(pymupdf.Point(72, 100), f"This is test text on page {i + 1}.")
    doc.save(path)
    doc.close()
    return path


@pytest.fixture
def sample_pdf_2(tmp_path):
    """Create a second simple PDF for merge tests."""
    path = str(tmp_path / "sample2.pdf")
    doc = pymupdf.open()
    for i in range(2):
        page = doc.new_page(width=595, height=842)
        page.insert_text(pymupdf.Point(72, 72), f"Second doc page {i + 1}")
    doc.save(path)
    doc.close()
    return path


@pytest.fixture
def sample_image(tmp_path):
    """Create a simple test PNG image."""
    path = str(tmp_path / "test_image.png")
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 200, 200), 0)
    pix.clear_with(255)
    pix.save(path)
    return path


@pytest.fixture
def output_dir(tmp_path):
    """Provide a clean output directory."""
    out = str(tmp_path / "output")
    os.makedirs(out, exist_ok=True)
    return out
