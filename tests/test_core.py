import lazypdf as lz


class TestRead:
    def test_read_pdf(self, sample_pdf):
        pdf = lz.read(sample_pdf)
        assert len(pdf) == 3
        assert pdf.path == sample_pdf
        pdf.close()

    def test_read_pdf_alias(self, sample_pdf):
        pdf = lz.read_pdf(sample_pdf)
        assert len(pdf) == 3
        pdf.close()

    def test_context_manager(self, sample_pdf):
        with lz.read(sample_pdf) as pdf:
            assert len(pdf) == 3

    def test_repr(self, sample_pdf):
        pdf = lz.read(sample_pdf)
        assert "PDFFile" in repr(pdf)
        assert "3 pages" in repr(pdf)
        pdf.close()

    def test_copy(self, sample_pdf):
        pdf = lz.read(sample_pdf)
        copy = pdf.copy()
        assert len(copy) == 3
        pdf.remove_pages([1])
        assert len(pdf) == 2
        assert len(copy) == 3
        pdf.close()
        copy.close()

    def test_from_bytes(self, sample_pdf):
        with open(sample_pdf, "rb") as f:
            data = f.read()
        pdf = lz.from_bytes(data)
        assert len(pdf) == 3
        pdf.close()


class TestReadImages:
    def test_read_images(self, sample_image, output_dir):
        pdf = lz.read_images(sample_image)
        out = pdf.to_pdf(f"{output_dir}/from_image.pdf")
        assert len(pdf) == 1
        pdf.close()

        verify = lz.read(out)
        assert len(verify) == 1
        verify.close()

    def test_read_jpg_alias(self, sample_image, output_dir):
        pdf = lz.read_jpg(sample_image)
        assert len(pdf) == 1
        pdf.close()
