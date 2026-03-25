import os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import cv2
import pandas as pd
import gradio as gr
import webview

from superccm.api import analysis_and_vis
from superccm.api import read


def refresh_image(img):
    return read(img)[0]


class SuperCCMApp:
    """
    GUI 应用程序逻辑类，用于管理所有 UI 状态与事件绑定
    """

    def __init__(self):
        self.stop_flag = False
        self.batch_result_df = pd.DataFrame()
        self.SUPPORTED_EXTS = ('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.webp')

    # ==========================
    # Tkinter 弹窗交互方法
    # ==========================
    def _get_tkinter_root(self):
        """初始化隐藏的 Tkinter Root 窗口，避免 GUI 冲突"""
        root = tk.Tk()
        root.attributes('-topmost', True)  # 确保对话框在最前
        root.withdraw()  # 隐藏主窗口
        return root

    def select_directory(self) -> str:
        root = self._get_tkinter_root()
        path = filedialog.askdirectory(master=root, title="Please select a folder.")
        root.destroy()
        return path if path else ""

    def save_file_dialog(self, ext_name: str, ext_pattern: str) -> str:
        root = self._get_tkinter_root()
        path = filedialog.asksaveasfilename(
            master=root,
            defaultextension=ext_pattern,
            filetypes=[(ext_name, f"*{ext_pattern}")],
            title=f"Save as {ext_name}"
        )
        root.destroy()
        return path if path else ""

    # ==========================
    # Gradio 事件回调方法
    # ==========================
    def on_analyze_single(self, image, um: float, px: float):
        if image is None:
            return None, {"Tip": "Please upload the image first."}

        um_per_px = um / px if px else 1.0
        metrics, proc_img = analysis_and_vis(image, um_per_px)

        # 将处理完的 BGR 图像转回 RGB，以便 Gradio 正常渲染色彩
        proc_img_rgb = cv2.cvtColor(proc_img, cv2.COLOR_BGR2RGB)
        return proc_img_rgb, metrics

    import os

    def on_select_input_dir(self):
        path = self.select_directory()
        if not path:
            return gr.update(), gr.update()

        supported_exts = {ext.lower() for ext in self.SUPPORTED_EXTS}

        count = sum(
            1
            for file in os.listdir(path)
            if os.path.splitext(file)[1].lower() in supported_exts
        )

        return path, f"<span style='color: green;'>There are {count} images in this directory.</span>"

    def on_select_output_dir(self):
        path = self.select_directory()
        if not path:
            return gr.update(), gr.update()

        items = os.listdir(path)
        if not items:
            msg = "<span style='color: green; font-weight: bold;'>This directory is an empty folder.</span>"
        else:
            msg = "<span style='color: red; font-weight: bold;'>Warning: This directory is not empty and may result in file overwriting.</span>"
        return path, msg

    def on_start_batch(self, um: float, px: float, in_dir: str, out_dir: str):
        """批量分析生成器函数，能够在后台实时返回最新进度而不阻塞 UI"""
        self.stop_flag = False
        self.batch_result_df = pd.DataFrame()

        if not in_dir or not out_dir:
            yield (
                self._render_progress(0), pd.DataFrame(),
                gr.update(interactive=False), gr.update(interactive=False)
            )
            return

        files = []
        for ext in self.SUPPORTED_EXTS:
            files.extend(Path(in_dir).glob(f"*{ext}"))
            files.extend(Path(in_dir).glob(f"*{ext.upper()}"))
        files = list(set(files))
        total = len(files)

        if total == 0:
            yield (
                self._render_progress(0), pd.DataFrame([{"Tip": "No supported image found."}]),
                gr.update(interactive=False), gr.update(interactive=False)
            )
            return

        um_per_px = um / px if px else 1.0
        results = []

        for i, file_path in enumerate(files):
            if self.stop_flag:
                break

            # 调用处理算法
            metrics, proc_img = analysis_and_vis(file_path, um_per_px)

            # 将图像保存至输出目录
            out_path = Path(out_dir) / f"proc_{file_path.name}"
            cv2.imwrite(str(out_path), proc_img)

            # 汇总数据
            record = {"Filename": file_path.name}
            record.update(metrics)
            results.append(record)

            pct = int((i + 1) / total * 100)
            current_df = pd.DataFrame(results)

            # 更新迭代 UI: [进度条, 数据表, csv按钮(不可用), xlsx按钮(不可用)]
            yield (
                self._render_progress(pct),
                current_df,
                gr.update(interactive=False),
                gr.update(interactive=False)
            )

        # 结束批处理
        self.batch_result_df = pd.DataFrame(results)
        is_done = not self.stop_flag and total > 0
        final_pct = 100 if is_done else int(len(results) / total * 100)

        yield (
            self._render_progress(final_pct),
            self.batch_result_df,
            gr.update(interactive=is_done),
            gr.update(interactive=is_done)
        )

    def on_stop_batch(self):
        """停止标志位注入"""
        self.stop_flag = True

    def on_save_csv(self):
        if self.batch_result_df.empty: return
        path = self.save_file_dialog("CSV File", ".csv")
        if path:
            self.batch_result_df.to_csv(path, index=False, encoding='utf-8-sig')  # 避免中文乱码

    def on_save_xlsx(self):
        if self.batch_result_df.empty: return
        path = self.save_file_dialog("Excel File", ".xlsx")
        if path:
            self.batch_result_df.to_excel(path, index=False)

    # ==========================
    # UI 构建辅助方法
    # ==========================
    def _render_progress(self, pct: int) -> str:
        """使用内联 HTML 渲染流畅的自定义进度条"""
        return f"""
        <div style='width: 100%; background-color: #e0e0e0; border-radius: 6px; overflow: hidden; height: 22px; box-shadow: inset 0 1px 3px rgba(0,0,0,.2);'>
            <div style='width: {pct}%; height: 100%; background-color: #4caf50; transition: width 0.3s ease; text-align: center; color: white; line-height: 22px; font-family: sans-serif; font-size: 13px; font-weight: bold;'>
                {pct}%
            </div>
        </div>
        """

    def build_ui(self) -> gr.Blocks:
        """通过 Gradio API 组装应用程序的前端界面"""
        css = """
        /* 强制图像框保持正方形 */
        .square-img { aspect-ratio: 1 / 1; object-fit: contain; width: 100%; height: auto;}
        .main-header { text-align: center; margin-bottom: 20px; }
        .main-header h1 { margin-bottom: 5px; color: #333; }
        .main-header a { text-decoration: none; color: #007bff; margin: 0 15px; font-weight: 500;}
        .main-header a:hover { text-decoration: underline; }
        """

        with gr.Blocks(title="SuperCCM WorkStation", css=css, theme=gr.themes.Soft()) as app:
            with gr.Tab("Single-image Analysis"):
                gr.HTML('''
                    <div class="main-header">
                        <h1>SuperCCM WorkStation</h1>
                        <a href="https://aiccm.fun/" target="_blank">Website</a> |
                        <a href="https://github.com/qlnfm/SuperCCM" target="_blank">Github</a>
                    </div>
                ''')

                with gr.Row():
                    # 左半侧
                    with gr.Column(scale=1):
                        with gr.Row():
                            single_um = gr.Number(label="μm", value=400, precision=2)
                            single_px = gr.Number(label="per pixel", value=384, precision=0)

                        # 使用同一图像组件作为输入及原位输出显示，并注入预设好的 CSS 控制比例
                        single_img = gr.Image(type="numpy", image_mode="RGB", elem_classes="square-img",
                                              label="Preview")

                        with gr.Row():
                            btn_refresh = gr.Button('Refresh')
                            btn_single_clear = gr.Button("Clear", variant="secondary")
                            btn_single_analyze = gr.Button("Analysis", variant="primary")


                    # 右半侧
                    with gr.Column(scale=1):
                        single_results = gr.JSON(label="Analysis Results")

                # 单图事件绑定
                btn_refresh.click(
                    fn=refresh_image,
                    inputs=[single_img],
                    outputs=[single_img],
                )
                btn_single_analyze.click(
                    fn=self.on_analyze_single,
                    inputs=[single_img, single_um, single_px],
                    outputs=[single_img, single_results]
                )
                btn_single_clear.click(
                    fn=lambda: (None, None),  # 直接使用 lambda 清空输出
                    outputs=[single_img, single_results]
                )

            with gr.Tab("Batch Analysis"):
                with gr.Row():
                    # 左半侧
                    with gr.Column(scale=1):
                        with gr.Row():
                            batch_um = gr.Number(label="μm", value=400, precision=2)
                            batch_px = gr.Number(label="per pixel", value=384, precision=0)

                        with gr.Row():
                            btn_in_dir = gr.Button("Select Input Directory")
                        in_dir_txt = gr.Textbox(label="Input Directory", interactive=False)
                        in_count_txt = gr.HTML("There are 0 images in this directory.")

                        with gr.Row():
                            btn_out_dir = gr.Button("Select Output Directory")
                        out_dir_txt = gr.Textbox(label="Output Directory", interactive=False)
                        out_status_txt = gr.HTML("<br>")  # 空白占位防抖动

                        with gr.Row():
                            btn_batch_start = gr.Button("Start", variant="primary")
                            btn_batch_stop = gr.Button("Stop", variant="stop")

                    # 右半侧
                    with gr.Column(scale=1):
                        batch_progress = gr.HTML(self._render_progress(0), label="Task Progress")

                        with gr.Row():
                            btn_save_csv = gr.Button("Download csv", interactive=False)
                            btn_save_xlsx = gr.Button("Download xlsx", interactive=False)

                        batch_table = gr.Dataframe(label="DATA", interactive=False)

                # 批处理事件绑定
                btn_in_dir.click(fn=self.on_select_input_dir, outputs=[in_dir_txt, in_count_txt])
                btn_out_dir.click(fn=self.on_select_output_dir, outputs=[out_dir_txt, out_status_txt])

                btn_batch_start.click(
                    fn=self.on_start_batch,
                    inputs=[batch_um, batch_px, in_dir_txt, out_dir_txt],
                    outputs=[batch_progress, batch_table, btn_save_csv, btn_save_xlsx]
                )
                btn_batch_stop.click(fn=self.on_stop_batch)

                btn_save_csv.click(fn=self.on_save_csv)
                btn_save_xlsx.click(fn=self.on_save_xlsx)

        return app


def launch_app():
    """环境配置与启动器"""
    app_logic = SuperCCMApp()
    gradio_app = app_logic.build_ui()

    # 1. 启动 Gradio 本地服务器
    # prevent_thread_lock=True 非常关键，确保能够继续执行后续的 pywebview 逻辑
    port = 7860
    gradio_app.launch(server_port=port, prevent_thread_lock=True, show_api=False)

    # 2. 启动 PyWebview 创建原生桌面窗口包裹该端口
    webview.create_window(
        title="SuperCCM WorkStation",
        url=f"http://127.0.0.1:{port}",
        width=1280,
        height=850,
        min_size=(1024, 768)
    )
    # 阻塞启动原生窗体
    webview.start()


if __name__ == '__main__':
    launch_app()
