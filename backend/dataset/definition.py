from abc import ABC, abstractmethod

import numpy as np

from backend.models.annotation import Annotations
from backend.pydantic_ext import BaseModel


class AnnotationDataset(ABC):
    data_root: str

    def __init__(self, data_root: str) -> None:
        self.data_root = data_root

    @abstractmethod
    def get_image(self, file: str, frame_idx: int | None = None) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def get_all_annotations(self, file: str) -> Annotations:
        raise NotImplementedError

    @abstractmethod
    def get_links(self) -> list[list[int]]:
        raise NotImplementedError

    @abstractmethod
    def get_files(self) -> "FileList":
        raise NotImplementedError

    def get_max_frames(self, file: str) -> int:
        raise NotImplementedError


class FileList(BaseModel):
    files: list[
        str
    ]  # list of files to annotate. at the moment, only videos are supported
    has_annotations: list[
        bool
    ]  # for each file, a boolean indicating if the annotation file exists
    has_source_data: list[
        bool
    ]  # for each file, a boolean indicating if the source data file with 3D information exists


class AnnotationOutput(BaseModel):
    frame: str  # base64 encoded image
    current_frame: int  # current frame index
    max_frames: int  # max number of frames in the video
    annotations: Annotations  # annotations for the current video (all frames)


class ImageOutput(BaseModel):
    frame: str  # base64 encoded image
    current_frame: int  # current frame index
