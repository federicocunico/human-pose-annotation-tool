import numpy as np
from ..pydantic_ext import BaseModel


class FrameAnnotation(BaseModel):
    frame: int
    visibles: list[bool]

    names_2d: list[str]  #  //  name of joints
    joints_2d: list[list[int]]  # Array<Point>;  // 2D coordinates of joints
    links_2d: list[list[int]]  # Array<Array<number>>;  // links between joints
    confidences_2d: list[float]  # Array<number>;  // confidence for each joint
    format_2d: str  # string;  // format of the annotation (e.g. coco, openpose, etc.)

    names_3d: list[str]  #  //  name of joints
    joints_3d: list[list[float]]  # Array<Point>;  // 3d
    links_3d: list[list[int]]  # Array<Array<number>>;  // links between joints
    format_3d: str  # string;  // format of the annotation (e.g. coco, openpose, etc.)


class Annotations(BaseModel):
    dst: str
    annotations: list[FrameAnnotation]
