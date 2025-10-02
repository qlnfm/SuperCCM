import onnxruntime
import numpy as np
import cv2
import os
from scipy.ndimage import label

STRUCTURE_4 = np.array([[0, 1, 0],
                        [1, 1, 1],
                        [0, 1, 0]])
STRUCTURE_8 = np.array([[1, 1, 1],
                        [1, 1, 1],
                        [1, 1, 1]])


def _split(image, split_skeleton=False):
    image = image > 0
    if not split_skeleton:
        arrays, num = label(image, structure=STRUCTURE_4)
    else:
        arrays, num = label(image, structure=STRUCTURE_8)

    segments = []
    for i in range(1, num + 1):
        component_image = np.where(arrays == i, 1, 0)
        component_image = component_image * 255
        component_image = component_image.astype('uint8')
        segments.append(component_image)

    return segments, num


class CornealNerveSegmenter:
    onnx_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ccm.onnx')
    # The smallest pixel size of the binarized segmented area is used for filtering.
    MIN_BINARY_AREA = 128
    # The smallest pixel size of the area located at the edge of the image after binarized segmentation, used for filtering.
    MIN_BINARY_EDGE_AREA = 32

    def __init__(self):
        self.sess_options = onnxruntime.SessionOptions()
        # If you want to use the GPU, please install onnxruntime-gpu and modify it as follows:
        # providers = ['CUDAExecutionProvider']
        self.ort_session = onnxruntime.InferenceSession(
            self.onnx_path, sess_options=self.sess_options, providers=['CPUExecutionProvider'])

    def seg(self, image: np.ndarray) -> np.ndarray:
        """
        Perform segmentation prediction on the input single image.
        """
        input_name = self.ort_session.get_inputs()[0].name
        output_name = self.ort_session.get_outputs()[0].name

        image_resized = cv2.resize(image, (384, 384))

        input_tensor = image_resized.astype(np.float32) / 255.0
        input_tensor = np.expand_dims(input_tensor, axis=0)  # 添加批次维度
        input_tensor = np.expand_dims(input_tensor, axis=0)  # 添加通道维度

        ort_inputs = {input_name: input_tensor}
        ort_outputs = self.ort_session.run([output_name], ort_inputs)

        output_data = ort_outputs[0]

        threshold = 0.5
        mask = (output_data > threshold).squeeze()
        mask = (mask * 255).astype(np.uint8)

        return mask

    def post_process(self, binary: np.ndarray) -> np.ndarray:
        min_area, min_edge_area = self.MIN_BINARY_AREA, self.MIN_BINARY_EDGE_AREA
        # Filter out noise
        if min_area > 0 or min_edge_area > 0:
            segments, _ = _split(binary, True)

            h, w = binary.shape
            edge_margin = 3  # How many pixels away from the edge is considered close to the edge

            for segment in segments:
                ys, xs = np.nonzero(segment)
                area = len(xs)

                # Whether it is within the edge range
                near_edge = (
                        np.any(xs < edge_margin) or np.any(xs >= w - edge_margin) or
                        np.any(ys < edge_margin) or np.any(ys >= h - edge_margin)
                )

                threshold = min_edge_area if near_edge else min_area

                if area < threshold:
                    binary[segment > 0] = 0  # Delete the areas that do not meet the area requirements

        return binary

    def __call__(self, image: np.ndarray, *, post_process=True) -> np.ndarray:
        binary = self.seg(image)
        if post_process:
            binary = self.post_process(binary)
        return binary
