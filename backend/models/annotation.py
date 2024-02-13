import pickle as pkl
from typing import List

from backend.models.conf import Config
from ..pydantic_ext import BaseModel


class FrameAnnotation(BaseModel):
    frame: int
    num_joints: int
    visibles: List[bool]

    names_2d: List[str]  #  //  name of joints
    joints_2d: List[List[int]]  # Array<Point>;  // 2D coordinates of joints
    links_2d: List[List[int]]  # Array<Array<number>>;  // links between joints
    confidences_2d: List[float]  # Array<number>;  // confidence for each joint
    format_2d: str  # string;  // format of the annotation (e.g. coco, openpose, etc.)

    names_3d: List[str]  #  //  name of joints
    joints_3d: List[List[float]]  # Array<Point>;  // 3d
    links_3d: List[List[int]]  # Array<Array<number>>;  // links between joints
    format_3d: str  # string;  // format of the annotation (e.g. coco, openpose, etc.)

    def get_placeholder(self, config: Config) -> "FrameAnnotation":
        kpts_2d = [[50, 50] for _ in range(config.joints_number)]
        kpts_3d = [[1, 1, 1] for _ in range(config.joints_number)]
        ann = FrameAnnotation(
            num_joints=config.joints_number,
            visibles=[True] * config.joints_number,
            frame=-1,
            names_2d=[str(i) for i in range(config.joints_number)],
            confidences_2d=[1] * config.joints_number,
            joints_2d=kpts_2d,
            links_2d=config.joints_links,
            format_2d="<unknown>",
            ####
            names_3d=[str(i) for i in range(len(kpts_3d))],
            joints_3d=kpts_3d,
            links_3d=config.joints_links,
            format_3d="<unknown>",
            ####
        )
        return ann


class Annotations(BaseModel):
    dst: str
    # placeholder_kpts: List[List[int]] = []
    annotations: List[FrameAnnotation]

    def save(self) -> None:
        with open(self.dst, "wb") as fp:
            pkl.dump(self.model_dump(), fp)
