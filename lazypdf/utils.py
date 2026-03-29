from __future__ import annotations


def validate_pages(pages: list[int], total: int) -> list[int]:
    """Validate a list of 1-indexed page numbers against the document length.

    Args:
        pages: List of 1-indexed page numbers.
        total: Total number of pages in the document.

    Returns:
        The validated list (unchanged).

    Raises:
        ValueError: If any page number is out of range.
    """
    if not pages:
        raise ValueError("Page list cannot be empty.")
    for p in pages:
        if not isinstance(p, int):
            raise TypeError(f"Page numbers must be integers, got {type(p).__name__}.")
        if p < 1 or p > total:
            raise ValueError(f"Page {p} is out of range. Document has {total} pages (1-{total}).")
    return pages


def resolve_pages(pages: list[int] | None, total: int) -> range | list[int]:
    """Resolve an optional pages parameter to 0-indexed indices.

    If pages is None, returns range(total) (all pages).
    Otherwise validates and converts to 0-indexed.

    Args:
        pages: Optional list of 1-indexed page numbers, or None for all.
        total: Total number of pages in the document.

    Returns:
        range or list of 0-indexed page indices.
    """
    if pages is None:
        return range(total)
    validate_pages(pages, total)
    return [p - 1 for p in pages]
