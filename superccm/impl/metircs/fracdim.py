import numpy as np
from sklearn.linear_model import LinearRegression


def fractal_dimension(image):
    """
    Calculate the fractal dimension of the binarized image using the box counting method.
    Optimized with vectorized operations.
    """
    image = image.astype(bool)
    min_dim = min(image.shape)
    n = int(np.floor(np.log2(min_dim / 2)))
    sizes = 2 ** np.arange(1, n + 1)

    counts = []
    for size in sizes:
        # 截断到能整除的区域，避免边界问题
        new_shape = (image.shape[0] // size * size,
                     image.shape[1] // size * size)
        img_cropped = image[:new_shape[0], :new_shape[1]]

        # 先 reshape，再检查每个 box 是否有 True
        img_reshaped = img_cropped.reshape(
            new_shape[0] // size, size,
            new_shape[1] // size, size
        )
        # 压缩 size 维度，得到 box 是否有像素
        box_present = img_reshaped.any(axis=(1, 3))
        box_count = np.count_nonzero(box_present)

        if box_count > 0:
            counts.append((size, box_count))

    if len(counts) < 2:
        return 0.0, None, None

    counts = np.array(counts)
    log_sizes = np.log(1.0 / counts[:, 0])
    log_counts = np.log(counts[:, 1])

    model = LinearRegression()
    model.fit(log_sizes.reshape(-1, 1), log_counts)
    D = model.coef_[0]

    return D
