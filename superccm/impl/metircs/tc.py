"""
The algorithm is reproduced from the paper:
Kallinikos P, Berhanu M, O'Donnell C, Boulton AJ, Efron N, Malik RA. Corneal nerve tortuosity in diabetic patients with neuropathy. Invest Ophthalmol Vis Sci. 2004;45(2):418-422. doi:10.1167/iovs.03-0637
After testing, the error compared with the original result is extremely small.
"""

import numpy as np


def calculate_tc(nerve_coords):
    if len(nerve_coords) < 3:
        return 0.0

    nerve_coords = nerve_coords[np.argsort(nerve_coords[:, 0])]

    x = nerve_coords[:, 0]
    y = nerve_coords[:, 1]

    # Dynamically determine dx from the actual step size in x coordinates
    # dx is the distance between consecutive x pixels.
    # For generated functions, this is (x_max - x_min) / (num_points - 1)
    # For image pixels, if aligned to x-axis, it's usually 1.
    # We take the average difference to handle potential floating point inaccuracies
    # or slight non-uniformity, though for linspace it should be uniform.
    if len(x) > 1:
        dx = np.mean(np.diff(x))  # Calculate the actual step size
    else:
        return 0.0  # Not enough points to determine dx

    # TC calculation
    tc_sum = 0.0

    # Iterate from the second point to the second-to-last point to allow for f(x_j-1), f(x_j), f(x_j+1)
    for j in range(1, len(y) - 1):
        # First derivative at x_j (using forward difference as per paper formula)
        first_derivative = (y[j + 1] - y[j]) / dx

        # Second derivative at x_j (using central difference as per paper formula)
        second_derivative = (y[j + 1] - 2 * y[j] + y[j - 1]) / (dx ** 2)

        # Term for summation: (x_j+1 - x_j) * { [f'(x_j)]^2 + [f''(x_j)]^2 }
        # Here (x_j+1 - x_j) is approximately dx
        term = dx * (first_derivative ** 2 + second_derivative ** 2)
        tc_sum += term

    return np.sqrt(tc_sum)


# The preprocess_and_align_nerve and generate_function_coords functions remain the same
def preprocess_and_align_nerve(image):
    y_coords, x_coords = np.where(image > 0)
    nerve_coords = np.vstack((x_coords, y_coords)).T

    if len(nerve_coords) < 2:
        return np.array([])

    min_x_idx = np.argmin(nerve_coords[:, 0])
    max_x_idx = np.argmax(nerve_coords[:, 0])

    if min_x_idx == max_x_idx:
        return nerve_coords

    end_point1 = nerve_coords[min_x_idx]
    end_point2 = nerve_coords[max_x_idx]

    translation_vector = -end_point1
    translated_coords = nerve_coords + translation_vector

    translated_end_point1 = end_point1 + translation_vector
    translated_end_point2 = end_point2 + translation_vector

    delta_x = translated_end_point2[0] - translated_end_point1[0]
    delta_y = translated_end_point2[1] - translated_end_point1[1]

    if delta_x == 0 and delta_y == 0:
        angle_rad = 0.0
    elif delta_x == 0:
        angle_rad = np.pi / 2 if delta_y > 0 else -np.pi / 2
    else:
        angle_rad = np.arctan2(delta_y, delta_x)

    cos_theta = np.cos(-angle_rad)
    sin_theta = np.sin(-angle_rad)

    rotation_matrix = np.array([[cos_theta, -sin_theta],
                                [sin_theta, cos_theta]])

    rotated_coords = np.dot(translated_coords, rotation_matrix.T)

    return rotated_coords


def generate_function_coords(func, x_range, num_points):
    x = np.linspace(x_range[0], x_range[1], num_points)
    y = func(x)
    return np.vstack((x, y)).T


def get_tc(image):
    coords = preprocess_and_align_nerve(image)
    tc = calculate_tc(coords)
    return tc


