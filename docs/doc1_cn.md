# 🎇 SuperCCM 简明教程

---

## 🧭 前言

**SuperCCM** 提供两种使用方式：

- ✅ **面向对象（OOP）风格**
- ⚙️ **函数式（Functional）风格**

---

### 💎 面向对象用法

```python
from superccm import DefaultWorkFlow
from superccm.api import vis_ACCM, show_image

# 初始化默认工作流
wf = DefaultWorkFlow()

# 运行分析
metrics = wf.run('test.jpg')
print(metrics)

# 可视化结果
vis_img = vis_ACCM(wf.graph, wf.image)
show_image(vis_img)
````

---

### ⚡ 函数式用法

```python
from superccm.api import analysis, analysis_and_vis, show_image

# 直接分析
metrics = analysis('test.jpg')
print(metrics)

# 分析并可视化
metrics, vis_img = analysis_and_vis('test.jpg')
show_image(vis_img)
```

---

## 🖼️ 读取图片

`SuperCCM.run()`或者`superccm.api.analysis` 等方法可以接受多种输入格式：

---

### 📂 1. 本地路径

```python
from superccm import DefaultWorkFlow

wf = DefaultWorkFlow()
metrics = wf.run('your/img/path')
print(metrics)
```

---

### 🧮 2. `numpy.ndarray`

```python
from superccm import DefaultWorkFlow
import cv2

img = cv2.imread('your/img/path', 0)
wf = DefaultWorkFlow()
metrics = wf.run(img)
print(metrics)
```

---

### 🖌️ 3. `PIL.Image`

```python
from superccm import DefaultWorkFlow
from PIL import Image

img = Image.open('your/img/path')
wf = DefaultWorkFlow()
metrics = wf.run(img)
print(metrics)
```

---

### 🌐 4. 图片 URL

```python
from superccm import DefaultWorkFlow

img_url = 'https://www.yourimgurl.com/your/img/url'
wf = DefaultWorkFlow()
metrics = wf.run(img_url)
print(metrics)
```

---

