from skimage.morphology import skeletonize


def get_skeleton(image):
    """ 将图片骨架化（根据是否靠边使用不同的最小面积阈值） """
    image = image > 0
    skeleton = skeletonize(image)
    skeleton = skeleton.astype('uint8')
    skeleton = skeleton * 255

    # 设置边缘像素为0
    skeleton[0, :] = 0
    skeleton[-1, :] = 0
    skeleton[:, 0] = 0
    skeleton[:, -1] = 0

    return skeleton
