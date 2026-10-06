import base64
from io import BytesIO

from PIL import Image, ImageDraw
from google import genai

from .config import Settings
from .resilience import retry_with_backoff


class ImageGenerationError(RuntimeError):
    """Raised when Gemini image generation fails."""


def _demo_image(prompt: str, aspect_ratio: str) -> bytes:
    """Create a local placeholder for UI testing without an API call."""
    dimensions = {
        "16:9": (900, 506),
        "1:1": (700, 700),
        "9:16": (506, 900),
    }

    width, height = dimensions.get(aspect_ratio, (700, 700))

    image = Image.new("RGB", (width, height), (225, 238, 247))
    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (20, 20, width - 20, height - 20),
        outline=(50, 80, 100),
        width=4,
    )

    draw.text((45, 55), "DEMO MODE", fill=(30, 55, 70))
    draw.text(
        (45, 100),
        "No Gemini API call was made.",
        fill=(40, 70, 85),
    )
    draw.text(
        (45, 150),
        prompt[:150],
        fill=(30, 55, 70),
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@retry_with_backoff()
def _generate_one(
    client,
    model: str,
    prompt: str,
    aspect_ratio: str,
    image_size: str,
    mime_type: str,
) -> bytes:
    try:
        interaction = client.interactions.create(
            model=model,
            input=prompt,
            response_format={
                "type": "image",
                "mime_type": mime_type,
                "aspect_ratio": aspect_ratio,
                "image_size": image_size,
            },
        )
    except Exception as exc:
        raise ImageGenerationError(
            f"Gemini API request failed: {exc}"
        ) from exc

    output_image = getattr(interaction, "output_image", None)

    if output_image is None:
        raise ImageGenerationError(
            "Gemini returned no output image. "
            "Check the model, API access, prompt, and quota."
        )

    image_data = getattr(output_image, "data", None)

    if not image_data:
        raise ImageGenerationError(
            "Gemini returned an empty image payload."
        )

    try:
        return base64.b64decode(image_data)
    except Exception as exc:
        raise ImageGenerationError(
            f"Could not decode Gemini image data: {exc}"
        ) from exc


def generate_images(
    prompt: str,
    model: str,
    aspect_ratio: str,
    image_size: str,
    count: int,
    mime_type: str,
    settings: Settings,
) -> list[dict]:
    if not 1 <= count <= 4:
        raise ImageGenerationError(
            "Generation count must be between 1 and 4."
        )

    if settings.demo_mode:
        return [
            {
                "bytes": _demo_image(
                    prompt,
                    aspect_ratio,
                )
            }
            for _ in range(count)
        ]

    if not settings.api_key:
        raise ImageGenerationError(
            "GEMINI_API_KEY is missing. "
            "Add it to .env or set DEMO_MODE=true."
        )

    try:
        client = genai.Client(api_key=settings.api_key)
    except Exception as exc:
        raise ImageGenerationError(
            f"Could not initialize Gemini client: {exc}"
        ) from exc

    results = []

    for _ in range(count):
        image_bytes = _generate_one(
            client=client,
            model=model,
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            mime_type=mime_type,
        )

        results.append({"bytes": image_bytes})

    return results
