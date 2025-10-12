import cv2


def get_gaussian_kernel(ksize=1, sigma=1):
    """ Get a Gaussian kernel """
    gaussian_kernel = cv2.getGaussianKernel(ksize=ksize, sigma=sigma)
    gaussian_kernel_2d = gaussian_kernel @ gaussian_kernel.T
    return gaussian_kernel_2d


def get_conv2d(image, kernel):
    assert len(image.shape) == 2
    output = cv2.filter2D(image, -1, kernel)
    return output


def estimate_width(image, skeleton):
    conv_result = get_conv2d(image, get_gaussian_kernel())
    conv_result[skeleton == 0] = 0
    return conv_result
