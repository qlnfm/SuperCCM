from .base import BaseModule

import numpy as np
import cv2
from PIL import Image
from pathlib import Path
from typing import Literal

_flags = {
    'gray': cv2.IMREAD_GRAYSCALE,
    'color': cv2.IMREAD_COLOR
}

CCM_IMAGE_SHAPE = (384, 384)


def _read_image(
        any_input: str | Path | np.ndarray | bytes | Image.Image,
        image_type: Literal["gray", "color"] = "gray",
) -> np.ndarray:
    """
    Try to be as compatible as possible with the input,
    and directly read it as an OpenCV image (numpy.ndarray) by using the 'image_type'.

    :param:
        any_input: str | Path | np.ndarray | bytes | PIL.Image.Image
        image_type: 'color' (BGR) or 'gray'

    :return:
        np.ndarray: OpenCV format image
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
            img = cv2.imdecode(buf, _flags[image_type])
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")
        except Exception as e:
            raise IOError(f"Unable to read image from {path}: {e}")

    # numpy.ndarray
    elif isinstance(any_input, np.ndarray):
        img = any_input
        # Don't repeat the conversion.
        if image_type == "gray" and img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif image_type == "color" and img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # bytes
    elif isinstance(any_input, (bytes, bytearray)):
        buf = np.frombuffer(any_input, np.uint8)
        img = cv2.imdecode(buf, _flags[image_type])

    # PIL.Image
    elif isinstance(any_input, Image.Image):
        if image_type == "gray":
            img = np.array(any_input.convert("L"))
        else:
            img = cv2.cvtColor(np.array(any_input.convert("RGB")), cv2.COLOR_RGB2BGR)

    else:
        raise TypeError(f"Unsupported input type: {type(any_input)}")

    if img is None or img.size == 0:
        raise IOError("Decoded image is empty or invalid.")

    height, width = CCM_IMAGE_SHAPE
    img = img[:height, :width]

    return img


class ReadImageModule(BaseModule):
    """
    A module for reading images, supporting multiple input types (file paths, URLs, numpy arrays, PIL images, etc.),
    and finally returning in the numpy array format of OpenCV.
    """

    def __init__(self):
        super().__init__()
        self.name = 'read'
        self.output_name = 'raw_image'

    def __call__(self, *args, **kwargs) -> np.ndarray:
        if not args:
            raise ValueError("An input is required.")
        return _read_image(*args, **kwargs)
