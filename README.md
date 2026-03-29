# lazypdf

[![Tests](https://github.com/jmfeck/lazypdf/actions/workflows/tests.yml/badge.svg)](https://github.com/jmfeck/lazypdf/actions/workflows/tests.yml)
[![Python](https://img.shields.io/pypi/pyversions/lazypdf)](https://pypi.org/project/lazypdf/)
[![License](https://img.shields.io/github/license/jmfeck/lazypdf)](LICENSE)

Simple PDF manipulation and conversion for Python. Read a PDF, transform it, export to another format. That's it.

No complex pipelines, no bloated abstractions — just a clean, fluent API to merge, split, compress, watermark, convert, and more.

## Install

```bash
pip install lazypdf
```

Optional extras:

```bash
pip install lazypdf[ocr]       # OCR support (pytesseract + Pillow)
pip install lazypdf[office]    # DOCX/XLSX/PPTX export (python-docx, openpyxl, python-pptx)
pip install lazypdf[tables]    # Table extraction (pdfplumber)
pip install lazypdf[html]      # HTML to PDF (WeasyPrint)
pip install lazypdf[msoffice]  # MS Office COM automation on Windows (pywin32)
pip install lazypdf[all]       # Everything
```

## Quick Start

```python
import lazypdf as lz

# Read -> Transform -> Export
lz.read("input.pdf").rotate(90).compress().to_pdf("output.pdf")

# Merge multiple PDFs
lz.merge("file1.pdf", "file2.pdf", "file3.pdf").to_pdf("merged.pdf")

# Convert images to PDF
lz.read_images("scan1.jpg", "scan2.jpg").to_pdf("scans.pdf")

# Read Office documents (requires MS Office or LibreOffice)
lz.read_docx("report.docx").add_watermark("DRAFT").to_pdf("draft.pdf")
lz.read_xlsx("data.xlsx").to_png("output/")
lz.read_pptx("slides.pptx").extract_pages([1, 3]).to_pdf("summary.pdf")

# Extract specific pages
lz.read("big.pdf").extract_pages([1, 3, 5]).to_pdf("selected.pdf")

# Add watermark and page numbers
(
    lz.read("report.pdf")
    .add_watermark("CONFIDENTIAL", opacity=0.2)
    .add_page_numbers(position="bottom-center")
    .to_pdf("final.pdf")
)

# Export to images
lz.read("slides.pdf").to_png("output_dir/", dpi=300)

# Extract text
text = lz.read("document.pdf").extract_text()

# Encrypt / decrypt
lz.read("doc.pdf").encrypt("password").to_pdf("protected.pdf")
lz.read("protected.pdf").decrypt("password").to_pdf("unlocked.pdf")

# Redact sensitive text (case-sensitive, exact match)
lz.read("doc.pdf").redact("SECRET-123").to_pdf("redacted.pdf")

# Split into individual pages
lz.read("doc.pdf").split("output_dir/", every=1)

# Chain anything
(
    lz.read("input.pdf")
    .merge("extra.pdf")
    .remove_pages([2, 4])
    .rotate(90, pages=[1])
    .crop(left=50, right=50)
    .add_watermark("DRAFT")
    .compress()
    .to_pdf("result.pdf")
)
```

## API Reference

### Entry Points

| Function | Description | Dependency |
|----------|-------------|------------|
| `lz.read(path)` | Read a PDF file | pymupdf |
| `lz.read_pdf(path)` | Alias for `read()` | pymupdf |
| `lz.merge(*paths)` | Merge multiple PDFs | pymupdf |
| `lz.read_images(*paths)` | Create PDF from images | pymupdf |
| `lz.read_jpg(*paths)` | Create PDF from JPEGs | pymupdf |
| `lz.read_png(*paths)` | Create PDF from PNGs | pymupdf |
| `lz.read_html(path_or_url)` | Create PDF from HTML | weasyprint |
| `lz.read_docx(path)` | Read Word document | MS Office / LibreOffice |
| `lz.read_xlsx(path)` | Read Excel spreadsheet | MS Office / LibreOffice |
| `lz.read_pptx(path)` | Read PowerPoint presentation | MS Office / LibreOffice |
| `lz.read_csv(path)` | Read CSV file | MS Office / LibreOffice |
| `lz.from_bytes(data)` | Create PDF from raw bytes | pymupdf |

### Chainable Operations

| Method | Description |
|--------|-------------|
| `.merge(*others)` | Append more PDFs (paths, objects, or lists) |
| `.rotate(degrees, pages=)` | Rotate pages (multiple of 90) |
| `.crop(left=, top=, right=, bottom=, pages=)` | Crop page margins (in points) |
| `.compress()` | Reduce file size (deflate compression, dedup objects) |
| `.add_watermark(text, ...)` | Add text watermark |
| `.add_image_watermark(path, ...)` | Add image watermark (with opacity) |
| `.add_page_numbers(...)` | Insert page numbers |
| `.resize(size, pages=)` | Resize pages to standard paper size (a4, letter, etc.) |
| `.flatten(dpi=, pages=)` | Rasterize pages (burns annotations/forms into flat image) |
| `.extract_pages(pages)` | Keep only specified pages |
| `.remove_pages(pages)` | Remove specified pages |
| `.reorder(order)` | Reorder/duplicate pages |
| `.reverse()` | Reverse page order |
| `.encrypt(password)` | Add password protection (AES-256) |
| `.decrypt(password)` | Remove password protection |
| `.redact(text)` | Black out text permanently |
| `.repair()` | Fix corrupted PDFs |
| `.ocr(language=)` | Make scanned pages searchable |
| `.copy()` | Create independent copy |

All page parameters are **1-indexed** (first page = 1).

### Export (Terminal Operations)

| Method | Returns |
|--------|---------|
| `.to_pdf(path)` | `str` (output path) |
| `.to_jpg(output_dir)` | `list[str]` (image paths) |
| `.to_png(output_dir)` | `list[str]` (image paths) |
| `.to_images(output_dir, fmt=)` | `list[str]` (image paths) |
| `.to_docx(path)` | `str` (output path) |
| `.to_xlsx(path)` | `str` (output path) |
| `.to_pdfa(path, level=)` | `str` (output path, requires Ghostscript) |
| `.to_bytes()` | `bytes` |
| `.split(output_dir, every=)` | `list[str]` (PDF paths) |
| `.split_at(output_dir, at=)` | `list[str]` (PDF paths) |

### Extraction & Info

| Method / Property | Returns |
|----------|---------|
| `.extract_text(pages=)` | `str` |
| `.extract_tables(pages=)` | `list[list[list[str]]]` |
| `.extract_images(output_dir, pages=)` | `list[str]` (image paths) |
| `.metadata` | `dict` |
| `.page_count` | `int` |
| `.page_sizes()` | `list[tuple[float, float]]` |

## Limitations

- **Office reads** (`read_docx`, `read_xlsx`, `read_pptx`, `read_csv`) require either Microsoft Office (Windows, auto-detected) or LibreOffice (any OS, must be on PATH). No pure-Python solution exists for reliable Office-to-PDF conversion.
- **`to_docx()`** extracts text only. Images, tables, and complex formatting are not preserved.
- **`to_xlsx()`** only exports tables found in the PDF. Requires `[tables]` and `[office]` extras.
- **OCR** (`ocr()`) requires Tesseract to be installed on the system in addition to the `[ocr]` pip extra.
- **`read_html()`** requires WeasyPrint which has system-level dependencies (Pango, Cairo). See [WeasyPrint docs](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).
- **Redaction** (`redact()`) is case-sensitive exact text match. Save the result with `to_pdf()` to persist.
- **PDF/A** (`to_pdfa()`) requires Ghostscript installed on the system (`gs` on Linux/Mac, `gswin64c` on Windows).
- **Flatten** (`flatten()`) rasterizes pages to images — text becomes non-searchable. Use higher DPI for better quality.
- **Image watermark** (`add_image_watermark()`) requires Pillow (included in `[ocr]` extra).

## License

BSD-3-Clause
