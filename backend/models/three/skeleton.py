from .color import Color
from .vector3 import Vector3
from ..pydantic_ext import BaseModel


class Skeleton(BaseModel):
    name: str
    joints: List[Vector3]
    colors: List[Color]
    links: List[List[int]]
