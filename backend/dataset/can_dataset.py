import glob
import os
import pickle as pkl
import cv2
import numpy as np
from backend.dataset.definition import AnnotationDataset, FileList
from backend.dataset.dataset_utils import natural_keys
from backend.extra.keypoint_definition import get_2d_kpts_placeholder
from backend.extra.links import OPTITRACK_HUMAN_LINKS
from backend.models.annotation import Annotations, FrameAnnotation
from backend.utility.cv_utils import get_frame_np


def get_annotations_from_file(target: str, max_frames: int) -> Annotations:
    annotations_file = target.replace(".mp4", "_annotation.pkl")
    source_data_file = target.replace(".mp4", ".pkl")
    if not os.path.exists(annotations_file):
        annotations = [
            _get_annotation_from_file(source_data_file, i) for i in range(max_frames)
        ]
        annotations = Annotations(
            dst=annotations_file,
            annotations=annotations,
        )
    else:
        with open(annotations_file, "rb") as fp:
            annotations = Annotations(**pkl.load(fp))
    return annotations


def empty_source_data(source_data_file: str) -> bool:
    if not os.path.isfile(source_data_file):
        return True
    with open(source_data_file, "rb") as fp:
        annotations = pkl.load(fp)
    return len(annotations) == 0


def _get_annotation_from_file(annotations_file: str, frame: int) -> FrameAnnotation:
    if not empty_source_data(annotations_file):
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
        kpts_2d = get_2d_kpts_placeholder(21)
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
        dst="<unknown>",
        visibles=[True] * len(kpts_2d),
        frame=frame,
        names_2d=[str(i) for i in range(len(kpts_2d))],
        confidences_2d=confs.tolist(),
        joints_2d=kpts_2d.tolist(),
        links_2d=OPTITRACK_HUMAN_LINKS,
        format_2d="optitrack",
        ####
        names_3d=[str(i) for i in range(len(kpts_3d))],
        joints_3d=kpts_3d.tolist(),
        links_3d=OPTITRACK_HUMAN_LINKS,
        format_3d="optitrack",
        ####
    )
    return ann


class CanDataset(AnnotationDataset):
    data_root: str  # from AnnotationDataset
    files: list[str]

    def __init__(self, root_folder: str) -> None:
        super().__init__(root_folder)
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
        annotations = get_annotations_from_file(file, max_frames)

        return annotations

    def get_links(self) -> list[list[int]]:
        return OPTITRACK_HUMAN_LINKS

    ## Utils methods

    def get_max_frames(self, file: str) -> int:
        cap = cv2.VideoCapture(file)
        max_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return max_frames
