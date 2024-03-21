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

# leave empty to load all actions. Otherwise, specify the actions to load (e.g. ["act1_90", "act1_0", "act1_180"])
ACTIONS = []


def aligned_to_annotation(aligned):
    # 'data/harper/test/annotations/toa_act3_left_fisheye_image_aligned.pkl'
    fname = os.path.basename(aligned)
    subj = fname.split("_")[0]
    act = (
        fname.split("_")[1] if "act1_" not in fname else "_".join(fname.split("_")[1:3])
    )
    cam_name = aligned.split(act + "_")[-1].split("_aligned")[0]

    annotation_name = f"{act}_{subj}--{cam_name}_annotation.pkl"
    folder = os.path.dirname(aligned)
    folder = os.path.abspath(os.path.join(folder, "..", "tool"))
    return os.path.join(folder, annotation_name)


def _load_pkl(file: str):
    with open(file, "rb") as f:
        data = pkl.load(f)
    return data

def sort_dict_by_key(dictionary):
    """
    Function to sort a dictionary based on keys in a human-like natural order.
    """
    sorted_keys = sorted(dictionary.keys(), key=natural_keys)
    sorted_dict = {key: dictionary[key] for key in sorted_keys}
    return sorted_dict

class HARPERDataset(AnnotationDataset):
    data_root: str  # from AnnotationDataset
    files: List[str]

    def __init__(self, root_folder: str, config: Config) -> None:
        super().__init__(root_folder, config)

        files = {}
        annotations = {}
        max_frames = {}
        all_pkls = glob.glob(
            os.path.join(root_folder, "**", "*aligned.pkl"), recursive=True
        )
        for pkl_file in all_pkls:
            if len(ACTIONS) > 0:
                if not any([a in pkl_file for a in ACTIONS]):
                    continue
            annotation_file = aligned_to_annotation(pkl_file)
            assert os.path.isfile(
                annotation_file
            ), f"Annotation file {annotation_file} does not exist! Unable to load dataset"
            v = _load_pkl(pkl_file)

            files[annotation_file] = pkl_file
            max_frames[annotation_file] = len(v) - 1
            annotations[annotation_file] = Annotations(**_load_pkl(annotation_file))

        # sort files by keys
        files = {key:files[key] for key in sorted(files.keys(), key=natural_keys)}
        self.files: dict[str, str] = files
        self.max_frames: dict[str, int] = max_frames
        self.annotations: dict[str, Annotations] = annotations

    ## Abstract methods implementations

    def get_files(self) -> FileList:
        files = list(self.files.keys())
        has_annotations = [True for _ in files]
        has_source_data = [True for _ in files]
        fl = FileList(
            files=files,
            has_annotations=has_annotations,
            has_source_data=has_source_data,
        )
        return fl

    def get_image(self, file: str, frame_idx: int | None = None) -> np.ndarray:
        if frame_idx is None:
            frame_idx = 0
        pkl_with_images = self.files[file]
        data = _load_pkl(pkl_with_images)[frame_idx]
        assert data["frame"] == int(
            frame_idx
        ), f"Frame index mismatch {data['frame']} != {frame_idx}"
        image_path = data["spot_pov_image"]
        assert os.path.isfile(image_path), f"Image file {image_path} does not exist"
        frame, _ = get_frame_np(image_path, frame_idx)
        return frame

    def get_all_annotations(self, file: str) -> Annotations:
        return self.annotations[file]

    def get_links(self) -> List[List[int]]:
        return self.config.joints_links

    get_max_frames_idx = lambda self, file: self.max_frames[file]


def __test__():
    from backend.cfg import get_config

    d = HARPERDataset("data/harper", get_config("backend/configs/harper.yaml"))
    fl = d.get_files()
    d.get_all_annotations(fl.files[0])
    d.get_image(fl.files[0], 30)
    d.get_links()
    for f in fl.files:
        ann: Annotations = d.get_all_annotations(f)
        for j, frame_ann in enumerate(ann.annotations):
            if np.sum(frame_ann.visibles) > 5:
                d.get_debug_plot(f, j)
                return


if __name__ == "__main__":
    __test__()
