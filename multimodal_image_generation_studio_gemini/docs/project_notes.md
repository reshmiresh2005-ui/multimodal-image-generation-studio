# Project 3 — Gemini Implementation

## Requirement mapping

| Project requirement | Implementation |
|---|---|
| Natural language → artwork | Streamlit prompt + Gemini image model |
| Image-generation API | `src/gemini_image_generator.py` |
| Resolution | Gemini `image_size`: 1K/2K/4K |
| Aspect ratio | Gemini `response_format.aspect_ratio` |
| Generation count | Streamlit count slider |
| Binary image handling | Base64 decoding |
| Display | Streamlit `st.image()` |
| Download | Streamlit download button |
| Integrity verification | Pillow |
| Local storage | `data/generated/` |
| History | `data/history.json` |
| Retry/backoff | `src/resilience.py` |

## Official Gemini API flow

```text
Prompt
  ↓
Gemini 3.1 Flash Image
  ↓
Interactions API
  ↓
output_image.data
  ↓
Base64 decode
  ↓
Pillow validation
  ↓
Save
  ↓
Display + Download
```

The current Google documentation uses `gemini-3.1-flash-image` and the Interactions API for native image generation.
