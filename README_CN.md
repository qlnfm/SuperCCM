<div align="center">

<img src="docs/assets/superccm.png" alt="SuperCCM Logo" width="500"/>

---

# ✨ SuperCCM v1.0

**🧠 A Fully Open-Source Framework for Corneal Confocal Microscopy (CCM) Image Analysis**

[![GitHub](https://img.shields.io/badge/GitHub-SuperCCM-blue?logo=github)](https://github.com/qlnfm/SuperCCM)
[![PyPI](https://img.shields.io/pypi/v/superccm?color=blueviolet&logo=pypi)](https://pypi.org/project/superccm/)
[![License: GPL v3](https://img.shields.io/badge/license-GPLv3-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

**[English](./README.md)** | **简体中文**

</div>

---

## 🚀 简介

### 💡 什么是 SuperCCM？为什么需要它？

✨ **SuperCCM** 是一个 **开源 Python 框架**，用于处理和分析角膜共聚焦显微镜 (CCM) 的角膜神经图像。  
只需输入一张 CCM 图像，SuperCCM 即可 **自动完成图像分析与形态学参数提取**。  
此外，SuperCCM 提供模块化架构，支持快速集成自定义算法（如分割、去噪等）。

🧩 **背景**  
过去 20 年间，CCM
角膜神经形态被证明是多种神经退行性疾病（如糖尿病周围神经病变、帕金森病）或眼表疾病（如干眼症）的可靠临床指标或预测因子。  
传统分析工具（CCMetrics、NeuronJ/ImageJ、ACCMetrics）存在封闭、繁琐等问题，  
SuperCCM 致力于提供一个 **开源、透明、自由且高效** 的新选择。

---

## 🔮 在线使用

🎯 **无需安装，立即体验：**  
👉 [在 Hugging Face 上运行 SuperCCM Web App](https://huggingface.co/spaces/jugking6688/SuperCCM-Web)

---

## ❇️ 环境安装

### 🧱 方式一：从源码安装

```bash
conda create -n superccm python=3.10 -y
conda activate superccm
pip install -r requirements.txt
````

### 📦 方式二：通过 PyPI 安装

```bash
pip install superccm
```

---

## ⚡ 快速开始

### ✅ 使用默认工作流

```python
from superccm import DefaultWorkFlow

wf = DefaultWorkFlow()
metrics = wf.run('your/img/path')
print(metrics)
```

### 🧩 快捷方式（非正式）

```python
from superccm.api import analysis

metrics = analysis('your/img/path')
print(metrics)
```

### 🌐 启动本地 Web 服务

```bash
python app.py
```

---

## 📖 文档教程

SuperCCM 坚持 “**简洁、模块化、易上手**” 的开发理念。
无论是研究者还是开发者，都可以快速入门。

* 📘 [简明教程](docs/doc1_cn.md)：深入了解 SuperCCM 的使用方法
* 🧠 [模块编写指南](docs/doc2_cn.md)：学习如何自定义工作流与算法模块

---

## 📄 许可协议

本项目基于 [**GPL v3**](./LICENSE) 开源许可协议发布。
欢迎自由使用与二次开发，但请保留署名。

---

## 🎓 学术引用

> 📢 即将发布！我们的论文已被 **TVST** 正式接收，敬请期待引用格式。

---

<div align="center">

🧬 Made with ❤️ by the SuperCCM Team
💻 [https://github.com/qlnfm/SuperCCM](https://github.com/qlnfm/SuperCCM)

</div>