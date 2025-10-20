#!/usr/bin/env python3

"""
@license: Apache License Version 2.0
@author: Stefano Di Martino
Exact histogram matching - Optimized Version by Qincheng Qiao and Gemini
"""

import numpy as np
from scipy import ndimage
import os
import cv2


class OptimizedExactHistogramMatcher:
    # 内核定义保持不变
    _kernel1 = 1.0 / 5.0 * np.array([[0, 1, 0],
                                     [1, 1, 1],
                                     [0, 1, 0]])

    _kernel2 = 1.0 / 9.0 * np.array([[1, 1, 1],
                                     [1, 1, 1],
                                     [1, 1, 1]])

    _kernel3 = 1.0 / 13.0 * np.array([[0, 0, 1, 0, 0],
                                      [0, 1, 1, 1, 0],
                                      [1, 1, 1, 1, 1],
                                      [0, 1, 1, 1, 0],
                                      [0, 0, 1, 0, 0]])

    _kernel4 = 1.0 / 21.0 * np.array([[0, 1, 1, 1, 0],
                                      [1, 1, 1, 1, 1],
                                      [1, 1, 1, 1, 1],
                                      [1, 1, 1, 1, 1],
                                      [0, 1, 1, 1, 0]])

    _kernel5 = 1.0 / 25.0 * np.array([[1, 1, 1, 1, 1],
                                      [1, 1, 1, 1, 1],
                                      [1, 1, 1, 1, 1],
                                      [1, 1, 1, 1, 1],
                                      [1, 1, 1, 1, 1]])
    _kernel_mapping = {1: [_kernel1],
                       2: [_kernel1, _kernel2],
                       3: [_kernel1, _kernel2, _kernel3],
                       4: [_kernel1, _kernel2, _kernel3, _kernel4],
                       5: [_kernel1, _kernel2, _kernel3, _kernel4, _kernel5]}

    @staticmethod
    def get_histogram(image: np.ndarray, image_bit_depth: int = 8) -> np.ndarray:
        """
        高效地计算图像直方图。
        :param image: numpy 数组形式的图像
        :param image_bit_depth: 图像的位深度，大多数为8位。
        :return: 直方图
        """
        max_grey_value = 1 << image_bit_depth  # 等同于 pow(2, image_bit_depth)

        if image.ndim == 3:
            dimensions = image.shape[2]
            hist = np.empty((max_grey_value, dimensions), dtype=np.int64)
            for i in range(dimensions):
                # np.bincount 比循环快几个数量级
                hist[:, i] = np.bincount(image[..., i].ravel(), minlength=max_grey_value)
        else:
            hist = np.bincount(image.ravel(), minlength=max_grey_value)

        return hist

    @staticmethod
    def _get_averaged_images(img: np.ndarray, kernels: list) -> list:
        # 使用 ndimage.convolve 替代 signal.convolve2d
        return [ndimage.convolve(img, kernel) for kernel in kernels]

    @staticmethod
    def _match_to_histogram(image: np.ndarray, reference_histogram: np.ndarray, number_kernels: int) -> np.ndarray:
        """
        优化的核心匹配函数，显著减少内存使用并提高速度。
        """
        img_shape = image.shape
        img_flat = image.flatten()

        # 1. 计算均值图像
        kernels = OptimizedExactHistogramMatcher._kernel_mapping[number_kernels]
        averaged_images = OptimizedExactHistogramMatcher._get_averaged_images(image, kernels)

        # 2. 准备 lexsort 的排序键
        # lexsort 从最后一个键开始排序。为了按 (原始像素, 均值1, 均值2, ...) 的顺序排序，
        # 我们需要将键以相反的顺序传入：(..., 均值2, 均值1, 原始像素)
        sort_keys = [avg.flatten() for avg in reversed(averaged_images)]
        sort_keys.append(img_flat)

        # 3. 一次性获取排序后的索引，避免创建和排序大型中间矩阵
        sorted_indices = np.lexsort(sort_keys)

        # 4. 根据参考直方图生成目标像素值序列
        # 例如，如果 hist=[2, 0, 3]，将生成 [0, 0, 2, 2, 2]
        target_pixel_values = np.repeat(np.arange(len(reference_histogram)), reference_histogram.astype(np.int64))

        # 5. 直接将目标像素值赋给新图像的正确位置
        # 这是优化的关键：我们创建一个空数组，然后使用 sorted_indices 直接将
        # 排序后的目标值（target_pixel_values）放置到它们最终应该在的位置。
        # 这避免了第二次排序。
        new_img_flat = np.empty_like(img_flat)
        new_img_flat[sorted_indices] = target_pixel_values

        # 6. 将扁平化的图像重塑为原始形状
        return new_img_flat.reshape(img_shape)

    @staticmethod
    def match_image_to_histogram(image: np.ndarray, reference_histogram: np.ndarray,
                                 number_kernels: int = 3) -> np.ndarray:
        """
        公共API，用于将图像匹配到参考直方图。
        :param image: numpy 数组形式的图像。
        :param reference_histogram: numpy 数组形式的参考直方图
        :param number_kernels: 使用的核数量。核越多，结果越可能精确匹配直方图，但计算量也越大。
        :return: 具有精确参考直方图的图像。
                 注意：不要将结果图像保存为JPEG等有损格式，因为压缩会改变直方图！
                 请使用PNG等无损格式。
        """
        if image.ndim == 3:
            # 对于多通道图像（如RGB），逐通道处理
            output = np.empty_like(image)
            dimensions = image.shape[2]

            for i in range(dimensions):
                output[..., i] = OptimizedExactHistogramMatcher._match_to_histogram(
                    image[..., i],
                    reference_histogram[:, i],
                    number_kernels
                )
        else:
            # 对于灰度图像
            output = OptimizedExactHistogramMatcher._match_to_histogram(
                image,
                reference_histogram,
                number_kernels
            )

        return output


reference_img_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ref.png')
reference_img = cv2.imread(reference_img_path, 0)
reference_histogram = OptimizedExactHistogramMatcher.get_histogram(reference_img)


def histogram_standardization(image: np.ndarray) -> np.ndarray:
    image = OptimizedExactHistogramMatcher.match_image_to_histogram(image, reference_histogram)
    image = image.astype(np.uint8)
    return image
