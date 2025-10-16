from superccm.impl.trunk.eval_path import analyze_curve_sharpness_windowed
from superccm.impl.trunk.ep_path import get_paths
import numpy as np
from scipy.spatial.distance import euclidean
from scipy.signal import medfilt

from superccm.impl.utils.ccm_vignetting import vignetting_correction
from superccm.impl.utils.histogram_matching import histogram_standardization
from superccm.impl.utils.estimate_width import estimate_width
from superccm.impl.utils.tools import get_canvas, cal_length, show_image


def extract_trunk(
        image: np.ndarray,
        skeleton: np.ndarray,
        *,
        side_x=30,
        min_distance=200,
        min_intensity=90,
) -> np.ndarray:
    image_ = vignetting_correction(histogram_standardization(image))
    skeleton_i = estimate_width(image_, skeleton)

    all_shortest_paths = get_paths(skeleton, side_x)
    canvas_list = []
    for pair, path in all_shortest_paths.items():
        distance = euclidean(*pair)
        if distance < min_distance:
            continue
        canvas = get_canvas(1)
        for y, x in path:
            intensity: int = skeleton_i[y, x]
            canvas[y, x] = intensity

        length = cal_length(canvas)
        intensities = [skeleton_i[y, x] for y, x in path]
        mean_intensity = sum(intensities) / length
        median_intensity = np.median(intensities)
        if mean_intensity < min_intensity:
            continue

        smooth = medfilt(np.array(intensities), kernel_size=15)
        rsd = np.std(smooth) / np.mean(smooth)
        if rsd > 0.5:
            continue

        results = analyze_curve_sharpness_windowed(path, half_window_size=15)
        angles = [x['angle'] for x in results]

        max_angle = max(angles)
        if max_angle >= 90:
            continue

        # print(rsd)
        # show_image(canvas)
        canvas_list.append((canvas, max_angle + rsd * 0.5 - median_intensity * 0.3))

    # paths = sorted(paths, key=lambda x: x['max_angle'])
    canvas_list = sorted(canvas_list, key=lambda x: x[1])
    canvas_all = get_canvas(1)
    for canvas in canvas_list:
        if not np.any(np.logical_and(canvas_all > 0, canvas[0] > 0)):
            canvas_all += canvas[0]

    return canvas_all
