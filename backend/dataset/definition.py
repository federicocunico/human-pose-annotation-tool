from abc import ABC, abstractmethod

import numpy as np

from backend.models.annotation import Annotations


class AnnotationDataset(ABC):
    data_root: str

    def __init__(self, data_root: str) -> None:
        self.data_root = data_root

    @abstractmethod
    def get_image(self, file: str, frame_idx: int | None = None) -> np.ndarray:
        pass

    @abstractmethod
    def get_all_annotations(self, file: str) -> Annotations:
        pass

    @abstractmethod
    def get_links(self) -> list[list[int]]:
        pass

    @abstractmethod
    def get_files(self) -> list[str]:
        pass
