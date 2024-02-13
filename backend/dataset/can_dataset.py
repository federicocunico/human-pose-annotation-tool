import glob
import os
import pickle as pkl
from typing import List
import cv2
import numpy as np
from backend.dataset import AnnotationDataset, FileList
from backend.dataset.dataset_utils import natural_keys
from backend.extra.keypoint_definition import get_2d_kpts_placeholder
from backend.models.annotation import Annotations, FrameAnnotation
from backend.models.conf import Config
from backend.utility.cv_utils import get_frame_np


def get_annotations_from_file(
    conf: Config, target: str, max_frames: int
) -> Annotations:
    annotations_file = target.replace(".mp4", "_annotation.pkl")
    source_data_file = target.replace(".mp4", ".pkl")
    if not os.path.exists(annotations_file):
        annotations = [
            _get_annotation_from_file(conf, source_data_file, i)
            for i in range(max_frames)
        ]
        annotations = Annotations(
            dst=annotations_file,
            annotations=annotations,
        )
    else:
        with open(annotations_file, "rb") as fp:
            annotations = Annotations(**pkl.load(fp))
    return annotations


def is_source_data_empty(source_data_file: str) -> bool:
    if not os.path.isfile(source_data_file):
        return True
    with open(source_data_file, "rb") as fp:
        annotations = pkl.load(fp)
    return len(annotations) == 0


def _get_annotation_from_file(
    config: Config, annotations_file: str, frame: int
) -> FrameAnnotation:
    if not is_source_data_empty(annotations_file):
        with open(annotations_file, "rb") as fp:
            annotations = pkl.load(fp)
            annotations = annotations["session"]
        session_dict = annotations[frame]
        kpts_3d = np.asarray(session_dict["skeletons"]["human0"]["positions"])
        n_kpts = len(kpts_3d)
        kpts_2d = get_2d_kpts_placeholder(n_kpts)
        confs = np.zeros(len(kpts_2d), dtype=np.float32) + 1
    else:
        kpts_3d = np.asarray([], dtype=np.float32)  # empty
        kpts_2d = get_2d_kpts_placeholder(config.joints_number)
        confs = np.zeros(len(kpts_2d), dtype=np.float32) + 1

    ### Debug visualization
    if False:
        from matplotlib import pyplot as plt

        plt.figure(figsize=(10, 10))
        ax = plt.subplot(111, projection="3d")
        for i in range(len(annotations)):
            ax.cla()
            kpts_3d = np.asarray(annotations[i]["skeletons"]["human0"]["positions"])
            ax.scatter(kpts_3d[:, 0], kpts_3d[:, 1], kpts_3d[:, 2])
            plt.pause(0.001)
    ###

    ann = FrameAnnotation(
        num_joints=config.joints_number,
        visibles=[True] * len(kpts_2d),
        frame=frame,
        names_2d=[str(i) for i in range(len(kpts_2d))],
        confidences_2d=confs.tolist(),
        joints_2d=kpts_2d.tolist(),
        links_2d=config.joints_links,
        format_2d="optitrack",
        ####
        names_3d=[str(i) for i in range(len(kpts_3d))],
        joints_3d=kpts_3d.tolist(),
        links_3d=config.joints_links,
        format_3d="optitrack",
        ####
    )
    return ann


class CanDataset(AnnotationDataset):
    data_root: str  # from AnnotationDataset
    files: List[str]

    def __init__(self, root_folder: str, config: Config) -> None:
        super().__init__(root_folder, config)
        self.files = glob.glob(os.path.join(root_folder, "*.mp4"))
        self.files.sort(key=natural_keys)

    ## Abstract methods implementations

    def get_files(self) -> FileList:
        has_annotations = [f.replace(".mp4", "_annotation.pkl") for f in self.files]
        has_annotations = [os.path.isfile(f) for f in has_annotations]

        has_source_data = [f.replace(".mp4", ".pkl") for f in self.files]
        has_source_data = [os.path.isfile(f) for f in has_source_data]
        fl = FileList(
            files=self.files,
            has_annotations=has_annotations,
            has_source_data=has_source_data,
        )
        return fl

    def get_image(self, file: str, frame_idx: int | None = None) -> np.ndarray:
        frame, _ = get_frame_np(file, frame_idx)
        return frame

    def get_all_annotations(self, file: str) -> Annotations:
        max_frames = self.get_max_frames(file)
        annotations = get_annotations_from_file(self.config, file, max_frames)

        return annotations

    def get_links(self) -> List[List[int]]:
        return self.config.joints_links

    ## Utils methods

    def get_max_frames(self, file: str) -> int:
        cap = cv2.VideoCapture(file)
        max_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
        cap.release()
        return max_frames
