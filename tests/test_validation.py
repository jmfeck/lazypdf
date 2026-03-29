import pytest

import lazypdf as lz


class TestPageValidation:
    """Test that invalid page numbers raise clear errors."""

    def test_extract_pages_out_of_range(self, sample_pdf):
        with pytest.raises(ValueError, match="Page 10 is out of range"):
            lz.read(sample_pdf).extract_pages([10])

    def test_extract_pages_zero(self, sample_pdf):
        with pytest.raises(ValueError, match="Page 0 is out of range"):
            lz.read(sample_pdf).extract_pages([0])

    def test_extract_pages_negative(self, sample_pdf):
        with pytest.raises(ValueError, match="out of range"):
            lz.read(sample_pdf).extract_pages([-1])

    def test_extract_pages_empty(self, sample_pdf):
        with pytest.raises(ValueError, match="cannot be empty"):
            lz.read(sample_pdf).extract_pages([])

    def test_remove_pages_out_of_range(self, sample_pdf):
        with pytest.raises(ValueError, match="Page 5 is out of range"):
            lz.read(sample_pdf).remove_pages([5])

    def test_remove_all_pages(self, sample_pdf):
        with pytest.raises(ValueError, match="Cannot remove all pages"):
            lz.read(sample_pdf).remove_pages([1, 2, 3])

    def test_reorder_out_of_range(self, sample_pdf):
        with pytest.raises(ValueError, match="Page 4 is out of range"):
            lz.read(sample_pdf).reorder([1, 4])

    def test_rotate_invalid_degrees(self, sample_pdf):
        with pytest.raises(ValueError, match="multiple of 90"):
            lz.read(sample_pdf).rotate(45)

    def test_rotate_pages_out_of_range(self, sample_pdf):
        with pytest.raises(ValueError, match="Page 5 is out of range"):
            lz.read(sample_pdf).rotate(90, pages=[5])

    def test_crop_negative_values(self, sample_pdf):
        with pytest.raises(ValueError, match="'left' must be >= 0"):
            lz.read(sample_pdf).crop(left=-10)

    def test_crop_exceeds_page(self, sample_pdf):
        with pytest.raises(ValueError, match="exceed page dimensions"):
            lz.read(sample_pdf).crop(left=300, right=300)

    def test_watermark_empty_text(self, sample_pdf):
        with pytest.raises(ValueError, match="cannot be empty"):
            lz.read(sample_pdf).add_watermark("")

    def test_watermark_pages_out_of_range(self, sample_pdf):
        with pytest.raises(ValueError, match="Page 10 is out of range"):
            lz.read(sample_pdf).add_watermark("DRAFT", pages=[10])

    def test_page_numbers_invalid_position(self, sample_pdf):
        with pytest.raises(ValueError, match="Invalid position"):
            lz.read(sample_pdf).add_page_numbers(position="middle")

    def test_page_numbers_pages_out_of_range(self, sample_pdf):
        with pytest.raises(ValueError, match="Page 5 is out of range"):
            lz.read(sample_pdf).add_page_numbers(pages=[5])

    def test_redact_pages_out_of_range(self, sample_pdf):
        with pytest.raises(ValueError, match="Page 10 is out of range"):
            lz.read(sample_pdf).redact("text", pages=[10])

    def test_extract_text_pages_out_of_range(self, sample_pdf):
        with pytest.raises(ValueError, match="Page 10 is out of range"):
            lz.read(sample_pdf).extract_text(pages=[10])

    def test_to_images_pages_out_of_range(self, sample_pdf, output_dir):
        with pytest.raises(ValueError, match="Page 10 is out of range"):
            lz.read(sample_pdf).to_images(output_dir, pages=[10])

    def test_split_at_out_of_range(self, sample_pdf, output_dir):
        with pytest.raises(ValueError, match="Page 10 is out of range"):
            lz.read(sample_pdf).split_at(output_dir, at=[10])

    def test_split_every_zero(self, sample_pdf, output_dir):
        with pytest.raises(ValueError, match="'every' must be >= 1"):
            lz.read(sample_pdf).split(output_dir, every=0)

    def test_to_images_invalid_format(self, sample_pdf, output_dir):
        with pytest.raises(ValueError, match="Unsupported image format"):
            lz.read(sample_pdf).to_images(output_dir, fmt="gif")


class TestMergeErrors:
    def test_merge_function_one_file(self, sample_pdf):
        with pytest.raises(ValueError, match="at least 2"):
            lz.merge(sample_pdf)

    def test_merge_function_empty(self):
        with pytest.raises(ValueError, match="at least 2"):
            lz.merge()

    def test_merge_nonexistent_file(self, sample_pdf):
        import pymupdf

        with pytest.raises(pymupdf.FileNotFoundError):
            lz.read(sample_pdf).merge("nonexistent.pdf")


class TestEncryptionErrors:
    def test_decrypt_wrong_password(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).encrypt("correct").to_pdf(f"{output_dir}/enc.pdf")
        with pytest.raises(ValueError, match="Incorrect password"):
            lz.read(out).decrypt("wrong")


class TestResourceCleanup:
    def test_context_manager_exception(self, sample_pdf):
        try:
            with lz.read(sample_pdf) as pdf:
                raise RuntimeError("test error")
        except RuntimeError:
            pass
        assert pdf._doc.is_closed

    def test_close_idempotent(self, sample_pdf):
        pdf = lz.read(sample_pdf)
        pdf.close()
        pdf.close()  # should not raise

    def test_del_closes_doc(self, sample_pdf):
        pdf = lz.read(sample_pdf)
        doc = pdf._doc
        del pdf
        import gc

        gc.collect()
        assert doc.is_closed
