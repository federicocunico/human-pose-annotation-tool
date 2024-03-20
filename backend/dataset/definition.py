from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import cv2
from matplotlib import pyplot as plt

import numpy as np

from backend.models.annotation import Annotations
from backend.models.conf import Config
from backend.pydantic_ext import BaseModel


class AnnotationDataset(ABC):
    data_root: str
    config: Config

    def __init__(self, data_root, config: Config = None) -> None:
        self.data_root = data_root
        self.config = config

    @abstractmethod
    def get_image(self, file: str, frame_idx: int | None = None) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def get_all_annotations(self, file: str) -> Annotations:
        raise NotImplementedError

    @abstractmethod
    def get_links(self) -> List[List[int]]:
        raise NotImplementedError

    @abstractmethod
    def get_files(self) -> "FileList":
        raise NotImplementedError

    @abstractmethod
    def get_max_frames_idx(self, file: str) -> int:
        raise NotImplementedError

    def get_debug_plot(self, file: str, frame_idx: int, wait_time: float = 60.0) -> np.ndarray:
        frame = self.get_image(file, frame_idx)
        annotations = self.get_all_annotations(file)
        kpts_2d = None
        kpts_visibles = None

        for ann in annotations.annotations:
            if ann.frame == frame_idx:
                kpts_2d = ann.joints_2d
                # kpts_3d = ann.joints_3d
                kpts_visibles = ann.visibles
                break

        for i, (x, y) in enumerate(kpts_2d):
            if kpts_visibles[i]:
                frame = cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)

        matplot_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        fig = plt.figure()
        plt.imshow(matplot_img)
        if wait_time > 0:
            plt.show(block=False)
            plt.pause(wait_time)
        else:
            plt.show()
        plt.close(fig)


class FileList(BaseModel):
    files: List[
        str
    ]  # list of files to annotate. at the moment, only videos are supported
    has_annotations: List[
        bool
    ]  # for each file, a boolean indicating if the annotation file exists
    has_source_data: List[
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
