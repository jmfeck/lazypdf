import os

import lazypdf as lz


class TestExtractPages:
    def test_extract_pages(self, sample_pdf):
        pdf = lz.read(sample_pdf).extract_pages([1, 3])
        assert len(pdf) == 2
        pdf.close()

    def test_extract_single_page(self, sample_pdf):
        pdf = lz.read(sample_pdf).extract_pages([2])
        assert len(pdf) == 1
        pdf.close()


class TestRemovePages:
    def test_remove_pages(self, sample_pdf):
        pdf = lz.read(sample_pdf).remove_pages([2])
        assert len(pdf) == 2
        pdf.close()

    def test_remove_multiple(self, sample_pdf):
        pdf = lz.read(sample_pdf).remove_pages([1, 3])
        assert len(pdf) == 1
        pdf.close()


class TestReorder:
    def test_reorder(self, sample_pdf):
        pdf = lz.read(sample_pdf).reorder([3, 1, 2])
        assert len(pdf) == 3
        pdf.close()

    def test_reorder_duplicate(self, sample_pdf):
        pdf = lz.read(sample_pdf).reorder([1, 1, 2, 2])
        assert len(pdf) == 4
        pdf.close()


class TestReverse:
    def test_reverse(self, sample_pdf):
        pdf = lz.read(sample_pdf)
        text_first = pdf._doc[0].get_text()
        pdf.reverse()
        text_last = pdf._doc[2].get_text()
        assert text_first == text_last
        pdf.close()


class TestSplit:
    def test_split_every_page(self, sample_pdf, output_dir):
        pdf = lz.read(sample_pdf)
        paths = pdf.split(output_dir, every=1)
        assert len(paths) == 3
        for p in paths:
            assert os.path.exists(p)
        pdf.close()

    def test_split_every_2(self, sample_pdf, output_dir):
        pdf = lz.read(sample_pdf)
        paths = pdf.split(output_dir, every=2)
        assert len(paths) == 2
        pdf.close()

    def test_split_at(self, sample_pdf, output_dir):
        pdf = lz.read(sample_pdf)
        paths = pdf.split_at(output_dir, at=[2])
        assert len(paths) == 2
        pdf.close()
