from io import BytesIO

from PIL import Image

from src.validation import validate_image_bytes


def test_valid_png():
    image = Image.new("RGB", (32, 24), "white")

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    result = validate_image_bytes(buffer.getvalue())

    assert result.valid is True
    assert result.extension == "png"
    assert result.width == 32
    assert result.height == 24


def test_empty_image():
    result = validate_image_bytes(b"")

    assert result.valid is False


def test_corrupt_image():
    result = validate_image_bytes(b"not-an-image")

    assert result.valid is False
