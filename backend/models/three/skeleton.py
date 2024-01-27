from .color import Color
from .vector3 import Vector3
from ..pydantic_ext import BaseModel


class Skeleton(BaseModel):
    name: str
    joints: list[Vector3]
    colors: list[Color]
    links: list[list[int]]
