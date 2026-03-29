import os

import lazypdf as lz


class TestMerge:
    def test_merge_two_pdfs(self, sample_pdf, sample_pdf_2, output_dir):
        pdf = lz.read(sample_pdf).merge(sample_pdf_2)
        assert len(pdf) == 5
        out = pdf.to_pdf(f"{output_dir}/merged.pdf")
        assert os.path.exists(out)
        pdf.close()

    def test_merge_function(self, sample_pdf, sample_pdf_2, output_dir):
        pdf = lz.merge(sample_pdf, sample_pdf_2)
        assert len(pdf) == 5
        pdf.close()

    def test_merge_multiple(self, sample_pdf, sample_pdf_2):
        pdf = lz.read(sample_pdf).merge(sample_pdf_2, sample_pdf_2)
        assert len(pdf) == 7
        pdf.close()

    def test_merge_list_of_paths(self, sample_pdf, sample_pdf_2):
        pdf = lz.read(sample_pdf).merge([sample_pdf_2, sample_pdf_2])
        assert len(pdf) == 7
        pdf.close()

    def test_merge_list_of_pdffiles(self, sample_pdf, sample_pdf_2):
        other1 = lz.read(sample_pdf_2)
        other2 = lz.read(sample_pdf_2)
        pdf = lz.read(sample_pdf).merge([other1, other2])
        assert len(pdf) == 7
        pdf.close()
        other1.close()
        other2.close()

    def test_merge_function_with_list(self, sample_pdf, sample_pdf_2):
        pdf = lz.merge([sample_pdf, sample_pdf_2])
        assert len(pdf) == 5
        pdf.close()

    def test_merge_mixed_args_and_list(self, sample_pdf, sample_pdf_2):
        pdf = lz.read(sample_pdf).merge(sample_pdf_2, [sample_pdf_2, sample_pdf_2])
        assert len(pdf) == 9
        pdf.close()


class TestRotate:
    def test_rotate_all(self, sample_pdf):
        pdf = lz.read(sample_pdf).rotate(90)
        for i in range(len(pdf)):
            assert pdf._doc[i].rotation == 90
        pdf.close()

    def test_rotate_specific_pages(self, sample_pdf):
        pdf = lz.read(sample_pdf).rotate(180, pages=[1, 3])
        assert pdf._doc[0].rotation == 180
        assert pdf._doc[1].rotation == 0
        assert pdf._doc[2].rotation == 180
        pdf.close()


class TestCrop:
    def test_crop_all(self, sample_pdf):
        pdf = lz.read(sample_pdf)
        original_width = pdf._doc[0].rect.width
        pdf.crop(left=50, right=50)
        assert pdf._doc[0].cropbox.width < original_width
        pdf.close()


class TestCompress:
    def test_compress_sets_opts(self, sample_pdf):
        pdf = lz.read(sample_pdf).compress()
        assert pdf._save_opts["deflate"] is True
        assert pdf._save_opts["garbage"] == 4
        pdf.close()


class TestWatermark:
    def test_add_watermark(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).add_watermark("DRAFT").to_pdf(f"{output_dir}/watermarked.pdf")
        assert os.path.exists(out)

    def test_watermark_specific_pages(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).add_watermark("SECRET", pages=[1]).to_pdf(f"{output_dir}/wm.pdf")
        assert os.path.exists(out)


class TestPageNumbers:
    def test_add_page_numbers(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).add_page_numbers().to_pdf(f"{output_dir}/numbered.pdf")
        assert os.path.exists(out)

    def test_page_numbers_custom(self, sample_pdf, output_dir):
        out = (
            lz.read(sample_pdf)
            .add_page_numbers(position="top-right", fmt="Page {n} of {total}")
            .to_pdf(f"{output_dir}/numbered2.pdf")
        )
        assert os.path.exists(out)


class TestRepair:
    def test_repair(self, sample_pdf):
        pdf = lz.read(sample_pdf).repair()
        assert len(pdf) == 3
        pdf.close()


class TestChaining:
    def test_chain_multiple_ops(self, sample_pdf, output_dir):
        out = (
            lz.read(sample_pdf)
            .rotate(90)
            .remove_pages([2])
            .add_watermark("TEST")
            .add_page_numbers()
            .compress()
            .to_pdf(f"{output_dir}/chained.pdf")
        )
        assert os.path.exists(out)
        verify = lz.read(out)
        assert len(verify) == 2
        verify.close()
