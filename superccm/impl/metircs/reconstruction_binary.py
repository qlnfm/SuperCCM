import cv2
import numpy as np
from skimage.morphology import reconstruction


def reconstruct_binary(binary: np.ndarray, skeleton: np.ndarray, max_radius=None):
    """
    根据骨架和原始掩膜，通过距离变换进行区域重建。

    参数：
    ----------
    mask : np.ndarray
        原始二值掩膜图像（0/1 或 0/255），类型 uint8。
    skeleton : np.ndarray
        处理后的骨架图像（0/1 或 0/255），类型 uint8。
    max_radius : float, 可选
        限制最大重建半径（单位：像素）。None 表示不限制。

    返回：
    ----------
    reconstructed_mask : np.ndarray
        从骨架重建的掩膜图像（二值，0/1）。
    """

    # 1️⃣ 统一二值格式
    mask_bin = (binary > 0).astype(np.uint8)
    skeleton_bin = (skeleton > 0).astype(np.uint8)

    # 2️⃣ 计算距离变换（原mask的厚度）
    dist = cv2.distanceTransform(mask_bin, cv2.DIST_L2, 5)

    # 3️⃣ 构造重建种子
    seed = np.zeros_like(dist, dtype=float)
    seed[skeleton_bin > 0] = dist[skeleton_bin > 0]

    # 4️⃣ 限制最大扩张半径（可选）
    if max_radius is not None:
        seed = np.minimum(seed, max_radius)

    # 5️⃣ 灰度形态学重建
    reconstructed = reconstruction(seed, dist, method='dilation')

    # 6️⃣ 转为二值输出
    reconstructed_mask = (reconstructed > 0).astype(np.uint8) * 255

    return reconstructed_mask
