import cv2

from .morphology import NerveImage
from .graph import NerveGraph
from .common import get_canvas

from typing import Literal

BACKGROUND_TYPE = Literal['empty', 'image']


def draw(
        nerve_image: NerveImage,
        nerve_graph: NerveGraph,
        *,
        main_edge_color: tuple[int, int, int] = (0, 0, 255),
        side_edge_color: tuple[int, int, int] = (255, 0, 0),
        edge_body: bool = False,
        show_main_edge: bool = True,
        show_side_edge: bool = True,
        end_node_color: tuple[int, int, int] = (255, 255, 0),
        branch_node_color: tuple[int, int, int] = (0, 255, 0),
        show_end_node: bool = False,
        show_branch_node: bool = True,
        background: BACKGROUND_TYPE = 'image',
        branch_node_size: int = 2,
        end_node_size: int = 0,
):
    """
    Visualization method
    :param nerve_image: NerveImage object
    :param nerve_graph: NerveGraph object
    :param main_edge_color: The color of the main nerve fibers
    :param side_edge_color: The color of the side nerve fibers
    :param edge_body: Whether to show the complete nerve fibers or only the skeleton
    :param show_main_edge: Whether the main nerve fibers are shown
    :param show_side_edge: Whether the side nerve fibers are shown
    :param end_node_color: The color of the end nodes
    :param branch_node_color: The color of the branch nodes
    :param show_end_node: Whether the end nodes are shown
    :param show_branch_node: Whether the branch nodes are shown
    :param background: For the image background, select 'Image' to use the original image as the background,
        and select 'empty' to use a pure black background
    :param branch_node_size: The radius (in pixels) of the size of the branch nodes
    :param end_node_size: The radius (in pixels) of the size of the end nodes
    :return:
    """
    match background:
        case 'empty':
            canvas = get_canvas(3)
        case 'image':
            canvas = nerve_image.image.copy()
        case _:
            raise TypeError

    for _, edge in nerve_image.edges.items():
        match edge.edge_type:
            case 'main':
                if not show_main_edge:
                    continue
                color = main_edge_color
            case 'side':
                if not show_side_edge:
                    continue
                color = side_edge_color
            case _:
                if edge_body or not any([show_main_edge, show_side_edge]):
                    continue
                color = edge.color if edge.color is not None else (128, 128, 128)
        if edge_body:
            canvas[edge.body > 0] = color
        else:
            canvas[edge.bone > 0] = color

    for _, node in nerve_image.nodes.items():
        match node.node_type:
            case 'end':
                if not show_end_node:
                    continue
                color = end_node_color
                size = end_node_size
            case 'branch':
                if not show_branch_node:
                    continue
                color = branch_node_color
                size = branch_node_size
            case _:
                if edge_body or not any([show_main_edge, show_side_edge]):
                    continue
                color = node.color if node.color is not None else (128, 128, 128)
                size = 0

        if size:
            cv2.circle(canvas, tuple(int(n) for n in node.centroid), size, color, -1)
        else:
            canvas[node.bone > 0] = color

    return canvas
