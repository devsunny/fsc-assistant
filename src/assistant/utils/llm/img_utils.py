"""
Utilities to send an image file to an LLM and automatically resize/compress
it if it exceeds a specified byte size limit.

Prerequisites:
- pip install pillow openai
"""

import base64
import io
import logging
from pathlib import Path
from typing import Tuple, Union

from openai import OpenAI
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def _image_to_data_url(
    img: Image.Image, fmt: str = "WEBP", quality: int = 85
) -> Tuple[str, int]:
    """
    Convert PIL image to a data URL with specified format and quality.
    Returns (data_url, byte_size).
    """
    buf = io.BytesIO()
    save_kwargs = {"quality": quality}
    # WebP supports alpha; JPEG does not. If JPEG requested and image has alpha, flatten to white.
    out_img = img
    if fmt.upper() == "JPEG":
        if img.mode in ("RGBA", "LA"):
            out_img = Image.new("RGB", img.size, (255, 255, 255))
            out_img.paste(img, mask=img.split()[-1])
        else:
            out_img = img.convert("RGB")
    out_img.save(buf, format=fmt, **save_kwargs)
    data = buf.getvalue()
    mime = {
        "WEBP": "image/webp",
        "JPEG": "image/jpeg",
        "PNG": "image/png",
    }.get(fmt.upper(), f"image/{fmt.lower()}")
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}", len(data)


def _downscale_and_compress_to_limit(
    img: Image.Image, max_bytes: int, preferred_fmt: str = "WEBP"
) -> str:
    """
    Iteratively reduce quality and scale until the encoded image is <= max_bytes.
    Returns a data URL of the final image.
    """
    # Start with a reasonable quality and no scaling
    quality = 85
    scale = 1.0
    min_quality = 50
    min_scale = 0.3
    # If image is huge, pre-limit max side to speed up
    MAX_INITIAL_SIDE = 4096
    w, h = img.size
    max_side = max(w, h)
    if max_side > MAX_INITIAL_SIDE:
        scale0 = MAX_INITIAL_SIDE / max_side
        new_size = (max(1, int(w * scale0)), max(1, int(h * scale0)))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        w, h = img.size

    # Try preferred format first (WEBP gives best size while keeping alpha)
    current_fmt = preferred_fmt

    # First attempt with current settings
    data_url, size = _image_to_data_url(img, fmt=current_fmt, quality=quality)
    if size <= max_bytes:
        return data_url

    # Reduce quality first down to min_quality, then start scaling.
    while True:
        if size > max_bytes and quality > min_quality:
            quality = max(min_quality, quality - 5)
        elif size > max_bytes and scale > min_scale:
            scale = max(min_scale, scale * 0.90)
            new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
            img_scaled = img.resize(new_size, Image.Resampling.LANCZOS)
            data_url, size = _image_to_data_url(
                img_scaled, fmt=current_fmt, quality=quality
            )
            if size <= max_bytes:
                return data_url
            # Continue loop with scaled image becoming baseline
            img = img_scaled
            w, h = img.size
            continue
        else:
            # As a last attempt, try switching to JPEG if not already (can be smaller without alpha)
            if current_fmt != "JPEG":
                current_fmt = "JPEG"
                quality = min(quality, 85)  # reset quality ceiling reasonably
                data_url, size = _image_to_data_url(
                    img, fmt=current_fmt, quality=quality
                )
                if size <= max_bytes:
                    return data_url
                # Try the loop again with JPEG
                continue
            # Could not reduce under limit; return the smallest achieved
            return data_url

        # Re-encode with updated quality
        data_url, size = _image_to_data_url(img, fmt=current_fmt, quality=quality)
        if size <= max_bytes:
            return data_url


def _file_to_data_url_with_limit(image_path: str, max_bytes: int) -> str:
    """
    Open image from disk, and produce a data URL that is <= max_bytes,
    using downscaling/compression as needed.
    """
    with Image.open(image_path) as img:
        img = ImageOps.exif_transpose(img)  # respect EXIF orientation
        # Prefer WEBP for size efficiency; will fall back to JPEG if needed
        return _downscale_and_compress_to_limit(img, max_bytes, preferred_fmt="WEBP")


def to_multipart_message_content(
    image_path: Union[Path, str],
    *image_paths: Union[Path, str],
    max_bytes: int = 4 * 1024 * 1024,
) -> list:
    """
    Create a message content list with text prompt and one or more images as data URLs.
    Each image is resized/compressed to be <= max_bytes.
    """
    contents = []
    for img_path in (image_path,) + image_paths:
        data_url = _file_to_data_url_with_limit(str(img_path), max_bytes)
        contents.append({"type": "image_url", "image_url": {"url": data_url}})
    return contents


def to_multipart_message(
    prompt: str,
    image_path: Union[Path, str],
    *image_paths: Union[Path, str],
    max_bytes: int = 4 * 1024 * 1024,
) -> list:
    """
    Create a message content list with text prompt and one or more images as data URLs.
    Each image is resized/compressed to be <= max_bytes.
    """
    contents = [{"type": "text", "text": prompt}] if prompt else []
    for img_path in (image_path,) + image_paths:
        data_url = _file_to_data_url_with_limit(str(img_path), max_bytes)
        contents.append({"type": "image_url", "image_url": {"url": data_url}})
    return {
        "role": "user",
        "content": contents,
    }
