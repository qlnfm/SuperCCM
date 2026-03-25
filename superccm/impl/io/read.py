import numpy as np
import cv2
from PIL import Image
from pathlib import Path


KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))


def _roi(gray_img):
    """ Get the actual area and size of the corneal nerve image in the image. """
    _, binary = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    if num_labels <= 1:
        return None, 0

    largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    x, y, w, h, area = stats[largest_label]

    mask = (labels == largest_label).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL)
    area = cv2.countNonZero(mask)

    roi = gray_img[y:y + h, x:x + w]
    mask = mask[y:y + h, x:x + w]
    return roi, mask, area


def read_image(
        any_input: str | Path | np.ndarray | bytes | Image.Image,
) -> tuple[np.ndarray, np.ndarray, int]:
    """
    Read a corneal nerve image and automatically crop it to the effective area.
    :param any_input: The input can be a file path, a URL, bytes, an image object in the OpenCV or PIL format.
    :return: ROI of image, mask of image, area of mask.
    """
    # filepath or URL
    if isinstance(any_input, (str, Path)):
        path = str(any_input)
        try:
            if path.startswith(("http://", "https://")):
                import requests
                resp = requests.get(path)
                resp.raise_for_status()
                buf = np.frombuffer(resp.content, np.uint8)
            else:
                with open(path, "rb") as f:
                    buf = np.frombuffer(f.read(), np.uint8)
            img = cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")
        except Exception as e:
            raise IOError(f"Unable to read image from {path}: {e}")

    # numpy.ndarray
    elif isinstance(any_input, np.ndarray):
        img = any_input
        # Don't repeat the conversion.
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # bytes
    elif isinstance(any_input, (bytes, bytearray)):
        buf = np.frombuffer(any_input, np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)

    # PIL.Image
    elif isinstance(any_input, Image.Image):
        img = np.array(any_input.convert("L"))

    else:
        raise TypeError(f"Unsupported input type: {type(any_input)}")

    if img is None or img.size == 0:
        raise IOError("Decoded image is empty or invalid.")

    # Reset the image to the preset size
    roi, mask, area = _roi(img)
    return roi, mask, int(area)
