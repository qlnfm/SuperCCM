# 🎇SuperCCM Advanced Tutorial

## Read the image
In the initial quickly start, we learned that:
```python
from superccm import SuperCCM

ccm = SuperCCM()
metrics = ccm.run('your/img/path')
print(metrics)
```
In fact, `SuperCCM.run` can accept more input formats, such as:
 - np.ndarray
```python
from superccm import SuperCCM
import cv2

img = cv2.imread('your/img/path', 0)
ccm = SuperCCM()
metrics = ccm.run(img)
print(metrics)
```
 - PIL.Image
```python
from superccm import SuperCCM
from PIL import Image

img = Image.open('your/img/path')
ccm = SuperCCM()
metrics = ccm.run(img)
print(metrics)
```
 - URL
```python
from superccm import SuperCCM

img_url = 'https://www.yourimgurl.com/your/img/url'
ccm = SuperCCM()
metrics = ccm.run(img_url)
print(metrics)
```

## Result visualization
SuperCCM offers a method called `draw` for visualizing the results.
```python
from superccm import SuperCCM, draw

superccm = SuperCCM()
file_path = 'your/img/path'
rst = superccm.run(file_path)
print(rst)
image = draw(superccm.graph)
image
```
The parameters of the `draw` method are:
```text
    :param nerve_graph: NerveGraph object
    :param main_edge_color: The color of the main nerve fibers
    :param side_edge_color: The color of the side nerve fibers
    :param edge_body: Whether to show the complete nerve fibers or only the skeleton
    :param show_main_edge: Whether the main nerve fibers are shown
    :param show_side_edge: Whether the side nerve fibers are shown
    :param end_node_color: The color of the end nodes
    :param branch_node_color: The color of the branch nodes
    :param show_end_node: Whether the end nodes are shown
    :param show_branch_node: Whether the branch nodes are shown
    :param background: For the image background, select 'Image' to use the original image as the background,
        and select 'empty' to use a pure black background
    :param branch_node_size: The radius (in pixels) of the size of the branch nodes
    :param end_node_size: The radius (in pixels) of the size of the end nodes
```
# Interact with SuperCCM through a Web application

1. Start the web service

```shell
python app.py
```
Output:
```text
* Running on local URL:  http://127.0.0.1:7860
```

2. Access the url through a browser

<img src="assets/web/app.png">

3. Upload an image

<img src="assets/web/app_2.png">