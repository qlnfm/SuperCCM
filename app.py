import gradio as gr
import cv2
import numpy as np

import superccm
from superccm.api import analysis_and_vis


def gradio_interface(gray_image):
    gray_cv = cv2.cvtColor(np.array(gray_image), cv2.COLOR_RGB2GRAY)

    info, color_result = analysis_and_vis(gray_cv)

    color_display = cv2.cvtColor(color_result, cv2.COLOR_BGR2RGB)

    return color_display, info


demo = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Image(label="Upload an image", type="pil"),
    ],
    outputs=[
        gr.Image(label="ACCMetrics Style Result"),
        gr.JSON(label="Metrics")
    ],
    title="SuperCCM Web",
    description=f"Backend Version: {superccm.__version__}"
)

if __name__ == "__main__":
    demo.launch()
