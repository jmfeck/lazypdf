import os

import pytest

import lazypdf as lz


class TestExtractText:
    def test_extract_all(self, sample_pdf):
        text = lz.read(sample_pdf).extract_text()
        assert "Page 1" in text
        assert "Page 2" in text
        assert "Page 3" in text

    def test_extract_specific_pages(self, sample_pdf):
        text = lz.read(sample_pdf).extract_text(pages=[1])
        assert "Page 1" in text
        assert "Page 2" not in text


class TestMetadata:
    def test_metadata(self, sample_pdf):
        pdf = lz.read(sample_pdf)
        meta = pdf.metadata
        assert isinstance(meta, dict)
        pdf.close()


class TestPageInfo:
    def test_page_count(self, sample_pdf):
        assert lz.read(sample_pdf).page_count == 3

    def test_page_sizes(self, sample_pdf):
        sizes = lz.read(sample_pdf).page_sizes()
        assert len(sizes) == 3
        w, h = sizes[0]
        assert 590 < w < 600
        assert 840 < h < 845


class TestExtractTables:
    def test_extract_tables_empty(self, sample_pdf):
        tables = lz.read(sample_pdf).extract_tables()
        assert isinstance(tables, list)

    def test_extract_tables_specific_pages(self, sample_pdf):
        tables = lz.read(sample_pdf).extract_tables(pages=[1])
        assert isinstance(tables, list)

    def test_extract_tables_invalid_page(self, sample_pdf):
        with pytest.raises(ValueError, match="out of range"):
            lz.read(sample_pdf).extract_tables(pages=[10])


class TestExtractImages:
    def test_extract_images_with_image(self, sample_image, output_dir):
        pdf = lz.read_images(sample_image)
        pdf_path = f"{output_dir}/img.pdf"
        pdf.to_pdf(pdf_path)

        paths = lz.read(pdf_path).extract_images(f"{output_dir}/imgs")
        assert len(paths) >= 1
        for p in paths:
            assert os.path.exists(p)

    def test_extract_images_no_images(self, sample_pdf, output_dir):
        paths = lz.read(sample_pdf).extract_images(f"{output_dir}/empty")
        assert paths == []

    def test_extract_images_specific_pages(self, sample_image, output_dir):
        pdf = lz.read_images(sample_image, sample_image)
        pdf_path = f"{output_dir}/2imgs.pdf"
        pdf.to_pdf(pdf_path)

        paths = lz.read(pdf_path).extract_images(f"{output_dir}/p1", pages=[1])
        assert len(paths) >= 1


class TestOcr:
    @pytest.fixture
    def has_tesseract(self):
        import shutil

        if shutil.which("tesseract") is None:
            pytest.skip("Tesseract not installed")

    def test_ocr_import_error(self, sample_pdf, monkeypatch):
        """OCR raises ImportError when pytesseract is not available."""
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "pytesseract":
                raise ImportError("mocked")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        with pytest.raises(ImportError, match="lazypdf\\[ocr\\]"):
            lz.read(sample_pdf).ocr()

    def test_ocr_pages_validation(self, sample_pdf):
        """OCR validates page numbers before running."""
        with pytest.raises(ValueError, match="out of range"):
            lz.read(sample_pdf).ocr(pages=[10])


class TestVersion:
    def test_version_exists(self):
        assert hasattr(lz, "__version__")
        assert isinstance(lz.__version__, str)
        assert lz.__version__ == "0.2.0"
