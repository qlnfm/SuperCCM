from superccm import SuperCCM, draw
import cv2
import aiccm

image = cv2.imread('docs/assets/auto_analysis/img.jpg')
ccm = SuperCCM()
metrics = ccm(image)
print(metrics)
aiccm.show_image(draw(ccm.nerve_image, ccm.nerve_graph))
