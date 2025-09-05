from superccm import SuperCCM, draw
import aiccm

superccm = SuperCCM()
file_path = 'your/img/path'
rst = superccm.run(file_path)
print(rst)
image = draw(superccm.graph)
aiccm.show_image(image)
