import numpy as np
from scipy import ndimage as ndi
from skimage import exposure, color

__all__ = ["vignetting_correction"]


def _to_float32(img):
    img = img.astype(np.float32)
    if img.ndim == 3:
        img = color.rgb2gray(img)
    if img.max() > 1.0:
        img = img / img.max()
    return img


def _to_output_dtype(img_float, orig_dtype):
    if np.issubdtype(orig_dtype, np.integer):
        out = (img_float * np.iinfo(orig_dtype).max).clip(
            0, np.iinfo(orig_dtype).max
        ).astype(orig_dtype)
    else:
        out = img_float.astype(orig_dtype)
    return out


def estimate_illumination_morph_gauss(image, se_radius=None, smooth_sigma=None):
    """估计平滑照明场（方法1：灰度开运算+高斯平滑）"""
    h, w = image.shape
    if se_radius is None:
        se_radius = max(3, min(h, w) // 12)
    size = (se_radius * 2 + 1, se_radius * 2 + 1)
    opened = ndi.grey_opening(image, size=size)
    if smooth_sigma is None:
        smooth_sigma = max(h, w) / 20.0
    background = ndi.gaussian_filter(opened, sigma=smooth_sigma)
    background = np.maximum(background, 1e-8)
    return background


def estimate_illumination_polyfit(image, degree=2, mask_percentile=80):
    """估计平滑照明场（方法2：log域多项式拟合）"""
    h, w = image.shape
    thresh = np.percentile(image, mask_percentile)
    mask = image < thresh
    yy, xx = np.mgrid[0:h, 0:w]
    x = xx[mask].ravel()
    y = yy[mask].ravel()
    z = np.log(image[mask].ravel() + 1e-8)

    def poly_terms(x, y, deg):
        terms = []
        for i in range(deg + 1):
            for j in range(deg + 1 - i):
                terms.append((x ** i) * (y ** j))
        return np.vstack(terms).T

    A = poly_terms(x, y, degree)
    coeffs, *_ = np.linalg.lstsq(A, z, rcond=None)
    A_full = poly_terms(xx.ravel(), yy.ravel(), degree)
    z_fit = A_full.dot(coeffs).reshape(h, w)
    background = np.exp(z_fit)
    background = np.maximum(background, 1e-8)
    return background


def vignetting_correction(image, method="polyfit", **kwargs):
    """执行暗角校正。

    参数
    ------
    image : ndarray
        灰度或RGB图像 (uint8/uint16/float)
    method : str
        'morph_gauss' 或 'polyfit'
    kwargs : dict
        传递给估计函数的额外参数

    返回
    ------
    corrected : ndarray
        校正后的图像，与输入 dtype 相同
    background : ndarray
        估计的照明场 (float32 [0,1])
    """
    orig_dtype = image.dtype
    imgf = _to_float32(image)

    if method == "morph_gauss":
        background = estimate_illumination_morph_gauss(imgf, **kwargs)
    elif method == "polyfit":
        background = estimate_illumination_polyfit(imgf, **kwargs)
    else:
        raise ValueError("Unknown method: %s" % method)

    median_bg = np.median(background)
    corrected = imgf / (background + 1e-8) * median_bg
    corrected = np.clip(corrected, 0.0, 1.0)

    p2, p98 = np.percentile(corrected, (1, 99))
    corrected = exposure.rescale_intensity(corrected, in_range=(p2, p98))

    out = _to_output_dtype(corrected, orig_dtype)
    return out
