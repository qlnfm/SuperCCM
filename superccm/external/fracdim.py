import numpy as np
from sklearn.linear_model import LinearRegression


def fractal_dimension(image):
    """
    Calculate the fractal dimension of the binarized image using the box counting method.
    """
    image = image.astype(bool)

    min_dim = min(image.shape)

    n = int(np.floor(np.log2(min_dim / 2)))
    sizes = 2 ** np.arange(1, n + 1)

    counts = []

    for size in sizes:
        box_count = 0
        for x in range(0, image.shape[0], size):
            for y in range(0, image.shape[1], size):
                box = image[x:x + size, y:y + size]
                if np.any(box):
                    box_count += 1

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
