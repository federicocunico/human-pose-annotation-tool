import glob
import os
import pickle as pkl
from typing import List, Optional
import shutil
import numpy as np
from tqdm import tqdm
from matplotlib import pyplot as plt
from backend.dataset import AnnotationDataset, FileList
from backend.dataset.dataset_utils import natural_keys
from backend.extra.keypoint_definition import get_2d_kpts_placeholder
from backend.models.annotation import Annotations, FrameAnnotation
from backend.models.conf import Config
from backend.utility.cv_utils import get_frame_np
from backend.utility.dyn_import import load_module

FILTER_ACTIONS = []


def is_source_data_empty(source_data_file: str) -> bool:
    if not os.path.isfile(source_data_file):
        return True
    with open(source_data_file, "rb") as fp:
        annotations = pkl.load(fp)
    return len(annotations) == 0


def _generate_annotation(config: Config, frame: int) -> FrameAnnotation:
    n_joints = config.joints_number

    kpts_2d = get_2d_kpts_placeholder(n_joints)
    kpts_3d = np.asarray(
        [
            [1.136719, 0.873618, 1.206124],
            [0.834257, 0.882746, 1.220468],
            [1.109332, 0.915527, 1.017916],
            [0.843921, 0.88771, 0.999905],
            [0.901337, 1.211119, 1.230884],
            [0.957567, 1.356336, 0.981261],
            [1.045989, 1.212307, 0.955979],
            [0.904956, 1.22158, 0.963926],
            [0.96775, 1.639268, 1.233489],
            [0.951423, 1.523076, 1.30284],
            [0.871839, 1.575931, 1.205962],
            [1.110771, 1.291938, 0.973919],
            [1.089796, 1.399161, 1.085506],
            [1.175522, 1.009305, 1.018958],
            [1.152928, 1.170807, 1.00415],
            [1.233646, 0.753759, 1.165131],
            [1.231741, 0.810421, 1.142993],
            [1.161459, 0.827705, 1.193418],
            [0.810097, 1.260664, 0.978913],
            [0.844339, 1.389186, 1.086585],
            [0.756994, 1.009421, 0.993313],
            [0.790335, 1.149982, 0.992365],
            [0.722706, 0.734142, 1.08679],
            [0.728727, 0.806222, 1.076808],
            [0.777959, 0.818478, 1.138311],
            [1.085861, 0.498997, 1.221834],
            [1.146155, 0.424791, 1.14429],
            [1.073955, 0.187708, 1.194498],
            [1.100793, 0.139487, 1.125059],
            [1.109628, 0.0675, 1.281107],
            [1.000025, 0.067785, 1.277275],
            [0.856977, 0.462625, 1.200729],
            [0.810359, 0.406668, 1.127705],
            [0.873038, 0.315188, 1.179615],
            [0.851635, 0.140705, 1.126197],
            [0.840716, 0.061956, 1.25429],
            [0.96148, 0.065682, 1.268157],
        ]
    )
    assert len(kpts_2d) == len(
        kpts_3d
    ), f"kpts length wrong {len(kpts_2d)} != {n_joints}"

    ann = FrameAnnotation(
        num_joints=config.joints_number,
        visibles=[False] * len(kpts_2d),
        frame=frame,
        names_2d=[str(i) for i in range(len(kpts_2d))],
        confidences_2d=[1] * len(kpts_2d),
        joints_2d=kpts_2d,
        links_2d=config.joints_links,
        format_2d="optitrack_raw",
        ####
        names_3d=[str(i) for i in range(len(kpts_3d))],
        joints_3d=kpts_3d,
        links_3d=config.joints_links,
        format_3d="optitrack_raw",
        ####
    )
    return ann


SEP = "--"


class OptitrackRawDataset(AnnotationDataset):
    data_root: str  # from AnnotationDataset
    files: List[str]

    def __init__(self, root_folder: str, config: Config) -> None:
        super().__init__(root_folder, config)

        # self.optitrack_module = load_module("", module_name="optitrack_processing")

        all_actions = [
            os.path.join(root_folder, f)
            for f in os.listdir(root_folder)
            if os.path.isdir(os.path.join(root_folder, f))
        ]
        all_subjects_folders = [
            os.path.join(a, f) for a in all_actions for f in os.listdir(a)
        ]
        all_subjects_folders = [f for f in all_subjects_folders if os.path.isdir(f)]
        all_subjects_folders.sort(key=natural_keys)

        ######### Stats
        print("Statistics on dataset")
        print("-" * 100)
        print(f"Found {len(all_actions)} actions in {root_folder}")
        _unique_subjects = set([os.path.basename(s) for s in all_subjects_folders])
        _unique_actions = set([os.path.basename(s) for s in all_actions])
        print(f"Found {len(_unique_subjects)} unique subjects")
        for act in _unique_actions:
            # check that all subjects are present
            _act_subs = [s for s in all_subjects_folders if act in s]
            _act_subs = set([os.path.basename(s) for s in _act_subs])
            if len(_act_subs) != len(_unique_subjects):
                print(f"Action {act} has {len(_act_subs)} subjects")
                print(f"Missing subjects: {_unique_subjects - _act_subs}")

        ####### FILTER BY ACTION
        if len(FILTER_ACTIONS) > 0:
            _all_subjects_folders = []
            for s in all_subjects_folders:
                for f in FILTER_ACTIONS:
                    if f in s:
                        _all_subjects_folders.append(s)
            # make sure folder is unique (should be already unique, but just in case)
            all_subjects_folders = list(set(_all_subjects_folders))
        #######

        print("-" * 100)
        ot_csvs = [(s, glob.glob(s + "/*.csv")) for s in all_subjects_folders]
        csvs: List[str] = []
        for s, ot_csv in ot_csvs:
            if len(ot_csv) <= 0:
                print("No csv files found in ", s)
                continue
            if len(ot_csv) > 1:
                print(
                    f"More than one csv file ({len(ot_csv)}) found in ",
                    s,
                    " using the first one.",
                )
            csvs.append(ot_csv[0])

        print("-" * 100)
        for csv in csvs:
            # check if is not empty
            if os.path.getsize(csv) <= 0:
                print("Empty csv file: ", csv)

        # For each csv, get the spot view names
        files: List[str] = []
        mapping_file_to_csv = {}
        for csv in tqdm(csvs, desc="Collecting data"):
            base_folder = os.path.dirname(csv)
            spot_views_candidate = glob.glob(
                base_folder + "/*_image_capture_converted.pkl"
            )
            if len(spot_views_candidate) <= 0:
                print("No spot view (converted) found for ", csv)
                continue
            if len(spot_views_candidate) > 1:
                # should never happen
                print(
                    f"More than one spot view ({len(spot_views_candidate)}) found for ",
                    csv,
                    ".",
                )
            spot_views_file = spot_views_candidate[0]
            with open(spot_views_file, "rb") as fp:
                spot_views_data = pkl.load(fp)

            views = list(spot_views_data["images"].keys())

            for view in views:
                if "depth" in view:
                    continue

                subject = base_folder.split(os.sep)[-1]
                action = base_folder.split(os.sep)[-2]
                fname = os.path.join(base_folder, f"{action}_{subject}{SEP}{view}")

                _legacy_wrong_fname = csv.replace(".csv", f"{SEP}{view}_annotation.pkl")
                self.__legacy_conv(_legacy_wrong_fname, fname)  # fix legacy name

                files.append(fname)
                mapping_file_to_csv[fname] = (csv, spot_views_file)

            ####
            # break
            ####

        files.sort(key=natural_keys)
        # visualization files for UI (len(csv) * len(views_for_csv))
        self.files: List[str] = files
        self.annotation_files = [f + "_annotation.pkl" for f in files]
        self.mapping_file_to_csv = mapping_file_to_csv  # mapping from visualization file to csv and spot view file

        ## Optional, update annotation dst
        # for f in self.annotation_files:
        #     if os.path.isfile(f):
        #         with open(f, "rb") as fp:
        #             annotations = pkl.load(fp)
        #         ann = Annotations(dst=f, annotations=annotations["annotations"])
        #         ann.save()

        ## TEST
        self.get_annotations_from_file(
            self.files[0], self.get_max_frames_idx(self.files[0])
        )

    def __legacy_conv(self, wrong_fname_file: str, new_fname: str) -> None:
        if os.path.isfile(wrong_fname_file):
            _new_fname = new_fname + "_annotation.pkl"
            # open and save with new name
            with open(wrong_fname_file, "rb") as fp:
                annotations = pkl.load(fp)
            ann = Annotations(dst=_new_fname, annotations=annotations["annotations"])
            ann.save()
            os.remove(wrong_fname_file)

    def _file_to_csv(self, file: str) -> str:
        _, camera_view = file.split(SEP)
        csv_file, spot_view_file = self.mapping_file_to_csv[file]
        return csv_file, spot_view_file, camera_view

    def get_annotations_from_file(self, file: str, max_frames: int) -> Annotations:
        csv_file, spot_view_file, camera_view = self._file_to_csv(file)
        annotations_file = file + "_annotation.pkl"
        if not os.path.exists(annotations_file):
            annotations = [
                _generate_annotation(self.config, i) for i in range(max_frames + 1)
            ]
            annotations = Annotations(
                dst=annotations_file,
                annotations=annotations,
            )
        else:
            with open(annotations_file, "rb") as fp:
                annotations = Annotations(**pkl.load(fp))
        return annotations

    ## Abstract methods implementations

    def get_files(self) -> FileList:
        has_annotation = [os.path.isfile(f) for f in self.annotation_files]
        has_source_data = [True] * len(self.files)
        fl = FileList(
            files=self.files,
            has_annotations=has_annotation,
            has_source_data=has_source_data,
        )
        return fl

    def get_image(self, file: str, frame_idx: Optional[int] = None) -> np.ndarray:
        if frame_idx > self.get_max_frames_idx(file):
            return None
        csv_file, spot_view_file, camera_view = self._file_to_csv(file)
        with open(spot_view_file, "rb") as fp:
            spot_views_data = pkl.load(fp)
        frame = spot_views_data["images"][camera_view][frame_idx]
        # frame, _ = get_frame_np(base_fname, frame_idx)
        return frame

    def get_all_annotations(self, file: str) -> Annotations:
        max_frames_idx = self.get_max_frames_idx(file)
        annotations = self.get_annotations_from_file(file, max_frames_idx)

        return annotations

    def get_links(self) -> List[List[int]]:
        return self.config.joints_links

    ## Utils methods

    def get_max_frames_idx(self, file: str) -> int:
        csv_file, spot_view_file, camera_view = self._file_to_csv(file)
        with open(spot_view_file, "rb") as fp:
            spot_views_data = pkl.load(fp)
        max_frame_idx = len(spot_views_data["images"][camera_view]) - 1
        return max_frame_idx
