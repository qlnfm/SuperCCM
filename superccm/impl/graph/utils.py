SHAPE = (384, 384)


def is_near_edge(x, y, hw: tuple[int, int], n: int) -> bool:
    """
    判断点 (x, y) 是否在数组 arr 的边缘 n 像素内。

    参数:
        x, y: 点坐标（注意：x 对应列索引，y 对应行索引）
        arr: 二维 numpy 数组
        n: 距离边缘的像素范围

    返回:
        True  -> 在边缘 n 像素内
        False -> 不在边缘 n 像素内
    """
    h, w = hw

    return (
            x < n or
            y < n or
            x >= w - n or
            y >= h - n
    )
