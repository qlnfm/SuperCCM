import onnxruntime
import numpy as np
import cv2
import os

ONNX_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ccm.onnx')

def segment_an_ccm_image(image: np.ndarray) -> np.ndarray:
    """
    Load the ONNX model using ONNX Runtime and perform segmentation prediction on the input single image.
    """
    onnx_path = ONNX_PATH
    # 1. Create an ONNX Runtime session
    try:
        # CPU
        sess_options = onnxruntime.SessionOptions()
        # If you want to use the GPU, please install onnxruntime-gpu and modify it as follows:
        # providers = ['CUDAExecutionProvider']
        ort_session = onnxruntime.InferenceSession(onnx_path, sess_options=sess_options,
                                                   providers=['CPUExecutionProvider'])
    except Exception as e:
        raise RuntimeError(f"Unable to load the ONNX model '{onnx_path}': {e}")

    input_name = ort_session.get_inputs()[0].name
    output_name = ort_session.get_outputs()[0].name

    image_resized = cv2.resize(image, (384, 384))

    input_tensor = image_resized.astype(np.float32) / 255.0
    input_tensor = np.expand_dims(input_tensor, axis=0)  # 添加批次维度
    input_tensor = np.expand_dims(input_tensor, axis=0)  # 添加通道维度

    ort_inputs = {input_name: input_tensor}
    ort_outputs = ort_session.run([output_name], ort_inputs)

    output_data = ort_outputs[0]

    threshold = 0.5
    mask = (output_data > threshold).squeeze()
    mask = (mask * 255).astype(np.uint8)

    return mask



