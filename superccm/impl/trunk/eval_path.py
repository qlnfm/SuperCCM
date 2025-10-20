import math


def analyze_curve_sharpness_windowed(
        points: list[tuple[int, int]],
        half_window_size: int = 5,
) -> list[float]:
    """
    The sliding window method is used to analyze the sudden changes and re-entries of the curve.

    Args:
        points (list[tuple[int, int]]): List of coordinate points representing the curve.
        half_window_size (int): Define the half-width of the sliding window.
            For example, when it is set to 5,
            the direction vector will be defined using the 5 points before
            the current point and the 5 points after the current point.

    Returns:
        list[float]: List of angles.
    """
    # Make sure there are enough points to form a complete window/确保有足够的点来形成一个完整的窗口
    if len(points) < 2 * half_window_size + 1:
        return []

    results = []

    # Traverse all the points that can serve as the center of the window/遍历所有可以作为窗口中心的点
    # Loop range: From the first point that can form a complete window to the last one.
    # 循环范围：从第一个能形成完整窗口的点到最后一个
    for i in range(half_window_size, len(points) - half_window_size):
        # The three key points for defining a window/定义窗口的三个关键点
        p_start = points[i - half_window_size]  # Window starting point
        p_curr = points[i]  # Center point of the window (the point to be tested)
        p_end = points[i + half_window_size]  # Window endpoint

        # Create an input vector vin (p_start -> p_curr)
        v_in = (p_curr[0] - p_start[0], p_curr[1] - p_start[1])
        # Create a vector vout (p_curr -> p_end)
        v_out = (p_end[0] - p_curr[0], p_end[1] - p_curr[1])

        # Calculate the dot product of vectors
        dot_product = v_in[0] * v_out[0] + v_in[1] * v_out[1]

        # Calculate the magnitude (length) of the vector
        mag_v_in = math.sqrt(v_in[0] ** 2 + v_in[1] ** 2)
        mag_v_out = math.sqrt(v_out[0] ** 2 + v_out[1] ** 2)

        # Check the zero vector (if the points within the window coincide)/检查零向量（如果窗口内的点重合）
        if mag_v_in == 0 or mag_v_out == 0:
            continue

        # Calculate the cosine value of the angle and perform the squeezing method/计算夹角的余弦值并进行夹逼处理
        cos_angle = max(-1.0, min(1.0, dot_product / (mag_v_in * mag_v_out)))

        # Calculate the angle and convert it to degrees/计算角度并转换为度
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)

        if True:
            results.append(angle_deg)

    return results
