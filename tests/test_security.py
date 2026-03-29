import os

import lazypdf as lz


class TestEncrypt:
    def test_encrypt_pdf(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).encrypt("mypassword").to_pdf(f"{output_dir}/encrypted.pdf")
        assert os.path.exists(out)

        pdf = lz.read(out)
        assert pdf._doc.is_encrypted
        pdf.decrypt("mypassword")
        assert len(pdf) == 3
        pdf.close()


class TestDecrypt:
    def test_decrypt_pdf(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).encrypt("pass123").to_pdf(f"{output_dir}/enc.pdf")
        pdf = lz.read(out).decrypt("pass123")
        assert len(pdf) == 3
        pdf.close()


class TestRedact:
    def test_redact_text(self, sample_pdf, output_dir):
        out = lz.read(sample_pdf).redact("Page 1").to_pdf(f"{output_dir}/redacted.pdf")
        assert os.path.exists(out)
        pdf = lz.read(out)
        text = pdf.extract_text(pages=[1])
        assert "Page 1" not in text
        pdf.close()
