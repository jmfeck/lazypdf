import os
import shutil

import pytest

import lazypdf as lz


class TestImageWatermark:
    def test_add_image_watermark(self, sample_pdf, sample_image, output_dir):
        out = lz.read(sample_pdf).add_image_watermark(sample_image).to_pdf(f"{output_dir}/img_wm.pdf")
        assert os.path.exists(out)

    def test_add_image_watermark_specific_pages(self, sample_pdf, sample_image, output_dir):
        out = (
            lz.read(sample_pdf)
            .add_image_watermark(sample_image, pages=[1], opacity=0.3)
            .to_pdf(f"{output_dir}/img_wm_p1.pdf")
        )
        assert os.path.exists(out)

    def test_add_image_watermark_overlay(self, sample_pdf, sample_image, output_dir):
        out = (
            lz.read(sample_pdf)
            .add_image_watermark(sample_image, overlay=True)
            .to_pdf(f"{output_dir}/img_wm_overlay.pdf")
        )
        assert os.path.exists(out)


class TestResize:
    def test_resize_to_letter(self, sample_pdf):
        pdf = lz.read(sample_pdf).resize("letter")
        w, h = pdf.page_sizes()[0]
        assert abs(w - 612) < 1
        assert abs(h - 792) < 1
        pdf.close()

    def test_resize_to_a3(self, sample_pdf):
        pdf = lz.read(sample_pdf).resize("a3")
        w, h = pdf.page_sizes()[0]
        assert w > 800
        pdf.close()

    def test_resize_invalid(self, sample_pdf):
        with pytest.raises(ValueError, match="Unknown size"):
            lz.read(sample_pdf).resize("tabloid")

    def test_resize_specific_pages(self, sample_pdf):
        pdf = lz.read(sample_pdf).resize("letter", pages=[1])
        sizes = pdf.page_sizes()
        w1, _ = sizes[0]
        w2, _ = sizes[1]
        assert abs(w1 - 612) < 1
        assert abs(w2 - 595) < 1  # original A4 width
        pdf.close()

    def test_resize_chain(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).resize("letter").add_page_numbers().to_pdf(f"{output_dir}/resized.pdf")
        assert os.path.exists(out)


class TestCompress:
    def test_compress(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).compress().to_pdf(f"{output_dir}/compressed.pdf")
        assert os.path.exists(out)

    def test_compress_chain(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).rotate(90).compress().to_pdf(f"{output_dir}/rot_comp.pdf")
        assert os.path.exists(out)


class TestFlatten:
    def test_flatten_all(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).flatten().to_pdf(f"{output_dir}/flat.pdf")
        assert os.path.exists(out)
        pdf = lz.read(out)
        assert len(pdf) == 3
        pdf.close()

    def test_flatten_specific_pages(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).flatten(pages=[1, 3]).to_pdf(f"{output_dir}/flat_p.pdf")
        assert os.path.exists(out)
        pdf = lz.read(out)
        assert len(pdf) == 3
        pdf.close()

    def test_flatten_custom_dpi(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).flatten(dpi=72).to_pdf(f"{output_dir}/flat_72.pdf")
        assert os.path.exists(out)

    def test_flatten_chain(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).flatten().add_page_numbers().to_pdf(f"{output_dir}/flat_num.pdf")
        assert os.path.exists(out)


class TestExtractImages:
    def test_extract_from_pdf_with_image(self, sample_image, output_dir):
        # Create a PDF with an embedded image first
        pdf = lz.read_images(sample_image)
        pdf_path = f"{output_dir}/with_image.pdf"
        pdf.to_pdf(pdf_path)

        img_dir = f"{output_dir}/extracted"
        paths = lz.read(pdf_path).extract_images(img_dir)
        assert len(paths) >= 1
        for p in paths:
            assert os.path.exists(p)

    def test_extract_from_text_pdf(self, sample_pdf, output_dir):
        # Text-only PDF should return empty list
        paths = lz.read(sample_pdf).extract_images(f"{output_dir}/no_imgs")
        assert paths == []


has_ghostscript = (
    shutil.which("gs") is not None or shutil.which("gswin64c") is not None or shutil.which("gswin32c") is not None
)


class TestToPdfa:
    def test_to_pdfa(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).to_pdfa(f"{output_dir}/archive.pdf")
        assert os.path.exists(out)

    def test_to_pdfa_level3(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).to_pdfa(f"{output_dir}/archive3.pdf", level=3)
        assert os.path.exists(out)

    def test_to_pdfa_invalid_level(self, sample_pdf, output_dir):
        with pytest.raises(ValueError, match="PDF/A level must be"):
            lz.read(sample_pdf).to_pdfa(f"{output_dir}/bad.pdf", level=5)

    @pytest.mark.skipif(not has_ghostscript, reason="Ghostscript not installed")
    def test_to_pdfa_ghostscript(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).to_pdfa(f"{output_dir}/archive_gs.pdf", engine="ghostscript")
        assert os.path.exists(out)
