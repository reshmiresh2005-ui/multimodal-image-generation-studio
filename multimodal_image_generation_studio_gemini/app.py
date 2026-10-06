import streamlit as st
from dotenv import load_dotenv

from src.config import IMAGE_FORMATS, IMAGE_SIZES, load_settings
from src.gemini_image_generator import ImageGenerationError, generate_images
from src.presets import PRESETS, build_prompt
from src.storage import save_history, save_image
from src.validation import validate_image_bytes

load_dotenv()

st.set_page_config(
    page_title="Multimodal Image Generation Studio",
    page_icon="🎨",
    layout="wide",
)

settings = load_settings()

st.title("🎨 Multimodal Image Generation Studio")
st.caption("Generative AI Project 3 — Prompt → Image → Verify → Store")

with st.sidebar:
    st.header("Generation Controls")

    model = st.text_input(
        "Gemini image model",
        value=settings.image_model,
        help="Current default: gemini-3.1-flash-image",
    )

    aspect = st.selectbox(
        "Aspect ratio",
        options=list(IMAGE_SIZES.keys()),
        format_func=lambda x: f"{x} — {IMAGE_SIZES[x]}",
    )

    image_size = st.selectbox(
        "Image size",
        options=["1K", "2K", "4K"],
        index=0,
        help="Gemini 3.1 Flash Image supports 1K, 2K and 4K output.",
    )

    count = st.slider(
        "Generation count",
        min_value=1,
        max_value=4,
        value=1,
        help="The app makes one API request per selected image.",
    )

    preset_name = st.selectbox("Style preset", list(PRESETS.keys()))

    st.divider()
    st.write("**Runtime mode:**", "Demo" if settings.demo_mode else "Gemini API")
    st.write("**Storage:**", str(settings.output_dir))

st.markdown(
    """
    Enter a natural-language description. The app builds a structured prompt,
    sends it to Gemini's image-generation model, validates the returned image,
    saves the verified asset locally, and provides a download button.
    """
)

prompt = st.text_area(
    "Image prompt",
    height=150,
    placeholder="Example: A futuristic Kerala train station at sunrise, cinematic lighting...",
)

negative_prompt = st.text_input(
    "Optional negative guidance",
    placeholder="Example: blurry, low quality, distorted text",
)

generate = st.button(
    "✨ Generate Image(s)",
    type="primary",
    use_container_width=True,
)

if generate:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
        st.stop()

    final_prompt = build_prompt(
        prompt=prompt,
        preset_name=preset_name,
        negative_prompt=negative_prompt,
    )

    st.subheader("Prompt Payload")
    st.code(final_prompt, language="text")

    progress = st.progress(0, text="Preparing Gemini generation...")

    try:
        results = generate_images(
            prompt=final_prompt,
            model=model,
            aspect_ratio=IMAGE_SIZES[aspect],
            image_size=image_size,
            count=count,
            mime_type=IMAGE_FORMATS["JPEG"],
            settings=settings,
        )

        progress.progress(100, text="Generation completed.")
        st.success(f"Generated {len(results)} asset(s).")

        columns = st.columns(min(len(results), 2))

        for index, result in enumerate(results):
            image_bytes = result["bytes"]
            validation = validate_image_bytes(image_bytes)

            if not validation.valid:
                st.error(
                    f"Asset {index + 1} failed integrity validation: "
                    f"{validation.reason}"
                )
                continue

            saved_path = save_image(
                image_bytes=image_bytes,
                output_dir=settings.output_dir,
                extension=validation.extension,
            )

            save_history(
                history_file=settings.history_file,
                record={
                    "prompt": final_prompt,
                    "model": model,
                    "aspect_ratio": IMAGE_SIZES[aspect],
                    "image_size": image_size,
                    "preset": preset_name,
                    "file": str(saved_path),
                    "mime_type": validation.mime_type,
                    "width": validation.width,
                    "height": validation.height,
                },
            )

            with columns[index % len(columns)]:
                st.image(
                    image_bytes,
                    caption=f"Asset {index + 1}: {saved_path.name}",
                )

                st.download_button(
                    "⬇️ Download",
                    data=image_bytes,
                    file_name=saved_path.name,
                    mime=validation.mime_type,
                    key=f"download_{saved_path.name}",
                )

                st.caption(
                    f"{validation.width} × {validation.height} | "
                    f"{validation.mime_type} | "
                    f"{len(image_bytes):,} bytes"
                )

    except ImageGenerationError as exc:
        progress.empty()
        st.error(str(exc))
        st.info(
            "Check GEMINI_API_KEY, the Gemini image model, API access/quota, "
            "internet connection, and the selected image settings."
        )

    except Exception as exc:
        progress.empty()
        st.exception(exc)

st.divider()

with st.expander("📚 Training brief alignment"):
    st.markdown(
        """
        **Pipeline**

        1. Natural-language prompt
        2. Gemini image-generation API
        3. Resolution/aspect-ratio parameters
        4. Image data decoding
        5. Binary integrity verification
        6. Local asset storage
        7. Streamlit display and download
        """
    )
