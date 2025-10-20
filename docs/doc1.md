# 🎇 SuperCCM Quick Tutorial

---

## 🧭 Introduction

**SuperCCM** offers two ways to use it:

* ✅ **Object-Oriented (OOP) style**
* ⚙️ **Functional style**

---

### 💎 Object-Oriented Usage

```python
from superccm import DefaultWorkFlow
from superccm.api import vis_ACCM, show_image

# Initialize default workflow
wf = DefaultWorkFlow()

# Run analysis
metrics = wf.run('test.jpg')
print(metrics)

# Visualize results
vis_img = vis_ACCM(wf.graph, wf.image)
show_image(vis_img)
```

---

### ⚡ Functional Usage

```python
from superccm.api import analysis, analysis_and_vis, show_image

# Direct analysis
metrics = analysis('test.jpg')
print(metrics)

# Analyze and visualize
metrics, vis_img = analysis_and_vis('test.jpg')
show_image(vis_img)
```

---

## 🖼️ Reading Images

Methods such as `SuperCCM.run()` or `superccm.api.analysis` can accept multiple input formats:

---

### 📂 1. Local File Path

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

### 🌐 4. Image URL

```python
from superccm import DefaultWorkFlow

img_url = 'https://www.yourimgurl.com/your/img/url'
wf = DefaultWorkFlow()
metrics = wf.run(img_url)
print(metrics)
```
