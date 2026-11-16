"""Tests for bounded, local PDF text extraction."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.main import app
from app.pdf_extraction import MAX_PDF_SIZE, PDFExtractionError, extract_pdf_text


client = TestClient(app)


def make_text_pdf(text: str) -> bytes:
    """Build a tiny standards-compliant PDF without adding a test dependency."""

    safe_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 720 Td ({safe_text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode()
        + stream
        + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, pdf_object in enumerate(objects, 1):
        offsets.append(len(output))
        output += f"{number} 0 obj\n".encode() + pdf_object + b"\nendobj\n"
    xref_offset = len(output)
    output += f"xref\n0 {len(objects) + 1}\n".encode()
    output += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        output += f"{offset:010d} 00000 n \n".encode()
    output += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    ).encode()
    return bytes(output)


def make_blank_pdf(*, encrypted: bool = False) -> bytes:
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    if encrypted:
        writer.encrypt("secret")
    writer.write(output)
    return output.getvalue()


def test_valid_pdf_text_is_extracted() -> None:
    result = extract_pdf_text(make_text_pdf("WIN PRIZE NOW"))

    assert result.text == "WIN PRIZE NOW"
    assert result.page_count == 1


@pytest.mark.parametrize("data", [b"not a pdf", b"", b"PK\x03\x04archive"])
def test_invalid_pdf_signature_is_rejected(data: bytes) -> None:
    with pytest.raises(PDFExtractionError, match="valid PDF signature"):
        extract_pdf_text(data)


def test_textless_pdf_explains_that_ocr_is_required() -> None:
    with pytest.raises(PDFExtractionError, match="OCR is required"):
        extract_pdf_text(make_blank_pdf())


def test_encrypted_pdf_is_rejected_clearly() -> None:
    with pytest.raises(PDFExtractionError, match="encrypted"):
        extract_pdf_text(make_blank_pdf(encrypted=True))


def test_malformed_pdf_is_rejected_clearly() -> None:
    with pytest.raises(PDFExtractionError, match="malformed"):
        extract_pdf_text(b"%PDF-1.7\nthis is incomplete")


def test_pdf_upload_endpoint_returns_extracted_text() -> None:
    response = client.post(
        "/api/pdf/extract",
        files={"file": ("email.pdf", make_text_pdf("CLAIM REWARD NOW"), "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["extracted_text"] == "CLAIM REWARD NOW"
    assert response.json()["page_count"] == 1
    assert response.json()["character_count"] == len("CLAIM REWARD NOW")


def test_upload_rejects_non_pdf_extension_and_signature() -> None:
    wrong_extension = client.post(
        "/api/pdf/extract",
        files={"file": ("email.txt", b"plain text", "text/plain")},
    )
    wrong_signature = client.post(
        "/api/pdf/extract",
        files={"file": ("email.pdf", b"plain text", "application/pdf")},
    )

    assert wrong_extension.status_code == 415
    assert wrong_signature.status_code == 400
    assert "valid PDF signature" in wrong_signature.json()["detail"]


def test_upload_rejects_oversized_pdf() -> None:
    response = client.post(
        "/api/pdf/extract",
        files={
            "file": (
                "large.pdf",
                b"%PDF-1.7\n" + b"0" * MAX_PDF_SIZE,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413
