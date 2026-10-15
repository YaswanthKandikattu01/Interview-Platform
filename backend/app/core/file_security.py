import io
import os
import re
import uuid
import hashlib
import zipfile
from typing import Tuple, Optional
from fastapi import HTTPException, UploadFile, status
from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def sanitize_filename(filename: str) -> str:
    """Sanitize original filename to remove path traversal, null bytes, and illegal chars."""
    basename = os.path.basename(filename)
    # Remove any non-alphanumeric chars except dots, dashes, underscores
    clean_name = re.sub(r"[^a-zA-Z0-9._-]", "_", basename)
    return clean_name[:100]  # Limit length


def validate_file_magic_bytes(content: bytes, ext: str) -> str:
    """
    Validate that the file header matches its claimed extension.
    Returns the validated MIME type or raises HTTPException.
    """
    if ext == ".pdf":
        # PDF magic bytes: '%PDF-' (\x25\x50\x44\x46\x2D)
        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content does not match a valid PDF structure (invalid magic bytes)."
            )
        return "application/pdf"

    elif ext == ".docx":
        # DOCX is a zip archive starting with PK\x03\x04
        if not content.startswith(b"PK\x03\x04"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content does not match a valid DOCX document (missing ZIP header)."
            )
        # Verify internal DOCX structure: must contain '[Content_Types].xml' or 'word/document.xml'
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                namelist = zf.namelist()
                if not any(f.startswith("word/") or f == "[Content_Types].xml" for f in namelist):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid DOCX package structure."
                    )
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrupt DOCX file format."
            )
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file format. Only PDF and DOCX are permitted."
    )


async def process_and_store_upload(
    file: UploadFile,
    user_id: Optional[str] = None,
    file_purpose: str = "RESUME",  # 'RESUME' or 'JOB_DESCRIPTION'
) -> Tuple[str, str, str, int, str, str]:
    """
    Reads, validates, calculates checksum, and securely saves an uploaded file.
    Returns: (sanitized_name, storage_path, mime_type, file_size, checksum, original_name)
    """
    original_name = file.filename or "uploaded_file"
    ext = os.path.splitext(original_name)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{ext}'. Only .pdf and .docx files are permitted."
        )

    # Read content with strict size enforcement
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if file_size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File exceeds the 5 MB limit (size: {file_size / (1024 * 1024):.2f} MB)."
        )

    # Validate Magic Bytes & Internal Structure
    mime_type = validate_file_magic_bytes(content, ext)

    # Compute SHA-256 Checksum
    checksum = hashlib.sha256(content).hexdigest()

    # Generate secure isolated storage location
    sanitized_name = sanitize_filename(original_name)
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, user_id or "guest")
    os.makedirs(user_upload_dir, exist_ok=True)

    random_filename = f"{uuid.uuid4().hex}{ext}"
    storage_path = os.path.join(user_upload_dir, random_filename)

    with open(storage_path, "wb") as f:
        f.write(content)

    return sanitized_name, storage_path, mime_type, file_size, checksum, original_name
