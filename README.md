---
title: SuperCCM Web Application
emoji: 🚀
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: "5.35.0"
app_file: app.py
pinned: false
---

<div align="center">
  <img src="docs/assets/superccm.png" alt="description" />

<hr>

English | [简体中文](./README_cn.md)
</div>

## 🚀 Introduction

✨️SuperCCM is an open-source Python framework for processing and analyzing corneal nerve images from corneal confocal microscopy (CCM).
By inputting a CCM corneal nerve image, SuperCCM can automatically process the image and output various commonly used morphological parameters in clinical practice.

## 🌟 Using online

> https://huggingface.co/spaces/jugking6688/SuperCCM

## ❇️ Environmental Preparation

```shell
conda create -n superccm python=3.10 -y
conda activate superccm
pip install -r requirements.txt
```

## ⚡ Quickly Start

```python
from superccm import SuperCCM  # Import the superccm object from the SuperCCM package
import cv2

image = cv2.imread('path/to/your/image.png')  # Read the test image
# Of course, you can also obtain a picture object in any way you like
# Make sure the image is an np.ndarray object of shape (384, 384, 3) and type uint8
ccm = SuperCCM()  # Instantiate the SuperCCM object
metrics = ccm(image)  # Process and analyze the image, and return a dictionary storing various morphological parameters
print(metrics)  # Print parameters
```

## 📖 Document Tutorial

We offer a wealth of documentation and tutorials for users to delve deeply into SuperCCM.
Click the link below to quickly jump to the corresponding section of the document.

 - ✨️ [Auto Analysis](docs/doc_auto_analysis.md)
 - ✨️ [Visualization](docs/doc_vis.md)
 - ✨️ [Bulk Analysis](docs/doc_bulk_analysis.md)
 - ✨️ [Web Application](docs/doc_web.md)


## 📄 License

This project follows the [GPL v3](LICENSE) open source license.

## 🎓 Academic Citation

> coming soon ...
