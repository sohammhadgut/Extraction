import cv2
import numpy as np
import os


def _enhance(gray):
    """CLAHE contrast enhancement — helps with faint handwriting."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def preprocess_image(image_path):
    """
    Multi-strategy preprocessing for handwritten diagram images.
    Saves preprocessed image and returns its path.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read: {image_path}")

    # Upscale — EasyOCR accuracy improves significantly on larger images
    h, w = image.shape[:2]
    scale = 2.5 if max(h, w) < 1000 else 1.5
    image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray     = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    enhanced = _enhance(gray)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced, h=12, templateWindowSize=7, searchWindowSize=21)

    # Adaptive threshold — handles uneven lighting and pencil/pen variation
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=15, C=4
    )

    # Morphological closing — joins broken letter strokes
    kernel  = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    out_path = "uploads/processed.png"
    os.makedirs("uploads", exist_ok=True)
    cv2.imwrite(out_path, cleaned)
    return out_path
