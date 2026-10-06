PRESETS = {
    "Cinematic": (
        "cinematic composition, dramatic lighting, rich atmosphere, "
        "detailed visual storytelling"
    ),
    "Cyberpunk": (
        "cyberpunk aesthetic, neon accents, futuristic architecture, "
        "high contrast"
    ),
    "Minimalism": (
        "minimalist composition, clean geometry, restrained palette, "
        "elegant negative space"
    ),
    "Photorealistic": (
        "photorealistic rendering, realistic materials, natural lighting, "
        "high detail"
    ),
    "Product Studio": (
        "premium commercial product photography, studio lighting, "
        "clean background, polished composition"
    ),
}


def build_prompt(prompt: str, preset_name: str, negative_prompt: str = "") -> str:
    style = PRESETS.get(preset_name, "")

    negative = ""
    if negative_prompt.strip():
        negative = (
            f" Avoid these unwanted characteristics: "
            f"{negative_prompt.strip()}."
        )

    return (
        f"Create an original image based on this description: "
        f"{prompt.strip()}. "
        f"Style direction: {style}.{negative}"
    )
