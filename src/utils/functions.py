import cv2
import numpy as np
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPolygonF, QPen, QBrush
from PySide6.QtWidgets import QGraphicsPolygonItem


def points_are_close(point1: QPointF, point2: QPointF, threshold: float = 5.0) -> bool:
    """
    Check if two points are close to each other.
    Args:
        point1 (QPointF): The first point.
        point2 (QPointF): The second point.
        threshold (float, optional): The maximum distance between the points to consider them close. Defaults to 5.0.
    Returns:
        bool: True if the points are close to each other, False otherwise.
    """
    return (point1 - point2).manhattanLength() < threshold


def calculate_handle_size(
    image_width: int,
    image_height: int,
    scale_factor: float = 1.0,
    min_handle_size: float = 5.0,
    max_handle_size: float = 20.0,
) -> float:
    average_dim = (image_width + image_height) / 2
    average_dim = 0.01 * average_dim

    scaled_handle_size = average_dim * scale_factor

    scaled_handle_size = max(min_handle_size, min(scaled_handle_size, max_handle_size))

    return scaled_handle_size


def simplify_contour(contour, epsilon_factor=0.005):
    """
    Simplify a contour using the Douglas-Peucker algorithm.

    :param contour: The contour to simplify.
    :param epsilon_factor: Factor to determine the approximation accuracy.
        Smaller values lead to more detailed approximations.
    :return: A simplified version of the contour.
    """
    contour = np.array(contour, dtype=np.int32).reshape(-1, 1, 2)

    epsilon = epsilon_factor * cv2.arcLength(contour, True)
    simplified_contour = cv2.approxPolyDP(contour, epsilon, True)
    return simplified_contour
