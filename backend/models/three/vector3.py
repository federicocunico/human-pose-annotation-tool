import numpy as np
from ..pydantic_ext import BaseModel, NdArray


class Vector3(BaseModel):
    x: float
    y: float
    z: float

    @staticmethod
    def from_numpy(array: NdArray) -> "Vector3":
        return Vector3(x=array[0], y=array[1], z=array[2])

    def to_numpy(self) -> NdArray:
        return np.asarray([self.x, self.y, self.z])
