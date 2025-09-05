import gradio as gr
import pandas as pd
import cv2
from superccm import SuperCCM, draw


def analysis(image):
    ccm = SuperCCM()
    metrics = ccm.run(image)
    df = pd.DataFrame(metrics.items(), columns=['Parameter', 'Value'])
    ccm_obj = ccm.graph
    image_vis = cv2.cvtColor(draw(ccm_obj), cv2.COLOR_BGR2RGB)
    return df, ccm_obj, image_vis


def analysis_sample():
    image = cv2.imread('docs/assets/web/img.jpg')
    return analysis(image)


def vis(
        ccm_obj,
        color_main, color_side,
        skeleton_only,
        show_main_nerve, show_side_nerve,
        color_end, color_branch,
        show_end_node, show_branch_node,
        size_end, size_branch,
        canvas
):
    def hex_to_bgr(hex_color):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (b, g, r)

    config = {
        'main_edge_color': color_main,
        'side_edge_color': color_side,
        'edge_body': skeleton_only,
        'show_main_edge': show_main_nerve,
        'show_side_edge': show_side_nerve,
        'end_node_color': color_end,
        'branch_node_color': color_branch,
        'show_end_node': show_end_node,
        'show_branch_node': show_branch_node,
        'end_node_size': size_end,
        'branch_node_size': size_branch,
        'background': canvas,
    }
    kwargs = {}
    for k, v in config.items():
        if v in (0, 1):
            if k == 'edge_body':
                kwargs[k] = bool(v)
            else:
                kwargs[k] = bool(1 - v)
        elif isinstance(v, str) and v.startswith('#'):
            kwargs[k] = hex_to_bgr(v)
        elif isinstance(v, str) and v.startswith('rgba'):
            color = tuple(int(x) for x in eval(v[4:]))
            color = color[:3][::-1]
            kwargs[k] = color
        else:
            kwargs[k] = v

    return cv2.cvtColor(draw(ccm_obj, **kwargs), cv2.COLOR_BGR2RGB)


with gr.Blocks(
        title='SuperCCM Web Application',
) as demo:
    ccm_obj = gr.State()
    gr.HTML('<h1 align="center">SuperCCM Web Application</h1>')
    with gr.Row():
        gr.Column()
        # 输入
        with gr.Column(scale=2):
            with gr.Tab('Upload a CCM image here'):
                image_input = gr.Image(sources=['upload'])
                sample_button = gr.Button('Use a sample', variant='primary')
            with gr.Tab('Visual parameter Settings'):
                with gr.Row():
                    with gr.Row():
                        canvas = gr.Radio(choices=['image', 'empty'], value='image', type='value',
                                          label='Image background')
                        skeleton_only = gr.Radio(choices=['Yes', 'No'], value='No', type='index',
                                                 label='Only show nerve skeleton')
                        show_main_nerve = gr.Radio(choices=['Yes', 'No'], value='Yes', type='index',
                                                   label='Show main nerves')
                        show_side_nerve = gr.Radio(choices=['Yes', 'No'], value='Yes', type='index',
                                                   label='Show side nerves')
                        show_end_node = gr.Radio(choices=['Yes', 'No'], value='No', type='index',
                                                 label='Show end nodes')
                        show_branch_node = gr.Radio(choices=['Yes', 'No'], value='Yes', type='index',
                                                    label='Show branch nodes')
                    with gr.Row():
                        color_main = gr.ColorPicker(label='Main Nerves Color', value='#FF0000')
                        color_side = gr.ColorPicker(label='Side Nerves Color', value='#0000FF')
                        color_end = gr.ColorPicker(label='End Nodes Color', value='#00FFFF')
                        size_end = gr.Number(label='End Nodes Size', value=2)
                        color_branch = gr.ColorPicker(label='Branch Nodes Color', value='#00FF00')
                        size_branch = gr.Number(label='Branch Nodes Size', value=4)
        # 输出
        with gr.Column(scale=2):
            image_output = gr.Image(label='Visualization of analysis results')
            para_table = gr.Dataframe(label='Morphological parameters', headers=['Parameter', 'Value'])
        gr.Column()

    vis_inputs = [
        ccm_obj,
        color_main, color_side,
        skeleton_only,
        show_main_nerve, show_side_nerve,
        color_end, color_branch,
        show_end_node, show_branch_node,
        size_end, size_branch,
        canvas
    ]
    image_input.change(fn=analysis, inputs=[image_input], outputs=[para_table, ccm_obj, image_output])
    sample_button.click(fn=analysis_sample, outputs=[para_table, ccm_obj, image_output])
    for vis_comp in vis_inputs:
        vis_comp.change(fn=vis, inputs=vis_inputs, outputs=[image_output])

if __name__ == '__main__':
    demo.launch(show_api=False)
