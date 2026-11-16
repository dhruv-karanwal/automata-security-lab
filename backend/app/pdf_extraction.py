"""Bounded, in-memory text extraction for user-supplied PDF files."""

from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


MAX_PDF_SIZE = 10 * 1024 * 1024


class PDFExtractionError(ValueError):
    """A PDF cannot be safely processed or has no selectable text."""


@dataclass(frozen=True)
class ExtractedPDF:
    text: str
    page_count: int


def validate_pdf_signature(data: bytes) -> None:
    """Require the standard PDF marker near the beginning of the file."""

    if not data[:1024].lstrip().startswith(b"%PDF-"):
        raise PDFExtractionError("The uploaded file does not have a valid PDF signature.")


def extract_pdf_text(data: bytes) -> ExtractedPDF:
    """Extract selectable text without writing the uploaded file to disk."""

    validate_pdf_signature(data)
    try:
        reader = PdfReader(BytesIO(data), strict=False)
        if reader.is_encrypted:
            raise PDFExtractionError(
                "The PDF is encrypted. Remove its password protection before uploading it."
            )
        page_text = [(page.extract_text() or "").strip() for page in reader.pages]
    except PDFExtractionError:
        raise
    except (PdfReadError, OSError, ValueError, TypeError) as error:
        raise PDFExtractionError(
            "The PDF is malformed or could not be read. Export the email as a new PDF and try again."
        ) from error

    text = "\n\n".join(part for part in page_text if part).strip()
    if not text:
        raise PDFExtractionError(
            "No selectable text was found. The PDF may be scanned or image-only; OCR is required and is not included in this project."
        )
    return ExtractedPDF(text=text, page_count=len(reader.pages))
