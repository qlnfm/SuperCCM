<div align="center">
  <img src="docs/assets/superccm.png" alt="description" />

<hr>

[English](./README.md) | 简体中文
</div>

## 🚀 Introduction

✨️SuperCCM is an open-source Python framework for processing and analyzing corneal nerve images from corneal confocal microscopy (CCM). By inputting a CCM corneal nerve image, SuperCCM can automatically process the image and output various commonly used morphological parameters in clinical practice.
### 🏠Github: https://github.com/qlnfm/SuperCCM

## ❇️ Environmental Preparation

```shell
conda create -n superccm python=3.10 -y
conda activate superccm
pip install -r requirements.txt
```
 - Install from PyPI
```shell
pip install superccm
```

## 🌟 Using online

> https://huggingface.co/spaces/jugking6688/SuperCCM

## ⚡ Quickly Start

```python
from superccm import SuperCCM

ccm = SuperCCM()
metrics = ccm.run('your/img/path')
print(metrics)
```
 - Just a few lines of commands are needed.

## 📖 Document Tutorial

 - ✨️ [Advanced Tutorial](docs/doc1.md): Gain a thorough understanding of the use of SuperCCM
 - ✨️ [Module writing](docs/doc2.md): Learn how to customize the workflow and integrate your developed algorithms into SuperCCM

## 📄 License

This project follows the [GPL v3](LICENSE) open source license.

## 🎓 Academic Citation

> coming soon ...
