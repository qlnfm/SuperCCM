import onnxruntime as ort
import numpy as np
import os

session = ort.InferenceSession(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ccm.onnx'))


def get_binary(image: np.ndarray) -> np.ndarray:
    assert len(image.shape) == 2

    h, w = image.shape
    pad_h = (32 - h % 32) % 32
    pad_w = (32 - w % 32) % 32

    if pad_h > 0 or pad_w > 0:
        image = np.pad(
            image,
            ((0, pad_h), (0, pad_w)),
            mode='constant',
            constant_values=0
        )

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    if np.max(image) > 1:
        image = image / 255.
    input_tensor = image.astype(np.float32)
    input_tensor = np.expand_dims(input_tensor, axis=0)
    input_tensor = np.expand_dims(input_tensor, axis=0)

    ort_inputs = {input_name: input_tensor}
    ort_outputs = session.run([output_name], ort_inputs)

    output_data = ort_outputs[0]

    threshold = 0.5
    mask = (output_data > threshold).squeeze()
    mask = (mask * 255).astype(np.uint8)

    mask = mask[:h, :w]
    return mask
