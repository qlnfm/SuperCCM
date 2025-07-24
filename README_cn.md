<div align="center">
  <img src="docs/assets/superccm.png" alt="description" />

<hr>

[English](./README.md) | 简体中文
</div>

## 🚀 简介

✨️SuperCCM是一个开源的，用于处理和分析角膜共聚焦显微镜(CCM)的角膜神经图像的Python框架。
通过输入一张CCM角膜神经图像，SuperCCM可以全自动的对图像进行处理，并输出各种临床中常用的形态学参数。


## ❇️ 环境准备

```shell
conda create -n superccm python=3.10 -y
conda activate superccm
pip install -r requirements.txt
```

## 🌟 在线体验

> https://huggingface.co/spaces/jugking6688/SuperCCM

## ⚡ 快速开始

```python
from superccm import SuperCCM  # 从superccm包中导入SuperCCM对象
import cv2

image = cv2.imread('path/to/your/image.png')  # 读取测试图片
# 当然，你也可以用任何你喜欢的方式得到一个图片对象
# 确保图片是形状为(384, 384, 3)，类型为uint8的np.ndarray对象
ccm = SuperCCM()  # 实例化SuperCCM对象
metrics = ccm(image)  # 处理并分析图像，返回一个储存有各个形态学参数的字典
print(metrics)  # 打印参数
```

## 📖 文档教程

我们提供了丰富的文档与教程供用户深入学习SuperCCM。
点击下方链接即可快速跳转至相应部分的文档。

 - ✨️ [自动分析](docs/doc_cn_auto_analysis.md)
 - ✨️ [可视化](docs/doc_cn_vis.md)
 - ✨️ [批量分析](docs/doc_cn_bulk_analysis.md)
 - ✨️ [Web应用程序](docs/doc_cn_bulk_analysis.md)


## 📄 许可协议

本项目遵循[GPL v3](LICENSE)开源许可证。

## 🎓 学术引用

> coming soon ...
