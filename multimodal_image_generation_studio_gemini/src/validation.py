from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    reason: str
    extension: str = "png"
    mime_type: str = "image/png"
    width: int = 0
    height: int = 0


def validate_image_bytes(data: bytes) -> ValidationResult:
    if not data:
        return ValidationResult(False, "The image payload is empty.")

    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()

        with Image.open(BytesIO(data)) as image:
            image.load()

            fmt = (image.format or "").upper()

            mapping = {
                "PNG": ("png", "image/png"),
                "JPEG": ("jpg", "image/jpeg"),
                "JPG": ("jpg", "image/jpeg"),
                "WEBP": ("webp", "image/webp"),
            }

            if fmt not in mapping:
                return ValidationResult(
                    False,
                    f"Unsupported image format: {fmt or 'unknown'}",
                )

            extension, mime_type = mapping[fmt]

            return ValidationResult(
                True,
                "Image integrity verified.",
                extension=extension,
                mime_type=mime_type,
                width=image.width,
                height=image.height,
            )

    except (UnidentifiedImageError, OSError, ValueError) as exc:
        return ValidationResult(
            False,
            f"Corrupt or incomplete image: {exc}",
        )
