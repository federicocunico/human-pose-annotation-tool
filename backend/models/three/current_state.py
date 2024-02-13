import numpy as np

from .color import Color
from .point import Point
from .vector3 import Vector3
from .skeleton import Skeleton
from ..pydantic_ext import BaseModel


class CurrentState(BaseModel):
    title: str | None = None
    points: List[Point] = []
    skeletons: List[Skeleton] = []

    ### Clear function
    def clear(self):
        self.clear_points()
        self.clear_skeletons()

    def clear_points(self):
        self.points = []

    def clear_skeletons(self):
        self.skeletons = []

    ### Add to state
    def add_points(self, points: np.ndarray, size: int = 1, color="blue"):
        points = [Vector3.from_numpy(p) for p in points]
        c = Color.from_string(color) if isinstance(color, str) else Color.from_tuple(color)
        points = [
            Point(location=p, size=size, color=c) for p in points
        ]
        self.points.extend(points)

    def add_skeleton(self, skeleton: Skeleton):
        self.skeletons.append(skeleton)

    ### Dumping data to frontend
    def dump(self):
        return self.model_dump()
