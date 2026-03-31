# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-31

### Added

- `compress()`: `img_quality` (1-100) and `compression_level` (1-9) parameters for granular compression control
- `encrypt()`: `algorithm` parameter with options `AES-256-R5`, `AES-256`, `AES-128`, `RC4-128`, `RC4-40`
- `extract_tables()`: `flavor` parameter (`lattice` for bordered tables, `stream` for borderless)
- `extract_text()`: `engine` parameter (`text`, `ocr`, `auto`) and `page_separator` with `{n}` placeholder
- `read_html()`: engine system — `pymupdf` (default, zero deps), `weasyprint`, `playwright`
- `repair()`: engine system — `pymupdf`, `pikepdf`, `auto` (default, tries each in order)
- `to_pdfa()`: engine system — `pymupdf` (default, zero deps), `ghostscript`
- Optional dependency extras: `lazypdf[browser]` (playwright), `lazypdf[repair]` (pikepdf)
- 47 new tests covering all v0.2.0 features

### Changed

- `flatten()`: default DPI lowered from 150 to 72 (smaller output files, matching original fitz behavior)
- `read_images()` / `read_jpg()` / `read_png()`: default `page_size` changed from `"a4"` to `"fit"` (preserves original image dimensions)
- `to_pdfa()`: default engine changed from `ghostscript` to `pymupdf` (zero external deps)

### Fixed

- `to_pdfa()`: Windows temp file locking error (`PermissionError` on cleanup)
- `extract_pages()` / `remove_pages()`: orphaned resources (fonts, images) no longer kept in output, reducing file bloat by up to 85%

## [0.1.1] - 2026-03-29

### Added

- Core `PDFFile` class with fluent read/chain/export API
- Entry points: `read`, `read_pdf`, `read_images`, `read_jpg`, `read_png`, `read_html`, `read_docx`, `read_xlsx`, `read_pptx`, `read_csv`, `merge`, `from_bytes`
- Page operations: `extract_pages`, `remove_pages`, `reorder`, `reverse`, `split`, `split_at`
- Transformations: `rotate`, `crop`, `compress`, `resize`, `flatten`, `repair`
- Watermarks: `add_watermark` (text), `add_image_watermark` (image)
- Page numbers: `add_page_numbers` with configurable position and format
- Security: `encrypt` (AES-256), `decrypt`, `redact`
- OCR: `ocr` with Tesseract integration
- Text extraction: `extract_text`, `extract_tables`, `extract_images`
- Export formats: `to_pdf`, `to_jpg`, `to_png`, `to_images`, `to_docx`, `to_xlsx`, `to_pdfa`, `to_bytes`
- Properties: `metadata`, `page_count`, `page_sizes`
- Office document conversion via MS Office COM (Windows) or LibreOffice (any OS)
- Context manager and `__del__` for automatic resource cleanup
- Comprehensive input validation with clear error messages
- 114 tests covering core operations, Office conversion, validations, and edge cases

## [0.1.0] - 2024-11-04

### Added

- Initial commit with LICENSE and README
