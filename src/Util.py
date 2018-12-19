import cv2
import numpy as np
from enum import Enum


def construct_bounding_box_array_from_contour(contour):
    [x, y, w, h] = cv2.boundingRect(contour)
    return np.array([[x, y], [x + w, y], [x, y + h], [x + w, y + h]])


class Side(Enum):
    RED = 1
    BLUE = 2
    NONE = 0


class MissingTimeException(Exception):
    pass


class NoDigitContoursException(Exception):
    pass