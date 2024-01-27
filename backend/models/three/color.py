from webcolors import name_to_rgb
from ..pydantic_ext import BaseModel


class Color(BaseModel):
    r: int | float
    g: int | float
    b: int | float

    @staticmethod
    def from_string(color_name: str) -> "Color":
        c = name_to_rgb(color_name)
        return Color(r=c[0], g=c[1], b=c[2])

    @staticmethod
    def from_tuple(color_tuple: tuple[float, float, float]) -> "Color":
        return Color(r=color_tuple[0], g=color_tuple[1], b=color_tuple[2])

    def to_tuple(self) -> tuple[float, float, float]:
        return self.r, self.g, self.b
