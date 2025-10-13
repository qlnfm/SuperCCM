<div align="center">
  <img src="docs/assets/superccm.png" alt="description" />

<hr>

English | [简体中文](./README_CN.md)

</div>

### *SuperCCM Version 0.3.0*

## 🚀 Introduction

✨️SuperCCM is an open-source Python framework for processing and analyzing corneal nerve images from corneal confocal microscopy (CCM).
By providing a CCM corneal nerve image as input, SuperCCM can automatically process the image and output various clinically relevant morphological parameters.
SuperCCM also allows fast and easy integration of independent algorithms (e.g., segmentation) into the framework.

### 🎆 Github: [https://github.com/qlnfm/SuperCCM](https://github.com/qlnfm/SuperCCM)

## 🔮 Use Online

### 🤗 Hugging Face: [https://huggingface.co/spaces/jugking6688/SuperCCM-Web](https://huggingface.co/spaces/jugking6688/SuperCCM-Web)

### 🏠 Our Website: [http://aiccm.fun/](http://aiccm.fun/)

## ❇️ Environment Setup

```shell
conda create -n superccm python=3.10 -y
conda activate superccm
pip install -r requirements.txt
```

* Install from PyPI:

```shell
pip install superccm
```

## ⚡ Quick Start

```python
from superccm import DefaultWorkFlow

wf = DefaultWorkFlow()
metrics = wf.run('your/img/path')
print(metrics)
```

Or a simpler, less formal version:

```python
from superccm.api import analysis

metrics = analysis('your/img/path')
print(metrics)
```
Or, enable Web service locally:
```shell
python app.py
```

## 📖 Documentation & Tutorials

SuperCCM follows a principle of simplicity, allowing users and developers to get started and master it with minimal cost and time.

* ✨️ [Quick Tutorial](docs/doc1.md): Learn how to use SuperCCM in detail
* ✨️ [Module Development](docs/doc2.md): Learn how to customize workflows and integrate your own algorithms into SuperCCM

## 📄 License

This project is licensed under the [GPL v3](LICENSE) open-source license.

## 🎓 Academic Citation

> coming soon ...
