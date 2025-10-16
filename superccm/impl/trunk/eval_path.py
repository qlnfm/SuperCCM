import math


def analyze_curve_sharpness_windowed(
        points: list[tuple[int, int]],
        half_window_size: int = 5,
        sharp_turn_threshold: float = 30.0,
        cusp_threshold: float = 135.0
) -> list[dict]:
    """
    使用滑动窗口方法分析曲线的突变和折返，这种方法更稳健，能抵抗局部噪声。

    Args:
        points (list[tuple[int, int]]): 代表曲线的坐标点列表。
        half_window_size (int): 定义滑动窗口的半宽度。
                                例如，为5时，会使用当前点前5个点和后5个点来定义方向向量。
        sharp_turn_threshold (float): 定义为“突变”的最小角度（度）。
        cusp_threshold (float): 定义为“折返”的最小角度（度）。

    Returns:
        list[dict]: 包含被识别为特征点的字典列表。
    """
    # 确保有足够的点来形成一个完整的窗口
    if len(points) < 2 * half_window_size + 1:
        return []

    results = []

    # 遍历所有可以作为窗口中心的点
    # 循环范围：从第一个能形成完整窗口的点到最后一个
    for i in range(half_window_size, len(points) - half_window_size):
        # 定义窗口的三个关键点
        p_start = points[i - half_window_size]  # 窗口起点
        p_curr = points[i]  # 窗口中心点 (待测点)
        p_end = points[i + half_window_size]  # 窗口终点

        # 创建入向量 vin (p_start -> p_curr)
        v_in = (p_curr[0] - p_start[0], p_curr[1] - p_start[1])
        # 创建出向量 vout (p_curr -> p_end)
        v_out = (p_end[0] - p_curr[0], p_end[1] - p_curr[1])

        # --- 接下来的角度计算逻辑与之前完全相同 ---

        # 计算向量的点积
        dot_product = v_in[0] * v_out[0] + v_in[1] * v_out[1]

        # 计算向量的模（长度）
        mag_v_in = math.sqrt(v_in[0] ** 2 + v_in[1] ** 2)
        mag_v_out = math.sqrt(v_out[0] ** 2 + v_out[1] ** 2)

        # 检查零向量（如果窗口内的点重合）
        if mag_v_in == 0 or mag_v_out == 0:
            continue

        # 计算夹角的余弦值并进行夹逼处理
        cos_angle = max(-1.0, min(1.0, dot_product / (mag_v_in * mag_v_out)))

        # 计算角度并转换为度
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)

        # 根据阈值判断类型
        feature_type = None
        if angle_deg >= cusp_threshold:
            feature_type = 'Cusp'
        elif angle_deg >= sharp_turn_threshold:
            feature_type = 'Sharp Turn'

        if True:
            results.append({
                "index": i,
                "point": p_curr,
                "angle": round(angle_deg, 2),
                "type": feature_type,
                "window": [i - half_window_size, i + half_window_size]
            })

    return results

