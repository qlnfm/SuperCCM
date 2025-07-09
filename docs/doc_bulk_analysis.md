# 批量分析

The following is an example of batch analysis and saving of visual images:
```python
from superccm import SuperCCM, draw
import cv2
import aiccm
import os
from tqdm import tqdm

root = r'your/root/image/dir'
for file in tqdm(os.listdir(root)):
    print(file)
    image = cv2.imread(os.path.join(root, file))
    ccm = SuperCCM()
    metrics = ccm(image)
    print(file, metrics)
    aiccm.save_image(
        draw(ccm.nerve_image, ccm.nerve_graph), 
        os.path.join('your/save/dir', file)
    )
```
