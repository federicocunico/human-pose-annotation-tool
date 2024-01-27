import numpy as np

from .vector3 import Vector3
from .color import Color
from ...pydantic_ext import BaseModel


class Point(BaseModel):
    location: Vector3
    size: float = 1.0
    color: Color = Color.from_string("blue")

    @staticmethod
    def from_numpy(p: np.ndarray):
        return Point(location=Vector3.from_numpy(p))
