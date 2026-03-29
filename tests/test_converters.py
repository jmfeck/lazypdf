import os

import lazypdf as lz


class TestToPdf:
    def test_save_pdf(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).to_pdf(f"{output_dir}/output.pdf")
        assert os.path.exists(out)
        assert out == f"{output_dir}/output.pdf"

    def test_save_creates_dirs(self, sample_pdf, tmp_path):
        out = lz.read(sample_pdf).to_pdf(f"{tmp_path}/nested/dir/output.pdf")
        assert os.path.exists(out)


class TestToImages:
    def test_to_png(self, sample_pdf, output_dir):
        paths = lz.read(sample_pdf).to_png(output_dir)
        assert len(paths) == 3
        for p in paths:
            assert os.path.exists(p)
            assert p.endswith(".png")

    def test_to_jpg(self, sample_pdf, output_dir):
        paths = lz.read(sample_pdf).to_jpg(output_dir)
        assert len(paths) == 3
        for p in paths:
            assert p.endswith(".jpg")

    def test_to_images_specific_pages(self, sample_pdf, output_dir):
        paths = lz.read(sample_pdf).to_images(output_dir, fmt="png", pages=[1, 3])
        assert len(paths) == 2

    def test_to_images_custom_dpi(self, sample_pdf, output_dir):
        paths = lz.read(sample_pdf).to_images(output_dir, fmt="png", dpi=72)
        assert len(paths) == 3


class TestToBytes:
    def test_to_bytes(self, sample_pdf):
        data = lz.read(sample_pdf).to_bytes()
        assert isinstance(data, bytes)
        assert len(data) > 0
        assert data[:5] == b"%PDF-"
