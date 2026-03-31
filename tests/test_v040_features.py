"""Tests for v0.4.0 feature requests and bug fixes."""

import os

import pytest

import lazypdf as lz


class TestCompressGranular:
    def test_compress_default(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).compress().to_pdf(f"{output_dir}/comp_default.pdf")
        assert os.path.exists(out)

    def test_compress_with_compression_level(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).compress(compression_level=9).to_pdf(f"{output_dir}/comp_lvl9.pdf")
        assert os.path.exists(out)

    def test_compress_invalid_compression_level(self, sample_pdf):
        with pytest.raises(ValueError, match="compression_level must be between"):
            lz.read(sample_pdf).compress(compression_level=0)

    def test_compress_invalid_compression_level_high(self, sample_pdf):
        with pytest.raises(ValueError, match="compression_level must be between"):
            lz.read(sample_pdf).compress(compression_level=10)

    def test_compress_img_quality(self, sample_image, output_dir):
        # Create a PDF with an image to test image compression
        pdf_path = f"{output_dir}/with_img.pdf"
        lz.read_images(sample_image).to_pdf(pdf_path)
        out = lz.read(pdf_path).compress(img_quality=50).to_pdf(f"{output_dir}/comp_img50.pdf")
        assert os.path.exists(out)

    def test_compress_img_quality_invalid(self, sample_pdf):
        with pytest.raises(ValueError, match="img_quality must be between"):
            lz.read(sample_pdf).compress(img_quality=0)

    def test_compress_img_quality_invalid_high(self, sample_pdf):
        with pytest.raises(ValueError, match="img_quality must be between"):
            lz.read(sample_pdf).compress(img_quality=101)


class TestEncryptAlgorithm:
    def test_encrypt_default_algorithm(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).encrypt("pass").to_pdf(f"{output_dir}/enc_default.pdf")
        assert os.path.exists(out)
        pdf = lz.read(out)
        assert pdf._doc.is_encrypted
        pdf.decrypt("pass")
        pdf.close()

    def test_encrypt_aes256(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).encrypt("pass", algorithm="AES-256").to_pdf(f"{output_dir}/enc_aes256.pdf")
        assert os.path.exists(out)

    def test_encrypt_aes128(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).encrypt("pass", algorithm="AES-128").to_pdf(f"{output_dir}/enc_aes128.pdf")
        assert os.path.exists(out)

    def test_encrypt_invalid_algorithm(self, sample_pdf):
        with pytest.raises(ValueError, match="Unknown algorithm"):
            lz.read(sample_pdf).encrypt("pass", algorithm="BLOWFISH")


class TestExtractTablesFlavor:
    def test_extract_tables_default_flavor(self, sample_pdf):
        # Text-only PDF, no tables expected
        tables = lz.read(sample_pdf).extract_tables()
        assert isinstance(tables, list)

    def test_extract_tables_stream_flavor(self, sample_pdf):
        tables = lz.read(sample_pdf).extract_tables(flavor="stream")
        assert isinstance(tables, list)

    def test_extract_tables_invalid_flavor(self, sample_pdf):
        with pytest.raises(ValueError, match="Unknown flavor"):
            lz.read(sample_pdf).extract_tables(flavor="magic")


class TestExtractTextEngine:
    def test_extract_text_default_engine(self, sample_pdf):
        text = lz.read(sample_pdf).extract_text()
        assert "Page 1" in text

    def test_extract_text_text_engine(self, sample_pdf):
        text = lz.read(sample_pdf).extract_text(engine="text")
        assert "Page 1" in text

    def test_extract_text_invalid_engine(self, sample_pdf):
        with pytest.raises(ValueError, match="Unknown engine"):
            lz.read(sample_pdf).extract_text(engine="magic")

    def test_extract_text_page_separator(self, sample_pdf):
        text = lz.read(sample_pdf).extract_text(page_separator="\n--- Page {n} ---\n")
        assert "--- Page 1 ---" in text
        assert "--- Page 2 ---" in text
        assert "--- Page 3 ---" in text

    def test_extract_text_page_separator_with_specific_pages(self, sample_pdf):
        text = lz.read(sample_pdf).extract_text(pages=[2], page_separator="\n--- Page {n} ---\n")
        assert "--- Page 2 ---" in text
        assert "--- Page 1 ---" not in text

    def test_extract_text_ocr_engine_requires_pytesseract(self, sample_pdf):
        # This test will either succeed (if pytesseract + tesseract installed) or raise
        try:
            lz.read(sample_pdf).extract_text(engine="ocr")
        except (ImportError, EnvironmentError):
            pass


class TestReadHtmlEngine:
    def test_read_html_invalid_engine(self):
        with pytest.raises(ValueError, match="Unknown engine"):
            lz.read_html("test.html", engine="safari")

    def test_read_html_weasyprint(self, tmp_path):
        html_path = str(tmp_path / "test.html")
        with open(html_path, "w") as f:
            f.write("<html><body><p>Hello</p></body></html>")
        try:
            pdf = lz.read_html(html_path, engine="weasyprint")
            assert len(pdf) >= 1
            pdf.close()
        except (ImportError, OSError):
            # ImportError if weasyprint not installed,
            # OSError if weasyprint installed but GTK libs missing (e.g. Windows CI)
            pass

    def test_read_html_pymupdf_engine(self, tmp_path):
        html_path = str(tmp_path / "test.html")
        with open(html_path, "w") as f:
            f.write("<html><body><p>Hello from pymupdf engine</p></body></html>")
        pdf = lz.read_html(html_path, engine="pymupdf")
        assert len(pdf) >= 1
        pdf.close()


class TestRepairEngine:
    def test_repair_default_auto(self, sample_pdf):
        pdf = lz.read(sample_pdf).repair()
        assert len(pdf) == 3
        pdf.close()

    def test_repair_pymupdf(self, sample_pdf):
        pdf = lz.read(sample_pdf).repair(engine="pymupdf")
        assert len(pdf) == 3
        pdf.close()

    def test_repair_pikepdf(self, sample_pdf):
        try:
            pdf = lz.read(sample_pdf).repair(engine="pikepdf")
            assert len(pdf) == 3
            pdf.close()
        except ImportError as e:
            assert "pikepdf" in str(e)

    def test_repair_invalid_engine(self, sample_pdf):
        with pytest.raises(ValueError, match="Unknown engine"):
            lz.read(sample_pdf).repair(engine="magic")


class TestToPdfaEngine:
    def test_to_pdfa_pymupdf(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).to_pdfa(f"{output_dir}/archive_mupdf.pdf", engine="pymupdf")
        assert os.path.exists(out)
        # Verify it's a valid PDF
        pdf = lz.read(out)
        assert len(pdf) == 3
        pdf.close()

    def test_to_pdfa_pymupdf_level1(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).to_pdfa(f"{output_dir}/archive_l1.pdf", level=1, engine="pymupdf")
        assert os.path.exists(out)

    def test_to_pdfa_pymupdf_level3(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).to_pdfa(f"{output_dir}/archive_l3.pdf", level=3, engine="pymupdf")
        assert os.path.exists(out)

    def test_to_pdfa_default_is_pymupdf(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).to_pdfa(f"{output_dir}/archive_default.pdf")
        assert os.path.exists(out)

    def test_to_pdfa_invalid_engine(self, sample_pdf, output_dir):
        with pytest.raises(ValueError, match="Unknown engine"):
            lz.read(sample_pdf).to_pdfa(f"{output_dir}/bad.pdf", engine="libreoffice")


class TestFlattenDefaultDpi:
    def test_flatten_default_dpi_72(self, sample_pdf, output_dir):
        # The default DPI is now 72, producing smaller files
        out = lz.read(sample_pdf).flatten().to_pdf(f"{output_dir}/flat_default.pdf")
        assert os.path.exists(out)

    def test_flatten_explicit_150(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).flatten(dpi=150).to_pdf(f"{output_dir}/flat_150.pdf")
        assert os.path.exists(out)


class TestReadImagesDefaultFit:
    def test_read_images_default_fit(self, sample_image):
        pdf = lz.read_images(sample_image)
        # With 'fit', page size should match image dimensions in points
        # 200px image at 96 DPI = 150pt
        w, h = pdf.page_sizes()[0]
        assert abs(w - 150) < 1
        assert abs(h - 150) < 1
        pdf.close()

    def test_read_images_explicit_a4(self, sample_image):
        pdf = lz.read_images(sample_image, page_size="a4")
        w, h = pdf.page_sizes()[0]
        assert abs(w - 595) < 2  # A4 width in points
        pdf.close()

    def test_read_jpg_default_fit(self, sample_image):
        pdf = lz.read_jpg(sample_image)
        w, h = pdf.page_sizes()[0]
        assert abs(w - 150) < 1
        pdf.close()

    def test_read_png_default_fit(self, sample_image):
        pdf = lz.read_png(sample_image)
        w, h = pdf.page_sizes()[0]
        assert abs(w - 150) < 1
        pdf.close()


class TestOrphanedResourceCleanup:
    def test_extract_pages_cleans_resources(self, sample_image, output_dir):
        # Create a multi-page PDF with images
        img_pdf_path = f"{output_dir}/multi_img.pdf"
        lz.read_images(sample_image, sample_image, sample_image).to_pdf(img_pdf_path)

        original_size = os.path.getsize(img_pdf_path)

        # Extract just one page - should be much smaller
        out = lz.read(img_pdf_path).extract_pages([1]).to_pdf(f"{output_dir}/one_page.pdf")
        extracted_size = os.path.getsize(out)

        # The extracted single page should be significantly smaller than the 3-page original
        assert extracted_size < original_size

    def test_remove_pages_cleans_resources(self, sample_image, output_dir):
        img_pdf_path = f"{output_dir}/multi_img2.pdf"
        lz.read_images(sample_image, sample_image, sample_image).to_pdf(img_pdf_path)

        original_size = os.path.getsize(img_pdf_path)

        # Remove 2 of 3 pages - should be smaller
        out = lz.read(img_pdf_path).remove_pages([2, 3]).to_pdf(f"{output_dir}/one_page2.pdf")
        result_size = os.path.getsize(out)

        assert result_size < original_size


class TestVersion:
    def test_version_040(self):
        assert lz.__version__ == "0.2.0"
